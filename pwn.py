import requests
import os
from dotenv import load_dotenv


scriptLink = 'https://raw.githubusercontent.com/LivvidDreams/pwnProject/master/'
mainUser = 'LivvidDreams'
files = ['pwn.py', '.env']


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
    else:
        exit()


def main():
    getScript()
    print("new Version")



if __name__ == "__main__":
    main()