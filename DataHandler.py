import requests
from config import API_KEY, COUNT_API_CALLS
import json
import pandas as pd

URL = "https://api-football-v1.p.rapidapi.com/v2/leagues"
URL_LEAGUES = "https://api-football-v1.p.rapidapi.com/v2/leagues"
ALL_FIXTURES_URL = "https://api-football-v1.p.rapidapi.com/v2/fixtures/league/"

headers = {
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
    'x-rapidapi-key': API_KEY
}


def get_league_ids(league_name, country, url, seasons=None):
    api_response = requests.request("GET", url, headers=headers)
    league_dicts = json.loads(api_response.content)['api']['leagues']
    league_ids = dict()

    if seasons is None:
        seasons = list(range(2010, 2020))

    for league_dict in league_dicts:
        if league_dict['name'] == league_name and league_dict['country'] == country:
            if league_dict['season'] in seasons:
                league_ids[str(league_dict['season'])] = league_dict['league_id']

    return league_ids, api_response


def get_league_fixtures(league_name, country, seasons=None):
    league_ids, response = get_league_ids(league_name, country, URL_LEAGUES, seasons)

    with open('data\\' + league_name.lower().replace(' ', '_') + '_ids.txt', 'w') as outfile:
        json.dump(json.loads(response.content), outfile)

    for season, id in league_ids.items():
        api_response = requests.request("GET", ALL_FIXTURES_URL + str(id), headers=headers)

        if api_response.status_code == 200:
            with open('data\\' + league_name.lower().replace(' ', '_') + '_fixtures_' + season + '.txt', 'w') as outfile:
                json.dump(json.loads(api_response.content), outfile)


def consolidate_season_data(league_name, season_year):
    with open('data\\' + league_name.lower().replace(' ', '_') + '_fixtures_' + str(season_year) + '.txt') as json_file:
        fixtures_dicts = json.load(json_file)

    df = pd.DataFrame(fixtures_dicts['api']['fixtures'])
    df['awayTeamID'] = df['awayTeam'].apply(lambda x: x['team_id'])
    df['AwayTeam'] = df['awayTeam'].apply(lambda x: x['team_name'])

    df['homeTeamID'] = df['homeTeam'].apply(lambda x: x['team_id'])
    df['HomeTeam'] = df['homeTeam'].apply(lambda x: x['team_name'])

    df['halftime'] = df['score'].apply(lambda x: x['halftime'])
    df['fulltime'] = df['score'].apply(lambda x: x['fulltime'])

    df['GameDate'] = pd.to_datetime(df['event_date'], format='%Y-%m-%d %H:%M:%S.%f')
    df['LeagueDay'] = df['round'].apply(lambda x: int(x.replace('Regular Season - ', '')))

    df.rename(columns={'goalsHomeTeam': 'HomeGoals', 'goalsAwayTeam': 'AwayGoals'}, inplace=True)
    df = df.drop(['awayTeam', 'homeTeam', 'score', 'referee', 'league'], axis=1)

    return df

#get_league_fixtures('Ligue 1', 'France')