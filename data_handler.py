import requests
from api_config import API_KEY
import json
import pandas as pd
from app import db
from models import League, Fixture
import datetime as dt
from sqlalchemy import or_, and_

BASE_URL = "https://api-football-v1.p.rapidapi.com/v2/"
URL = "https://api-football-v1.p.rapidapi.com/v2/leagues"
URL_LEAGUES = "https://api-football-v1.p.rapidapi.com/v2/leagues"
ALL_FIXTURES_URL = "https://api-football-v1.p.rapidapi.com/v2/fixtures/league/"
FIXTURES_STATS_URL = "https://api-football-v1.p.rapidapi.com/v2/statistics/fixture/"

HEADERS = {
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
    'x-rapidapi-key': API_KEY
}

LEAGUE_COUNTRY = {'Ligue 1': 'France', 'Premier League': 'England'}

def get_api_results(url, arg=""):
    api_response = requests.request("GET", url + arg, headers=HEADERS)
    return json.loads(api_response.content)['api'], api_response

def get_league_ids(league_name, api_call=False, country=None, seasons=None):
    league_ids = dict()
    if api_call:
        league_dicts, api_response = get_api_results(URL_LEAGUES)
        league_dicts = league_dicts['leagues']
    else:
        api_response=None
        with open('data\\' + league_name.lower().replace(' ', '_') + '_ids.txt') as json_file:
            league_dicts = json.load(json_file)['api']['leagues']

    if seasons is None:
        seasons = list(range(2010, 2020))

    for league_dict in league_dicts:
        if league_dict['name'] == league_name and league_dict['country'] == country:
            if league_dict['season'] == seasons:
                league_ids[str(league_dict['season'])] = league_dict['league_id']

    return league_ids, api_response


def get_league_fixtures(league_name, country, seasons=None):
    try:
        # get league ids from json
        league_ids, response = get_league_ids(league_name, seasons=seasons)
    except:
        # get league ids from api call
        league_ids, response = get_league_ids(league_name, True, country, seasons)

    for season, id in league_ids.items():
        api_response = requests.request("GET", ALL_FIXTURES_URL + str(id), headers=HEADERS)

        if api_response.status_code == 200:
            with open('data\\' + league_name.lower().replace(' ', '_') + '_fixtures_' + season + '.txt', 'w') as outfile:
                json.dump(json.loads(api_response.content), outfile)

    return json.loads(api_response.content)['api']

def format_fixture_stats(res_dict, fixture_id):
    formated_dict = dict(fixture_id=fixture_id)
    leagueID = db.session.query(League).filter_by(fixture_id=int(fixture_id)).first().league_id
    formated_dict['league_id'] = leagueID

    for key, item in res_dict.items():

            key = 'Passes Perc' if key == 'Passes %' else key

            for sub_key, sub_item in item.items():
                sub_item = '0' if sub_item is None else sub_item

                if '%' in sub_item:
                    sub_item = int(sub_item.replace('%', ''))/100
                else:
                    sub_item = int(sub_item.replace('%', ''))

                formated_dict[key.lower().replace(' ', '_') + '_' + sub_key] = sub_item

    return formated_dict

def get_fixtures_stats(fixture_id):
    query = db.session.query(Fixture).filter_by(fixture_id=fixture_id).statement
    if pd.read_sql_query(query, db.session.bind).shape[0] > 0:
        df = pd.read_sql_query(query, db.session.bind)
    else:
        api_response = requests.request("GET", FIXTURES_STATS_URL + str(fixture_id), headers=HEADERS)
        res_dict = json.loads(api_response.content)['api']['statistics']
        res_dict = format_fixture_stats(res_dict, fixture_id)
        if db.session.query(Fixture).filter_by(fixture_id=fixture_id).count() < 1:
            try:
                row_fixture = Fixture(**res_dict)
                db.session.add(row_fixture)
                db.session.commit()
                db.session.flush()
            except Exception as e:
                db.session.rollback()

        query = db.session.query(Fixture).filter_by(fixture_id=fixture_id).statement
        df = pd.read_sql_query(query, db.session.bind)

    query2 = db.session.query(League).filter_by(fixture_id=fixture_id).statement
    df2 = pd.read_sql_query(query2, db.session.bind)

    df['home_goals'] = df2['home_goals']
    df['away_goals'] = df2['away_goals']

    return df

def consolidate_season_data(league_name, season_year):

    league_id = get_league_ids(league_name, api_call=True, country=LEAGUE_COUNTRY[league_name], seasons=season_year)

    league_dicts, api_response = get_api_results(ALL_FIXTURES_URL, str(league_id[0][str(season_year)]))

    df = pd.DataFrame(league_dicts['fixtures'])
    # df = pd.read_sql_query(query, db.session.bind)
    df['away_team_id'] = df['awayTeam'].apply(lambda x: x['team_id'])
    df['away_team'] = df['awayTeam'].apply(lambda x: x['team_name'])

    df['home_team_id'] = df['homeTeam'].apply(lambda x: x['team_id'])
    df['home_team'] = df['homeTeam'].apply(lambda x: x['team_name'])

    df['halftime'] = df['score'].apply(lambda x: x['halftime'])
    df['fulltime'] = df['score'].apply(lambda x: x['fulltime'])

    df['game_date'] = pd.to_datetime(df['event_date'], format='%Y-%m-%d %H:%M:%S.%f')
    df['event_date'] = pd.to_datetime(df['event_date'], format='%Y-%m-%d %H:%M:%S.%f')

    df = df[df['round'] != 'Relegation Play Off - First Leg']
    df = df[df['round'] != 'Relegation Play Off - Second Leg']
    df = df[df['round'] != 'Finals']
    df['league_day'] = df['round'].apply(lambda x: int(x.replace('Regular Season - ', '')))

    df.rename(columns={'goalsHomeTeam': 'home_goals', 'goalsAwayTeam': 'away_goals',
                       'statusShort': 'status_short', 'firstHalfStart': 'first_half_start',
                       'secondHalfStart': 'second_half_start'}, inplace=True)
    df = df.drop(['awayTeam', 'homeTeam', 'score', 'referee', 'league', 'elapsed'], axis=1)



    return df

def get_team_results(country, league_name, team_name, season):
    ids = get_league_ids(league_name, api_call=True, country=country, seasons=season)
    query = db.session.query(League).filter(and_(League.league_id == ids[0][str(season)], or_((League.away_team == team_name), (League.home_team == team_name)))).statement
    df = pd.read_sql_query(query, db.session.bind)

    mask = (df['home_team'] == team_name) + (df['away_team'] == team_name)
    away_mask = (df['away_team'] == team_name)
    home_mask = (df['home_team'] == team_name)
    res_df = df[mask]
    res_df['Opponent'] = 0
    res_df['goals_scored'] = 0
    res_df['goals_taken'] = 0

    res_df['Opponent'].loc[away_mask] = res_df['home_team'].loc[away_mask]
    res_df['Opponent'].loc[home_mask] = res_df['away_team'].loc[home_mask]

    res_df['goals_scored'].loc[away_mask] = res_df['away_goals'].loc[away_mask]
    res_df['goals_scored'].loc[home_mask] = res_df['home_goals'].loc[home_mask]

    res_df['goals_taken'].loc[away_mask] = res_df['home_goals'].loc[away_mask]
    res_df['goals_taken'].loc[home_mask] = res_df['away_goals'].loc[home_mask]

    res_df['Result'] = 0
    res_df['Result'].loc[res_df['goals_scored'] > res_df['goals_taken']] = 'Win'
    res_df['Result'].loc[res_df['goals_scored'] == res_df['goals_taken']] = 'Tie'
    res_df['Result'].loc[res_df['goals_scored'] < res_df['goals_taken']] = 'Loss'

    res_df = res_df.set_index('league_day', drop=False).sort_index()

    res_df['Points'] = 0
    res_df['Points'].loc[res_df['Result'] == 'Win'] = 3
    res_df['Points'].loc[res_df['Result'] == 'Tie'] = 1
    res_df['Points'].loc[res_df['Result'] == 'Loss'] = 0
    res_df['CumPoints'] = res_df['Points'].cumsum()

    res_df.drop(['away_team', 'home_team', 'away_goals', 'home_goals'], axis=1, inplace=True)

    return res_df

def get_team_names(fixture_id):
    query = db.session.query(League).filter((League.fixture_id == fixture_id)).statement
    df = pd.read_sql_query(query, db.session.bind)
    home_team = df['home_team'].values
    away_team = df['away_team'].values

    return home_team, away_team

def get_team_fixtures(date, league):
    fixture_year = date.year
    fixture_month = date.month

    if fixture_month < 8:
        fixture_season = fixture_year - 1
    else:
        fixture_season = fixture_year

    ids = get_league_ids(league, api_call=True, country=LEAGUE_COUNTRY[league], seasons=fixture_season)

    query = db.session.query(League).filter(League.league_id == ids[0][str(fixture_season)], League.event_date >= date,
                                            League.event_date < dt.datetime(fixture_year, fixture_month, date.day + 1)).statement
    df = pd.read_sql_query(query, db.session.bind)
    df['all_teams'] = df['home_team'] + ' - ' + df['away_team']

    fixture_dict = dict(zip(df.fixture_id, df.all_teams))

    return fixture_dict

def set_db_league(league_name,year):
    df = consolidate_season_data(league_name, year)

    for idx, row in df.iterrows():
        if db.session.query(League).filter_by(fixture_id=row.fixture_id).count() < 1:

            try:
                row_league = League(**row.to_dict())
                db.session.add(row_league)
                db.session.commit()
                db.session.flush()
                print("Fixture: ", row.fixture_id, ", Year:", year, ": Success")
            except Exception as e:
                db.session.rollback()
                print("Fixture: ", row.fixture_id, ", Year:", year  , ": Failed")

# for x in range(2011, 2020):
#     set_db_league("Premier League", x)

# ids = get_league_ids('Premier League', api_call=True, country='England', seasons=[2010, 2011, 2012,2013,2014,2015,2016,2017,2018])
# ids = get_league_ids('Ligue 1', api_call=False, country='France', seasons=2010)
# query = db.session.query(League).filter((League.league_id == ids[0][str(2010)])).statement
# df = pd.read_sql_query(query, db.session.bind)
#
# for i in range(30):
#     get_fixtures_stats(df['fixture_id'].iloc[i])

# get_api_results(BASE_URL, arg="leagues")