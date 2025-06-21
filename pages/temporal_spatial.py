
from dash import Dash, dcc, html, callback, Output, Input
import pandas as pd
from dash.dependencies import Input, Output
from pages import map_chart
from pages import bar_chart
from pages import bar_chart_region
from pages.template import create_template

from data import get_dataframe

def clean_region_names(df):
    df['region'] = df['region'].str.replace(r'\s*\(\d+\)', '', regex=True).str.upper()
    return df

def init_app_layout(fig_bar, fig_map):
    return html.Div(className='content', style={
        'fontFamily': 'Open Sans, sans-serif',
        'padding': '20px',
        'overflowX': 'hidden',
        'overflowY': 'hidden',
        'maxWidth': '100%',
        'boxSizing': 'border-box'
    }, children=[

        html.H1('Spatio-temporal analysis', style={
            'textAlign': 'center',
            'marginTop': '20px',
            'marginBottom': '30px',
            'fontSize': '34px',
            'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
            'color': '#2c3e50'
        }),

        html.P(
            "This interactive dashboard visualizes the spatio-temporal distribution of road accidents in Quebec. "
            "Click on a region to explore accident trends over time by severity, and use the time granularity selector "
            "to zoom from annual to daily patterns. The goal is to help identify high-risk zones and better understand accident dynamics.",
            style={'textAlign': 'center','fontSize': '18px', 'maxWidth': '900px','color': '#2c3e50','marginLeft': 'auto',
                'marginRight': 'auto','marginbottom': '30px'
            }
        ),

        html.Div(className='row', style={
            'display': 'flex',
            'flexDirection': 'row',
            'justifyContent': 'space-between',
            'marginBottom': '40px',
            'gap': '30px',
            'flexWrap': 'wrap'
        }, children=[

            html.Div(style={'flex': '1', 'minWidth': '400px'}, children=[

                html.H2("Accidents by region", style={'textAlign': 'left','fontSize': '25px', 'marginBottom': '20px','fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",'color': '#2c3e50'}),
                dcc.Graph(
                    figure=fig_map,
                    id='accident-map',
                    config={
                        'scrollZoom': True,
                        'displayModeBar': True
                    },
                    style={'height': '600px'}
                )
            ]),

            html.Div(style={'flex': '1', 'minWidth': '400px'}, children=[

                html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '10px', 'marginBottom': '20px'}, children=[
                    html.Label("Select time granularity:", style={'textAlign': 'left','fontSize': '20px', 'marginBottom': '20px','fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",'color': '#2c3e50'}),
                    dcc.Dropdown(
                        id='granularity-region-selector',
                        options=[
                            {'label': 'Year', 'value': 'year'},
                            {'label': 'Month', 'value': 'month'},
                            {'label': 'Day Type (Weekday/Weekend)', 'value': 'daytype'},
                            {'label': 'Quarter of Day', 'value': 'quarter_day'}
                        ],
                        value='year',
                        clearable=False,
                        style={'fontSize': '12px', 'flex': '1', 'height': '32px', 'width': '150px'}
                    )
                ]),

                html.Div(id='region-info', style={
                    'padding': '10px',
                    'backgroundColor': '#ffffff',
                    'borderRadius': '8px',
                    'boxShadow': '0 0 10px rgba(0,0,0,0.05)',
                    'height': '540px',
                    'overflowY': 'auto'
                }, children=[
                    html.P("", style={'fontSize': '14px'})
                ])
            ])
        ]),

        html.Div(style={'width': '100%'}, children=[
            html.H3("Accidents by time and type (Global)", style={'textAlign': 'left','fontSize': '25px', 'marginBottom': '20px','fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",'color': '#2c3e50'}),

            html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '10px', 'marginBottom': '20px'}, children=[
                html.Label("Select time granularity:", style={'textAlign': 'left','fontSize': '20px', 'marginBottom': '20px','fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",'color': '#2c3e50'}),
                dcc.Dropdown(
                    id='granularity-selector',
                    options=[
                        {'label': 'Year', 'value': 'year'},
                        {'label': 'Month', 'value': 'month'},
                        {'label': 'Day Type (Weekday/Weekend)', 'value': 'daytype'},
                        {'label': 'Quarter of Day', 'value': 'quarter_day'}
                    ],
                    value='year',
                    clearable=False,
                    style={'width': '150px', 'fontSize': '12px', 'height': '32px'}
                )
            ]),

            dcc.Graph(
                figure=fig_bar,
                id='bar-chart',
                config={'displayModeBar': False},
                style={'height': '400px', 'width': '100%'}
            )
        ])
    ])

create_template()
COLUMNS = "REG_ADM, JR_SEMN_ACCDN, GRAVITE, AN"
df_global = get_dataframe("data", cols=COLUMNS)


fig_bar = bar_chart.init_figure()
fig_bar = bar_chart.draw(fig_bar, df_global, mode='count', type_col='GRAVITE', granularity='AN')

df_map = map_chart.prepare_region_data(df_global)
df_map = clean_region_names(df_map)
fig_map = map_chart.draw_geo_map(df_map, center_lat=47.5, center_lon=-71.5, zoom=4.5)

layout = html.Div([
    dcc.Store(id='selected-region'),
    init_app_layout(fig_bar, fig_map)
])

@callback(
        Output('selected-region', 'data'),
        Input('accident-map', 'clickData')
    )
def store_clicked_region(clickData):
        if clickData:
            return clickData['points'][0]['customdata'][0]
        return None

@callback(
        Output('region-info', 'children'),
        Input('selected-region', 'data'),
        Input('granularity-region-selector', 'value')
    )
def update_region_bar_chart(region_clicked, granularity):
    if region_clicked:
        df = get_dataframe("data", cols="REG_ADM, JR_SEMN_ACCDN, GRAVITE, AN, MS_ACCDN, HR_ACCDN")

        if df is None or df.empty:
            return bar_chart.init_figure("Aucune donnée")

        df['JR_SEMN_ACCDN'] = df['JR_SEMN_ACCDN'].replace({'SEM': 'Weekday', 'FDS': 'Weekend'})

        # Pas besoin de filtrer ici, c'est fait dans draw()
        fig = bar_chart_region.init_figure(f"Accidents in {region_clicked}")
        fig = bar_chart.draw(fig, df, mode='count', type_col='GRAVITE', granularity=granularity.lower())


        return dcc.Graph(figure=fig, style={'width': '100%', 'height': '500px'})
    return html.P("", style={'fontSize': '14px'})


@callback(
        Output('bar-chart', 'figure'),
        Input('granularity-selector', 'value')
    )
def update_bar_chart(granularity):
        
        df = get_dataframe(
                    "data",
                    cols="REG_ADM, JR_SEMN_ACCDN, GRAVITE, AN, HR_ACCDN, MS_ACCDN"
                    
                )
        if df is None or df.empty:
            return bar_chart.init_figure("Aucune donnée")
        df['JR_SEMN_ACCDN'] = df['JR_SEMN_ACCDN'].replace({'SEM': 'Weekday', 'FDS': 'Weekend'})
        fig = bar_chart.init_figure(f"Accidents by {granularity.capitalize()}")
        fig = bar_chart.draw(fig, df, mode='count', type_col='GRAVITE', granularity=granularity)
        return fig