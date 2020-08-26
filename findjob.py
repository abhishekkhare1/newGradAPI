
import requests
import json

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

def main():
    newDate = getNewDate()
    oldDate = getOldDate()
    
    if newDate > oldDate:
        writeOldDate(newDate)
        print("updated")


main()

