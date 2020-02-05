import requests
from config import API_KEY
url = "https://api-football-beta.p.rapidapi.com/seasons"

headers = {
    'x-rapidapi-host': "api-football-beta.p.rapidapi.com",
    'x-rapidapi-key': API_KEY
    }

response = requests.request("GET", url, headers=headers)

print(response.text)