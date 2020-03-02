import requests
from api_config import API_KEY
import json
import pandas as pd
from app import db
from models import League

URL = "https://api-football-v1.p.rapidapi.com/v2/leagues"
URL_LEAGUES = "https://api-football-v1.p.rapidapi.com/v2/leagues"
ALL_FIXTURES_URL = "https://api-football-v1.p.rapidapi.com/v2/fixtures/league/"
FIXTURES_STATS_URL = "https://api-football-v1.p.rapidapi.com/v2/statistics/fixture/"

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

    return json.loads(api_response.content)['api']

def get_fixtures_stats(fixture_id):
    try:
        api_response = requests.request("GET", FIXTURES_STATS_URL + str(fixture_id), headers=headers)
    except:
        print('Error calling API')

    if api_response.status_code == 200:
        return json.loads(api_response.content)['api']

def consolidate_season_data(league_name, season_year):
    with open('data\\' + league_name.lower().replace(' ', '_') + '_fixtures_' + str(season_year) + '.txt') as json_file:
        fixtures_dicts = json.load(json_file)

    df = pd.DataFrame(fixtures_dicts['api']['fixtures'])
    df['away_team_id'] = df['awayTeam'].apply(lambda x: x['team_id'])
    df['away_team'] = df['awayTeam'].apply(lambda x: x['team_name'])

    df['home_team_id'] = df['homeTeam'].apply(lambda x: x['team_id'])
    df['home_team'] = df['homeTeam'].apply(lambda x: x['team_name'])

    df['halftime'] = df['score'].apply(lambda x: x['halftime'])
    df['fulltime'] = df['score'].apply(lambda x: x['fulltime'])

    df['game_date'] = pd.to_datetime(df['event_date'], format='%Y-%m-%d %H:%M:%S.%f')
    df['event_date'] = pd.to_datetime(df['event_date'], format='%Y-%m-%d %H:%M:%S.%f')
    df['league_day'] = df['round'].apply(lambda x: int(x.replace('Regular Season - ', '')))

    df.rename(columns={'goalsHomeTeam': 'home_goals', 'goalsAwayTeam': 'away_goals',
                       'statusShort': 'status_short', 'firstHalfStart': 'first_half_start',
                       'secondHalfStart': 'second_half_start'}, inplace=True)
    df = df.drop(['awayTeam', 'homeTeam', 'score', 'referee', 'league', 'elapsed'], axis=1)

    return df

def get_team_results(team_name, season):
    df = consolidate_season_data('ligue_1', season)

    mask = (df['HomeTeam'] == team_name) + (df['AwayTeam'] == team_name)
    away_mask = (df['AwayTeam'] == team_name)
    home_mask = (df['HomeTeam'] == team_name)
    res_df = df[mask]
    res_df['Opponent'] = 0
    res_df['GoalsScored'] = 0
    res_df['GoalsTaken'] = 0

    res_df['Opponent'].loc[away_mask] = res_df['HomeTeam'].loc[away_mask]
    res_df['Opponent'].loc[home_mask] = res_df['AwayTeam'].loc[home_mask]

    res_df['GoalsScored'].loc[away_mask] = res_df['AwayGoals'].loc[away_mask]
    res_df['GoalsScored'].loc[home_mask] = res_df['HomeGoals'].loc[home_mask]

    res_df['GoalsTaken'].loc[away_mask] = res_df['HomeGoals'].loc[away_mask]
    res_df['GoalsTaken'].loc[home_mask] = res_df['AwayGoals'].loc[home_mask]

    res_df['Result'] = 0
    res_df['Result'].loc[res_df['GoalsScored'] > res_df['GoalsTaken']] = 'Win'
    res_df['Result'].loc[res_df['GoalsScored'] == res_df['GoalsTaken']] = 'Tie'
    res_df['Result'].loc[res_df['GoalsScored'] < res_df['GoalsTaken']] = 'Loss'

    res_df = res_df.set_index('LeagueDay', drop=False).sort_index()

    res_df['Points'] = 0
    res_df['Points'].loc[res_df['Result'] == 'Win'] = 3
    res_df['Points'].loc[res_df['Result'] == 'Tie'] = 1
    res_df['Points'].loc[res_df['Result'] == 'Loss'] = 0
    res_df['CumPoints'] = res_df['Points'].cumsum()

    res_df.drop(['AwayTeam', 'HomeTeam', 'AwayGoals', 'HomeGoals'], axis=1, inplace=True)

    return res_df

def set_db_league(league_name,year):
    df = consolidate_season_data(league_name, year)

    for idx, row in df.iterrows():
        row_league = League(**row.to_dict())
        db.session.add(row_league)

    db.session.commit()

set_db_league('Ligue 1', 2010)