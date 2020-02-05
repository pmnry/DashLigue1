import requests

url = "https://api-football-beta.p.rapidapi.com/seasons"

headers = {
    'x-rapidapi-host': "api-football-beta.p.rapidapi.com",
    'x-rapidapi-key': "1101ec060fmshee8fc50f408d2b2p17f205jsn5b6b9f3764dc"
    }

response = requests.request("GET", url, headers=headers)

print(response.text)