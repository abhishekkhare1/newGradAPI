
import requests
import json
import os
import base64
from twilio.rest import Client


COMMIT_URL = "https://api.github.com/repos/Pitt-CSC/NewGrad-2021/commits/master"
README_URL = "https://api.github.com/repos/Pitt-CSC/NewGrad-2021/readme"
REPO_URL = "https://github.com/Pitt-CSC/NewGrad-2021"


#Gets date of most recent commit from the repo
def getNewDate():
    response = requests.get(url = COMMIT_URL).json()
    return str(response["commit"]["author"]["date"])


#Makes a request to the repo readme
#Parses repo to get list of recent company names and links
def parseReadMe():

    companyList = list()
    linkList = list()

    #Request README and decode to plaintext
    response = requests.get(url = README_URL).json()
    readme = str(base64.b64decode(response['content']))
    
    #Cut out closing newLines
    body,_,_ = readme.rpartition('\\n\\n')

    lastCompany = getLastCompany()
    body,_,end = body.rpartition('\\n')
    #Get the company name and link to application
    company,_,linkEnd = end.lstrip('| [').partition(']')
    link,_,_ = linkEnd.lstrip('(').partition(')')

    while company != lastCompany:
        companyList.append(company)
        linkList.append(link)
        body,_,end = body.rpartition('\\n')
        #Get the company name and link to application
        company,_,linkEnd = end.lstrip('| [').partition(']')
        link,_,_ = linkEnd.lstrip('(').partition(')')
    
    if len(companyList) > 0:
        setLastCompany(companyList[0])

    return companyList, linkList


#Reads content from file
def readFile(fileName):
    f = open(fileName, "r")
    content = f.read()
    f.close()
    return content


#Writes content to file
def writeFile(fileName, content):
    f = open(fileName, "w")
    f.write(content)
    f.close()


#Gets last commit date
def getOldDate():
    return readFile('date')

#Writes the new date to file
def setOldDate(newDate):
    writeFile('date', newDate)


#Gets last company
def getLastCompany():
    return readFile('lastCompany')

#Writes the most recent company to lastCompany
def setLastCompany(company):
    writeFile('lastCompany', company)


#Texts my number with a message using the Twilio API
def sendText(message):
    
    if len(message) >= 480:
        print('error: message length too long')
        return

    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    message = client.messages \
                .create(
                     body=message,
                     from_=os.environ['MY_TWILIO_NUMBER'],
                     to=os.environ['MY_PHONE_NUMBER']                   
                 )


#main
def main():
    newDate = getNewDate()
    oldDate = getOldDate()
    
    if newDate > oldDate:
        setOldDate(newDate)
        companyList, linkList = parseReadMe()
        length = len(companyList)

        #Avoid excessive Twilio charges in case of mass activity or error
        if length > 5:
            massActivity = str(length) + ' New Grad Jobs Posted!\n'
            sendText(massActivity + REPO_URL)
            return
        
        #Send out texts for each company with link
        for i in range(length):
            company = companyList[i]
            link = linkList[i]
            message = company + ' added a New Grad role\n' + link
            sendText(message)
    else:
        print('no updates')


main()