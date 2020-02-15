import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
from DataHandler import consolidate_season_data

DATA_PATH = 'D:\\Data Mac\\Documents\\Datasets\\'
FILENAME = 'resultats-ligue-1.csv'

### Read Data
#df = pd.read_csv(DATA_PATH + FILENAME, sep=';', names=['LeagueDay', 'StartDate', 'EndDate', 'HomeTeam', 'AwayTeam',
#                                                       'HomeGoals', 'AwayGoals'], parse_dates=[1,2], header=0)

def get_team_results(team_name, season):
    df = consolidate_season_data('ligue_1', season)

    mask = (df['HomeTeam']==team_name) + (df['AwayTeam']==team_name)
    away_mask = (df['AwayTeam']==team_name)
    home_mask = (df['HomeTeam']==team_name)
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
    res_df['Points'].loc[res_df['Result'] =='Win'] = 3
    res_df['Points'].loc[res_df['Result'] =='Tie'] = 1
    res_df['Points'].loc[res_df['Result'] =='Loss'] = 0
    res_df['CumPoints'] = res_df['Points'].cumsum()

    res_df.drop(['AwayTeam', 'HomeTeam', 'AwayGoals', 'HomeGoals'], axis=1, inplace=True)

    return res_df

test = get_team_results('Paris Saint Germain', 2010)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Ligue 1 Results'),
    dcc.Dropdown(id='season', options=[{'label': x, 'value': x} for x in list(range(2010,2020))], value=2018),
    html.Div([
        html.Div([
            html.Div(children='''Season points'''),

            dcc.Dropdown(id='all_teams1', multi=True),

            dcc.Graph(
                id='scored-taken-goals'
            )], className='six columns'),

        html.Div([
            dcc.Dropdown(id='all_teams2'),

            dcc.Graph(
                id='hist_wlt'
            )
        ],
            className='six columns')
    ], className='row')])

@app.callback(dash.dependencies.Output('all_teams1', 'options'), [dash.dependencies.Input('season', 'value')])
def get_teams_options_scatter(season):
    return [{'label': x, 'value': x} for x in consolidate_season_data('ligue_1', season)['HomeTeam'].unique()]

@app.callback(dash.dependencies.Output('all_teams2', 'options'), [dash.dependencies.Input('season', 'value')])
def get_teams_options_hist(season):
    return [{'label': x, 'value': x} for x in consolidate_season_data('ligue_1', season)['HomeTeam'].unique()]

@app.callback(
    dash.dependencies.Output('scored-taken-goals', 'figure'),
    [dash.dependencies.Input('all_teams1', 'value'), dash.dependencies.Input('season', 'value')])
def update_scatter_graph(teams, season):
    teams_dfs = []

    if type(teams) != list:
        teams = [teams]

    for team in teams:
        teams_dfs.append(get_team_results(team, season))

    return {
        'data': [
            dict(
                x=res_df.index,
                y=res_df['CumPoints'],
                mode='markers',
                name='Points',
                hovertemplate= '<b>Points</b>: %{y}' + '<br><b>League Day</b>: %{text}<br>',
                text=[str(l) for l in res_df['LeagueDay']]
            )
        for res_df in teams_dfs],
        'layout': {
            'height': 400,
            'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': 'Season Points'
            }],
            'yaxis': {'type': 'linear'},
            'xaxis': {'showgrid': False}
        }
    }

@app.callback(
    dash.dependencies.Output('hist_wlt', 'figure'),
    [dash.dependencies.Input('all_teams2', 'value'), dash.dependencies.Input('season', 'value')])
def update_hist_graph(team, season):
    res_df = get_team_results(team, season)

    return {
        'data': [
            dict(
                x=res_df['LeagueDay'],
                y=res_df['GoalsScored'],
                type='bar',
                name='Goals Scored'
            ),
            dict(
                x=res_df['LeagueDay'],
                y=res_df['GoalsTaken'],
                type='bar',
                name='Goals Taken'
            )
        ],
        'layout': {
            'height': 400,
            'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': 'Game Score'
            }],
            'yaxis': {'type': 'linear'},
            'xaxis': {'showgrid': False}
        }
    }

if __name__ == '__main__':
    app.run_server(debug=True)