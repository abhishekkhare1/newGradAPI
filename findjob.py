
import requests
import json
import os
import base64
import logging

import polling2
from twilio.rest import Client

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

COMMIT_URL = "https://api.github.com/repos/Pitt-CSC/NewGrad-2021/commits/master"
README_URL = "https://api.github.com/repos/Pitt-CSC/NewGrad-2021/readme"
REPO_URL = "https://github.com/Pitt-CSC/NewGrad-2021"

#Gets date of most recent commit from the repo
def get_new_date():
    response = requests.get(url = COMMIT_URL).json()
    return str(response["commit"]["author"]["date"])


#Makes a request to the repo readme
#Parses repo to get list of recent company names and links
def parse_read_me():

    companyList = list()
    linkList = list()

    #Request README and decode to plaintext
    response = requests.get(url = README_URL).json()
    readme = str(base64.b64decode(response['content']))
    #Cut out closing newLines
    body,_,_ = readme.rpartition('\\n')

    lastCompany = get_last_company()
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
        set_last_company(companyList[0])

    return companyList, linkList


#Reads content from file
def read_file(fileName):
    f = open(fileName, "r")
    content = f.read()
    f.close()
    return content


#Writes content to file
def write_file(fileName, content):
    f = open(fileName, "w")
    f.write(content)
    f.close()


#Gets last commit date
def get_old_date():
    return read_file('date')

#Writes the new date to file
def set_old_date(newDate):
    write_file('date', newDate)


#Gets last company
def get_last_company():
    return read_file('lastCompany')

#Writes the most recent company to lastCompany
def set_last_company(company):
    write_file('lastCompany', company)


#Texts my number with a message using the Twilio API
def send_text(message):
    
    if len(message) >= 480:
        logger.ERROR('message length too long: ' + str(len(message)))
        return

    logger.info('sending text!')
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    message = client.messages \
                .create(
                     body=message,
                     from_=os.environ['MY_TWILIO_NUMBER'],
                     to=os.environ['MY_PHONE_NUMBER']                   
                 )


def process_commit():
    logger.info('new commit')
    companyList, linkList = parse_read_me()
    length = len(companyList)

    #Avoid excessive Twilio charges in case of mass activity or error
    if length > 5:
        massActivity = str(length) + ' New Grad Jobs Posted!\n'
        send_text(massActivity + REPO_URL)
        return
    
    #Send out texts for each company with link
    for i in range(length):
        company = companyList[i]
        link = linkList[i]
        message = company + ' added a New Grad role\n' + link
        send_text(message)


#Checks if the most recent commit is newer than the stored one
def is_new_commit(newDate):
    oldDate = get_old_date()
    if newDate <= oldDate:
        logger.info('no updates')
    
    else:
        set_old_date(newDate)
        process_commit()

    return False


#main
def main():
    polling2.poll(
    lambda: str(requests.get(url = COMMIT_URL).json()["commit"]["author"]["date"]),
    check_success=is_new_commit,
    step=60,
    poll_forever=True)


main()