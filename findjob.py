
import requests
import json

URL = "https://api.github.com/repos/Pitt-CSC/NewGrad-2021/commits/master"

r = requests.get(url = URL).json()
with open('response.json', 'w') as outfile:
    json.dump(r, outfile)
print(r["commit"]["author"]["date"])