import os
import json
import requests
import base64
import subprocess
import datetime

from dotenv import load_dotenv


'''
TOTALLY NOT OUR METHOD. 
Adapted to run on Python3 vs Python2

Credit to Github User @avullo
https://gist.github.com/avullo/b8153522f015a8b908072833b95c3408

Used To Push Our Keys To Github since you don't have access TA. sorry :(

Technically you do with the api_key... but thats a whole other thing
'''
def push_to_repo_branch(gitHubFileName, fileName, repo_slug, branch, validAuth):
    '''
    Push file update to GitHub repo
    
    :param gitHubFileName: the name of the file in the repo
    :param fileName: the name of the file on the local branch
    :param repo_slug: the github repo slug, i.e. username/repo
    :param branch: the name of the branch to push the file to
    :param user: github username
    :param token: github user token
    :return None
    :raises Exception: if file with the specified name cannot be found in the repo
    '''
    
    message = "Automated update " + str(datetime.datetime.now())
    path = "https://api.github.com/repos/%s/branches/%s" % (repo_slug, branch)

    r = requests.get(path, auth=validAuth)
    if not r.ok:
        print("Error when retrieving branch info from %s" % path)
        print("Reason: %s [%d]" % (r.text, r.status_code))
        raise
    rjson = r.json()
    treeurl = rjson['commit']['commit']['tree']['url']
    r2 = requests.get(treeurl, auth=validAuth)
    if not r2.ok:
        print("Error when retrieving commit tree from %s" % treeurl)
        print("Reason: %s [%d]" % (r2.text, r2.status_code))
        raise
    r2json = r2.json()
    sha = None

    for file in r2json['tree']:
        # Found file, get the sha code
        if file['path'] == gitHubFileName:
            sha = file['sha']

    # if sha is None after the for loop, we did not find the file name!
    if sha is None:
        print ("Could not find " + gitHubFileName + " in repos 'tree' ")
        raise Exception

    with open(fileName, 'rb') as data:
        content = base64.b64encode(data.read())

    # gathered all the data, now let's push
    inputdata = {}
    inputdata["path"] = gitHubFileName
    inputdata["branch"] = branch
    inputdata["message"] = message
    inputdata["content"] = content.decode()
    if sha:
        inputdata["sha"] = str(sha)

    updateURL = "https://api.github.com/repos/LivvidDreams/pwnProject/contents/" + gitHubFileName
    try:
        rPut = requests.put(updateURL, auth=validAuth, data = json.dumps(inputdata))
        if not rPut.ok:
            print("Error when pushing to %s" % updateURL)
            print("Reason: %s [%d]" % (rPut.text, rPut.status_code))
            raise Exception
    except requests.exceptions.RequestException as e:
        print ('Something went wrong! I will print all the information that is available so you can figure out what happend!')
        print (rPut)
        print (rPut.headers)
        print (rPut.text)
        print (e)

def runCommand(command, output=False):
    if not command: return
    if not output:
        subprocess.call(command.split(), stdout = subprocess.PIPE)
    else:
        subprocess.call(command.split())

def configureTokens():
    api_key = None

    try:
        with open(".env", "r") as envFile:
            envFile.close()
    except:
        # Prompt user for link
        # store the link 
        # put link in command    
        # https://transfer.sh/4dsUEB/.env
        usrInput = input("Enter link for environment variable: ")
        runCommand("curl -s -o .env {}".format(usrInput))


    # Ensure we can download enviornment file
    load_dotenv()
    api_key = os.getenv("github_key")

    assert api_key

    return api_key



def main():
    # STEP 1: MAKES RSA KEY 

    # TA NOTE: Change the directory of .ssh location if necessary 
    # (only need to change @homeDir)
    defaultDir = "/home/kali/.ssh/"
    homeDir = ""

    print("~~~~~ Making SSH Key-Pair ~~~~~")
    while homeDir == "":
        getDir = input("\tSpecify absolute .ssh directory. [Press Enter for default of '/home/kali/.ssh/]: ")
        if getDir == "":
            homeDir = defaultDir
        elif len(getDir) > 5 and getDir[-5:] == ".ssh/":
            homeDir = getDir
            break

    
    runCommand("ssh-keygen -t rsa -f {}rsakeys -N kali".format(homeDir))
    runCommand("mv {}rsakeys.pub {}.rsakeys.pub".format(homeDir, homeDir))


    # STEP 2: Upload Keypair to github
    user = "LivvidDreams"
    githubFileName = ".rsakeys.pub"
    fileName = "{}.rsakeys.pub".format(homeDir)
    repo_slug = "LivvidDreams/pwnProject"
    branch = "main"

    print("\n\n~~~~~ Uploading Key-Pair To Github ~~~~~")

    # WIll Prompt You For Link To Token if not already in current directory.
    # Will provide you with link (but can expire. so will also provide the file)
    token = configureTokens()
    validAuth = (user, token)

    push_to_repo_branch(githubFileName, fileName, repo_slug, branch, validAuth)

    print("~~~~~ Time to run Script On Target Machine ~~~~~\n")
    print("Note: SSH Key-Pair Password is 'kali'")
    print("Note: Can now SCP pwn.py to target machine")

if __name__ == '__main__':
    main()