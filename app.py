import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from datetime import datetime as dt
import plotly.graph_objects as go
import plotly.subplots as tls

external_stylesheets = ['https://codepen.io/trooperandz/pen/EOgJvg']
LEAGUE_NAME = 'Premier League'
COUNTRY = 'England'

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server.config.from_object(Config)
db = SQLAlchemy(server)
migrate = Migrate(server, db)

import data_handler
from models import League

DATA_PATH = 'D:\\Data Mac\\Documents\\Datasets\\'
FILENAME = 'resultats-ligue-1.csv'
LEAGUE_COUNTRY = {'Ligue 1': 'France', 'Premier League': 'England'}

def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Img(id="premier_league_logo", src="assets\\premier_league_logo.svg", width='75px', height='150px', className='six columns'),
            html.Div([
                html.Div(
                    id="banner-text",
                    children=[
                        html.H3("Football Data Explorer", className='six rows'),
                        html.H4(LEAGUE_NAME, className='six rows'),
                    ],
                )]
            , className='six columns')
        ],
    )


def build_tabs():
    return html.Div(id='tabs',
                    className='tabs',
                    children=[
                        dcc.Tabs(id='app-tabs',
                                 value='tab1',
                                 className='custom-tabs',
                                 children=[dcc.Tab(id='season-tab',
                                                   label='Season Data',
                                                   className='custom-tab',
                                                   value='tab1',
                                                   selected_className='custom-tab--selected'
                                                   ),
                                           dcc.Tab(id='team-tab',
                                                   label='Team Data',
                                                   className='custom-tab',
                                                   value='tab2',
                                                   selected_className='custom-tab--selected'
                                                   ),
                                           dcc.Tab(id='fixture-tab',
                                                   label='Fixture Data',
                                                   className='custom-tab',
                                                   value='tab3',
                                                   selected_className='custom-tab--selected'
                                                   ),
                                           ]
                                 ),
                        html.Div(id="app-content"),
                    ])


def build_tab1():
    return html.Div(children=[
        dcc.Dropdown(id='season1', options=[{'label': x, 'value': x} for x in list(range(2010, 2020))], value=2018),
        html.Div([
            html.Div([
                html.Div(children='''Season points'''),
                dcc.Dropdown(id='all_teams1', value='Paris Saint Germain', multi=True),
                dcc.Graph(
                    id='scored-taken-goals'
                )], className='six columns')]
        )
    ])


def build_tab2():
    return html.Div(children=[
        dcc.Dropdown(id='season2', options=[{'label': x, 'value': x} for x in list(range(2010, 2020))], value=2018),
        html.Div([
            html.Div([
                html.Div(children='''Goals Scored/Taken'''),
                dcc.Dropdown(id='all_teams2', value='Paris Saint Germain'),
                dcc.Graph(
                    id='hist_wlt'
                )], className='six columns'),
            html.Div(children=[
                html.Div([html.H3("Summary Stats")]),
                build_summary()], className='six columns')
        ])], className='row')

def build_tab3():
    return html.Div(children=[
        html.Div(children=[dcc.DatePickerSingle(
            id='date-picker-single',
            min_date_allowed=dt(2010, 8, 5),
            max_date_allowed=dt(2020, 3, 21),
            date=str(dt(2018, 9, 23))
        ),
            html.Div([
                html.Div(children='''Fixture main stats'''),
                dcc.Dropdown(id='all_teams3')
            ])], className='row'),
        html.Div([html.Div([
            html.Div(children=[
                html.Div([html.H3("Summary Stats")]),
                build_summary_fixture()
            ])
        ], className='six columns'),
            html.Div([
                html.Div([html.H3("Offensive/Defensive Stats")]),
                dcc.Graph(id='hozbar-chart')
            ], className='six columns')], className='row')
    ])

def build_summary():
    return html.Div([
        dash_table.DataTable(id='summary_table',
                             columns=[{"name": i, "id": i} for i in ['Stats', 'Values']],
                             style_cell_conditional=[
                                                        {
                                                            'if': {'column_id': c},
                                                            'textAlign': 'left'
                                                        } for c in ['Stats']
                                                    ] + [
                                                        {
                                                            'if': {'column_id': c},
                                                            'textAlign': 'center'
                                                        } for c in ['Values']
                                                    ],
                             style_data_conditional=[
                                 {
                                     'if': {'row_index': 'odd'},
                                     'backgroundColor': 'rgb(248, 248, 248)'
                                 }
                             ],
                             style_header={
                                 'backgroundColor': 'rgb(230, 230, 230)',
                                 'fontWeight': 'bold'
                             }),
    ], className='six columns')

def build_summary_fixture():
    return html.Div([
        dash_table.DataTable(id='summary_fixture_table',
                             columns=[{"name": i, "id": i} for i in ['Stats', 'Values']],
                             style_cell_conditional=[
                                                        {
                                                            'if': {'column_id': c},
                                                            'textAlign': 'left'
                                                        } for c in ['Stats']
                                                    ] + [
                                                        {
                                                            'if': {'column_id': c},
                                                            'textAlign': 'center'
                                                        } for c in ['Values']
                                                    ],
                             style_data_conditional=[
                                 {
                                     'if': {'row_index': 'odd'},
                                     'backgroundColor': 'rgb(248, 248, 248)'
                                 }
                             ],
                             style_header={
                                 'backgroundColor': 'rgb(230, 230, 230)',
                                 'fontWeight': 'bold'
                             }),
    ], className='six columns')

def serve_layout():
    layout = html.Div(children=[
        build_banner(),

        html.Div(
            id="app-container",
            children=[
                build_tabs(),
                # Main app
            ],
        ),
    ])
    return layout

app.layout = serve_layout()

@app.callback(dash.dependencies.Output("app-content", "children"),
              [dash.dependencies.Input("app-tabs", "value")],
)
def render_tab_content(tab_switch):
    if tab_switch == "tab1":
        return build_tab1()
    elif tab_switch == "tab2":
        return build_tab2()
    elif tab_switch == "tab3":
        return build_tab3()

@app.callback(dash.dependencies.Output('all_teams1', 'value'),
              [dash.dependencies.Input('all_teams1', 'options')])
def get_teams_value_scatter(all_teams1):
    return all_teams1[0]['value']

@app.callback(dash.dependencies.Output('all_teams1', 'options'),
              [dash.dependencies.Input('season1', 'value')])
def get_teams_options_scatter(season):
    league_id = data_handler.get_league_ids(LEAGUE_NAME, api_call=True, country=LEAGUE_COUNTRY[LEAGUE_NAME], seasons=season)
    query = db.session.query(League).filter(League.league_id == league_id[0][str(season)]).statement
    df = pd.read_sql_query(query, db.session.bind)

    df.rename(columns={'goalsHomeTeam': 'home_goals', 'goalsAwayTeam': 'away_goals',
                       'statusShort': 'status_short', 'firstHalfStart': 'first_half_start',
                       'secondHalfStart': 'second_half_start'}, inplace=True)

    return [{'label': x, 'value': x} for x in df['home_team'].unique()]

@app.callback(dash.dependencies.Output('all_teams2', 'value'),
              [dash.dependencies.Input('all_teams2', 'options')])
def get_teams_value_hist(all_teams2):
    return all_teams2[0]['value']

@app.callback(dash.dependencies.Output('all_teams2', 'options'),
               [dash.dependencies.Input('season2', 'value')])
def get_teams_options_hist(season):
    league_id = data_handler.get_league_ids(LEAGUE_NAME, api_call=True, country=LEAGUE_COUNTRY[LEAGUE_NAME],
                                            seasons=season)
    query = db.session.query(League).filter(League.league_id == league_id[0][str(season)]).statement
    df = pd.read_sql_query(query, db.session.bind)

    df.rename(columns={'goalsHomeTeam': 'home_goals', 'goalsAwayTeam': 'away_goals',
                       'statusShort': 'status_short', 'firstHalfStart': 'first_half_start',
                       'secondHalfStart': 'second_half_start'}, inplace=True)

    return [{'label': x, 'value': x} for x in df['home_team'].unique()]

@app.callback(dash.dependencies.Output('all_teams3', 'value'),
              [dash.dependencies.Input('all_teams3', 'options')])
def get_teams_value_hist(all_teams3):
    return all_teams3[0]['value']

@app.callback(dash.dependencies.Output('all_teams3', 'options'),
               [dash.dependencies.Input('date-picker-single', 'date')])
def get_fixtures_options(date):
    date = pd.to_datetime(date)
    fixture_dict = data_handler.get_team_fixtures(date, LEAGUE_NAME)

    return [{'label': value, 'value': key} for key, value in fixture_dict.items()]

@app.callback(dash.dependencies.Output('scored-taken-goals', 'figure'),
              [dash.dependencies.Input('all_teams1', 'value'), dash.dependencies.Input('season1', 'value')])
def update_scatter_graph(teams, season):
    teams_dfs = {}

    if type(teams) != list:
        teams = [teams]

    for team in teams:
        teams_dfs[team] = data_handler.get_team_results(COUNTRY, LEAGUE_NAME, team, season)

    return {
        'data': [
            dict(
                x=res_df.index,
                y=res_df['CumPoints'],
                mode='lines-markers',
                name=team + ' Points',
                hovertemplate='<b>Points</b>: %{y}' + '<br><b>League Day</b>: %{text[0]}<br>' + '<br><b>Opponent</b>: %{text[1]}<br>',
                text=[(str(l1), l2) for l1, l2 in zip(res_df['league_day'], res_df['Opponent'])]
            )
            for team, res_df in teams_dfs.items()],
        'layout': {
            'height': 400,
            'margin': {'l': 50, 'b': 50, 'r': 0, 't': 0},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': 'Season Points'
            }],
            'yaxis': {'title': 'Cumulative League Points', 'type': 'linear'},
            'xaxis': {'title': 'Season Days', 'showgrid': False}
        }
    }


@app.callback(
    dash.dependencies.Output('hist_wlt', 'figure'),
    [dash.dependencies.Input('all_teams2', 'value'), dash.dependencies.Input('season2', 'value')])
def update_hist_graph(team, season):
    res_df = data_handler.get_team_results(COUNTRY, LEAGUE_NAME, team, season)

    return {
        'data': [
            dict(
                x=res_df['league_day'],
                y=res_df['goals_scored'],
                type='bar',
                name='Goals Scored',
                hovertemplate='<b>Points</b>: %{y}' + '<br><b>League Day</b>: %{text[0]}<br>' + '<br><b>Opponent</b>: %{text[1]}<br>',
                text=[(str(l1), l2) for l1, l2 in zip(res_df['league_day'], res_df['Opponent'])]
            ),
            dict(
                x=res_df['league_day'],
                y=res_df['goals_taken'],
                type='bar',
                name='Goals Taken',
                hovertemplate='<b>Points</b>: %{y}' + '<br><b>League Day</b>: %{text[0]}<br>' + '<br><b>Opponent</b>: %{text[1]}<br>',
                text=[(str(l1), l2) for l1, l2 in zip(res_df['league_day'], res_df['Opponent'])]
            )
        ],
        'layout': {
            'height': 400,
            'margin': {'l': 50, 'b': 50, 'r': 0, 't': 0},
            'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': 'Game Score'
            }],
            'yaxis': {'title': 'Goals', 'type': 'linear'},
            'xaxis': {'title': 'League Days', 'showgrid': False}
        }
    }

@app.callback(
    dash.dependencies.Output('radar-chart', 'figure'),
    [dash.dependencies.Input('all_teams3', 'value')])
def update_radar_chart(fixture_id):
    res_df = data_handler.get_fixtures_stats(fixture_id)
    home_team, away_team = data_handler.get_team_names(fixture_id)
    res_df['passes_perc_home'] = res_df['passes_perc_home']*100
    res_df['passes_perc_away'] = res_df['passes_perc_away']*100

    res_df['ball_possession_home'] = res_df['ball_possession_home']*100
    res_df['ball_possession_away'] = res_df['ball_possession_away']*100

    categories = ['Shots Taken', 'Shots on Goal', 'Possession', 'Fouls', 'Accurate Passes Percentage']
    home_team_stats = res_df[['total_shots_home', 'shots_on_goal_home', 'ball_possession_home', 'fouls_home',
                              'passes_perc_home']].values[0]
    away_team_stats = res_df[['total_shots_away', 'shots_on_goal_away', 'ball_possession_away', 'fouls_away',
                              'passes_perc_away']].values[0]

    return {
        'data':
            [
                go.Scatterpolar(r=home_team_stats,
                                theta=categories,
                                fill='toself',
                                name=home_team[0]),
                go.Scatterpolar(r=away_team_stats,
                                theta=categories,
                                fill='toself',
                                name=away_team[0])
             ],
        'layout':
            {'polar': dict(radialaxis=dict(visible=True),tickformat=".2%"), 'showlegend': True}
    }

@app.callback(
    dash.dependencies.Output('hozbar-chart', 'figure'),
    [dash.dependencies.Input('all_teams3', 'value')])
def update_hoz_bar_chart(fixture_id):
    res_df = data_handler.get_fixtures_stats(fixture_id)
    home_team, away_team = data_handler.get_team_names(fixture_id)
    res_df['passes_perc_home'] = res_df['passes_perc_home']*100
    res_df['passes_perc_away'] = res_df['passes_perc_away']*100

    res_df['ball_possession_home'] = res_df['ball_possession_home']*100
    res_df['ball_possession_away'] = res_df['ball_possession_away']*100

    home_team_stats = res_df[['home_goals', 'total_shots_home', 'shots_on_goal_home', 'ball_possession_home', 'fouls_home',
                              'passes_perc_home']]
    away_team_stats = res_df[['total_shots_away', 'shots_on_goal_away', 'ball_possession_away', 'fouls_away',
                              'passes_perc_away']]
    home_team_stats.rename(columns={'home_goals': 'Goals', 'total_shots_home': 'Total Shots',
                                    'shots_on_goal_home': 'Shots on Goals', 'ball_possession_home': 'Possession',
                                    'fouls_home': 'Fouls', 'passes_perc_home': 'Passes Precision'}, inplace=True)
    away_team_stats.rename(columns={'away_goals': 'Goals', 'total_shots_away': 'Total Shots',
                                    'shots_on_goal_away': 'Shots on Goals', 'ball_possession_away': 'Possession',
                                    'fouls_away': 'Fouls', 'passes_perc_away': 'Passes Precision'}, inplace=True)

    fig = tls.make_subplots(rows=1, cols=2, shared_yaxes=True, vertical_spacing=0.001, horizontal_spacing=0.001)

    fig.add_trace(go.Bar(x=home_team_stats.values[0], y=home_team_stats.columns,
                         name=home_team[0], orientation='h'))
    fig.add_trace(go.Bar(x=away_team_stats.values[0], y=away_team_stats.columns,
                         name=away_team[0], orientation='h'))
    return fig

@app.callback(dash.dependencies.Output('summary_table', 'data'),
              [dash.dependencies.Input('all_teams2', 'value'), dash.dependencies.Input('season2', 'value')])
def summary_table(all_teams2, season):
    res_df = data_handler.get_team_results(COUNTRY, LEAGUE_NAME, all_teams2, season)
    summary = pd.DataFrame([res_df['goals_taken'].mean(), res_df['goals_scored'].mean(),
                            res_df['goals_taken'].std(), res_df['goals_scored'].std()],
                           index=['Average Goals Taken', 'Average Goals Scored', 'Stdev Goals Taken',
                                  'Stdev Goals Scored'],
                           columns=['Values'])
    summary = summary.reset_index(drop=False)
    summary = summary.rename({'index': 'Stats'}, axis=1)
    return summary.to_dict(orient='records')

@app.callback(dash.dependencies.Output('summary_fixture_table', 'data'),
              [dash.dependencies.Input('all_teams3', 'value')])
def summary_fixture_table(fixture_id):
    res_df = data_handler.get_fixtures_stats(fixture_id)
    summary = pd.DataFrame([res_df['shots_on_goal_home'].values, res_df['shots_on_goal_away'].values,
                            res_df['total_shots_home'].values, res_df['total_shots_away'].values],
                           index=['Shots On Goal Home', 'Shots On Goal Away', 'Total Shots On Goal Home',
                                  'Total Shots On Goal Away'],
                           columns=['Values'])
    summary = summary.reset_index(drop=False)
    summary = summary.rename({'index': 'Stats'}, axis=1)
    return summary.to_dict(orient='records')

if __name__ == '__main__':
    app.run_server(debug=True)
