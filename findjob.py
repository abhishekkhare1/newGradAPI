
import requests
import json
import os
import base64
from twilio.rest import Client


COMMIT_URL = "https://api.github.com/repos/Pitt-CSC/NewGrad-2021/commits/master"
README_URL = "https://api.github.com/repos/Pitt-CSC/NewGrad-2021/readme"

#GET /repos/:owner/:repo/git/blobs/:file_sha
def getNewDate():
    response = requests.get(url = COMMIT_URL).json()
    return str(response["commit"]["author"]["date"])

def parseReadMe():
    response = requests.get(url = README_URL).json()
    readme = str(base64.b64decode(response['content']))
    
    #Parse readme to get last company in table
    body,_,_ = readme.rpartition('\\n')
    _,_,end = body.rpartition('\\n')

    #Get the company name and link to application
    company,_,linkEnd = end.lstrip('| [').partition(']')
    link,_,_ = linkEnd.lstrip('(').partition(')')
    
    return company, link

def getOldDate():
    f = open("date", "r")
    oldDate = f.read()
    f.close()
    return oldDate

def writeOldDate(newDate):
    f = open("date", "w")
    f.write(newDate)
    f.close()

def sendText(message):
    
    if len(message) >= 160:
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

def main():
    newDate = getNewDate()
    oldDate = getOldDate()
    
    if newDate > oldDate:
        writeOldDate(newDate)
        company, link = parseReadMe()
        message = company + ' added a New Grad role\n' + link
        sendText(message)
        print(message)


main()

