import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from DataHandler import consolidate_season_data

DATA_PATH = 'D:\\Data Mac\\Documents\\Datasets\\'
FILENAME = 'resultats-ligue-1.csv'


### Read Data
# df = pd.read_csv(DATA_PATH + FILENAME, sep=';', names=['LeagueDay', 'StartDate', 'EndDate', 'HomeTeam', 'AwayTeam',
#                                                       'HomeGoals', 'AwayGoals'], parse_dates=[1,2], header=0)

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


def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Img(id="ligue_1_logo", src="assets\\ligue_1_logo.svg", width='100px', height='200px', className='six columns'),
            html.Div([
                html.Div(
                    id="banner-text",
                    children=[
                        html.H2("Football Data Explorer", className='six rows'),
                        html.H3("Ligue 1", className='six rows'),
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
                                 value='tab2',
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
                                           ]
                                 )
                    ])


def build_tab1():
    return [
        dcc.Dropdown(id='season', options=[{'label': x, 'value': x} for x in list(range(2010, 2020))], value=2018),
        html.Div([
            html.Div([
                html.Div(children='''Season points'''),
                dcc.Dropdown(id='all_teams1', value='Paris Saint Germain', multi=True),
                dcc.Graph(
                    id='scored-taken-goals'
                )], className='six columns')]
        )
    ]


def build_tab2():
    return [
        html.Div(children='''Goals Scored/Taken'''),
        dcc.Dropdown(id='all_teams2', value='Paris Saint Germain'),
        dcc.Graph(id='hist_wlt'),
        build_summary()
    ]


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

def serve_layout():
    layout = html.Div(children=[
        build_banner(),

        dcc.Interval(
            id="interval-component",
            interval=2 * 1000,  # in milliseconds
            n_intervals=50,  # start at batch 50
            disabled=True,
        ),
        html.Div(
            id="app-container",
            children=[
                build_tabs(),
                # Main app
                html.Div(id="app-content"),
            ],
        ),
        dcc.Store(id="n-interval-stage", data=50),
    ])
    return layout

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

# app.layout = html.Div(children=[
#     build_banner(),
#
#     dcc.Interval(
#         id="interval-component",
#         interval=2 * 1000,  # in milliseconds
#         n_intervals=50,  # start at batch 50
#         disabled=True,
#     ),
#     html.Div(
#         id="app-container",
#         children=[
#             build_tabs(),
#             # Main app
#             html.Div(id="app-content"),
#         ],
#     ),
    # dcc.Dropdown(id='season', options=[{'label': x, 'value': x} for x in list(range(2010,2020))], value=2018),
    # html.Div([
    #     html.Div([
    #         html.Div(children='''Season points'''),
    #
    #         dcc.Dropdown(id='all_teams1', value='Paris Saint Germain', multi=True),
    #
    #         dcc.Graph(
    #             id='scored-taken-goals'
    #         )], className='six columns'),
    #
    #     html.Div([
    #         html.Div(children='''Goals Scored/Taken'''),
    #
    #         dcc.Dropdown(id='all_teams2', value='Paris Saint Germain'),
    #
    #         dcc.Graph(
    #             id='hist_wlt'
    #         )
    #     ],
    #         className='six columns')
    # ], className='row'),
    # html.Div([
    #     html.Div([html.Div([])], className='six columns'),
    #     html.Div([
    #         dash_table.DataTable(id='summary_table',
    #                              columns=[{"name": i, "id": i} for i in ['Stats', 'Values']],
    #                              style_cell_conditional=[
    #                                                         {
    #                                                             'if': {'column_id': c},
    #                                                             'textAlign': 'left'
    #                                                         } for c in ['Stats']
    #                                                     ] + [
    #                                                         {
    #                                                             'if': {'column_id': c},
    #                                                             'textAlign': 'center'
    #                                                         } for c in ['Values']
    #                                                     ],
    #                              style_data_conditional=[
    #                                  {
    #                                      'if': {'row_index': 'odd'},
    #                                      'backgroundColor': 'rgb(248, 248, 248)'
    #                                  }
    #                              ],
    #                              style_header={
    #                                  'backgroundColor': 'rgb(230, 230, 230)',
    #                                  'fontWeight': 'bold'
    #                              }),
    #     ], className='six columns')
    #
    # ], className='row'),
#    dcc.Store(id="n-interval-stage", data=50),
#])

app.layout = serve_layout()

@app.callback(
    [dash.dependencies.Output("app-content", "children"), dash.dependencies.Output("interval-component", "n_intervals")],
    [dash.dependencies.Input("app-tabs", "value")],
    [dash.dependencies.State("n-interval-stage", "data")],
)
def render_tab_content(tab_switch, stopped_interval):
    if tab_switch == "tab1":
        return build_tab1(), stopped_interval
    elif tab_switch == "tab2":
        return build_tab2(), stopped_interval


# Update interval
@app.callback(
    dash.dependencies.Output("n-interval-stage", "data"),
    [dash.dependencies.Input("app-tabs", "value")],
    [
        dash.dependencies.State("interval-component", "n_intervals"),
        dash.dependencies.State("interval-component", "disabled"),
        dash.dependencies.State("n-interval-stage", "data"),
    ],
)
def update_interval_state(tab_switch, cur_interval, disabled, cur_stage):
    if disabled:
        return cur_interval

    if tab_switch == "tab1":
        return cur_interval
    return cur_stage


@app.callback([dash.dependencies.Output('all_teams1', 'options'), dash.dependencies.Output('all_teams1', 'value')],
               [dash.dependencies.Input('season', 'value')])
def get_teams_options_scatter(season):
    return [{'label': x, 'value': x} for x in consolidate_season_data('ligue_1', season)['HomeTeam'].unique()]


@app.callback([dash.dependencies.Output('all_teams2', 'options'), dash.dependencies.Output('all_teams2', 'value')],
               [dash.dependencies.Input('season', 'value')])
def get_teams_options_hist(season):
    return [{'label': x, 'value': x} for x in consolidate_season_data('ligue_1', season)['HomeTeam'].unique()]


@app.callback(
    dash.dependencies.Output('scored-taken-goals', 'figure'),
    [dash.dependencies.Input('all_teams1', 'value'), dash.dependencies.Input('season', 'value')])
def update_scatter_graph(teams, season):
    teams_dfs = {}

    if type(teams) != list:
        teams = [teams]

    for team in teams:
        teams_dfs[team] = get_team_results(team, season)

    return {
        'data': [
            dict(
                x=res_df.index,
                y=res_df['CumPoints'],
                mode='lines-markers',
                name=team + ' Points',
                hovertemplate='<b>Points</b>: %{y}' + '<br><b>League Day</b>: %{text}<br>',
                text=[str(l) for l in res_df['LeagueDay']]
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


@app.callback(dash.dependencies.Output('summary_table', 'data'),
              [dash.dependencies.Input('all_teams2', 'value'), dash.dependencies.Input('season', 'value')])
def summary_table(all_teams2, season):
    res_df = get_team_results(all_teams2, season)
    summary = pd.DataFrame([res_df['GoalsTaken'].mean(), res_df['GoalsScored'].mean(),
                            res_df['GoalsTaken'].std(), res_df['GoalsScored'].std()],
                           index=['Average Goals Taken', 'Average Goals Scored', 'Stdev Goals Taken',
                                  'Stdev Goals Scored'],
                           columns=['Values'])
    summary = summary.reset_index(drop=False)
    summary = summary.rename({'index': 'Stats'}, axis=1)
    return summary.to_dict(orient='records')

if __name__ == '__main__':
    app.run_server(debug=True)
