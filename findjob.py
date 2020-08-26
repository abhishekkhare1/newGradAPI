
import requests
import json
import os
from twilio.rest import Client


URL = "https://api.github.com/repos/Pitt-CSC/NewGrad-2021/commits/master"

def getNewDate():
    response = requests.get(url = URL).json()
    return str(response["commit"]["author"]["date"])

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
        sendText("updated")
        print("updated")


main()

