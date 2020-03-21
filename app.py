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


external_stylesheets = ['https://codepen.io/trooperandz/pen/EOgJvg']
LEAGUE_NAME = 'Ligue 1'
COUNTRY = 'France'

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server.config.from_object(Config)
db = SQLAlchemy(server)
migrate = Migrate(server, db)

import data_handler

DATA_PATH = 'D:\\Data Mac\\Documents\\Datasets\\'
FILENAME = 'resultats-ligue-1.csv'

def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Img(id="ligue_1_logo", src="assets\\ligue_1_logo.svg", width='75px', height='150px', className='six columns'),
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
        dcc.DatePickerSingle(
            id='date-picker-single',
            min_date_allowed=dt(2010, 8, 5),
            max_date_allowed=dt(2020, 3, 21),
            date=str(dt(2018, 9, 23))
        ),
        html.Div([
            html.Div([
                html.Div(children='''Fixture main stats'''),
                dcc.Dropdown(id='all_teams3')
            ]),
            html.Div(children=[
                html.Div([html.H3("Summary Stats")]),
                build_summary_fixture()
            ], className='six columns')
        ])], className='row')

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
    return [{'label': x, 'value': x} for x in data_handler.consolidate_season_data(LEAGUE_NAME.lower().replace(' ', '_'), season)['home_team'].unique()]

@app.callback(dash.dependencies.Output('all_teams2', 'value'),
              [dash.dependencies.Input('all_teams2', 'options')])
def get_teams_value_hist(all_teams2):
    return all_teams2[0]['value']

@app.callback(dash.dependencies.Output('all_teams2', 'options'),
               [dash.dependencies.Input('season2', 'value')])
def get_teams_options_hist(season):
    return [{'label': x, 'value': x} for x in data_handler.consolidate_season_data(LEAGUE_NAME.lower().replace(' ', '_'), season)['home_team'].unique()]

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
                hovertemplate='<b>Points</b>: %{y}' + '<br><b>League Day</b>: %{text}<br>',
                text=[str(l) for l in res_df['league_day']]
            )
            for team, res_df in teams_dfs.items()],
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
    [dash.dependencies.Input('all_teams2', 'value'), dash.dependencies.Input('season2', 'value')])
def update_hist_graph(team, season):
    res_df = data_handler.get_team_results(COUNTRY, LEAGUE_NAME, team, season)

    return {
        'data': [
            dict(
                x=res_df['league_day'],
                y=res_df['goals_scored'],
                type='bar',
                name='Goals Scored'
            ),
            dict(
                x=res_df['league_day'],
                y=res_df['goals_taken'],
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
