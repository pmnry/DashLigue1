import requests
from config import API_KEY
import json

url = "https://api-football-v1.p.rapidapi.com/v2/fixtures/team/85"

headers = {
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
    'x-rapidapi-key': API_KEY
    }

response = requests.request("GET", url, headers=headers)

print(response.text)