# -*- coding: utf-8 -*-

'''
    File name: app.py
    Python Version: 3.11.0

    Simplified version: displays only a stacked bar chart of accident counts
    by year and severity.
'''

import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import map_chart  
import bar_chart
from template import create_template


# Initialisation de l'application Dash
app = dash.Dash(__name__)
app.title = 'Quebec Road Accidents'


def prep_data():
    '''
    Lit le fichier CSV contenant les données d’accidents.

    Returns:
        pd.DataFrame: Données des accidents
    '''
    return pd.read_csv('./assets/data/data_fusionnee.csv')


def init_app_layout(fig_bar, fig_map):
    return html.Div(className='content', children=[
        html.Header([
            html.H1('Quebec Road Accidents')
        ]),
        html.Main(children=[
            html.Div(className='viz-container', children=[
                html.H2("Accidents by Year and Severity"),
                dcc.Graph(
                    figure=fig_bar,
                    config=dict(scrollZoom=False),
                    className='graph',
                    id='bar-chart'
                )
            ]),
            html.Div(className='viz-container', children=[
                html.H2("Accidents by Region"),
                dcc.Graph(
                    figure=fig_map,
                    config=dict(scrollZoom=True),
                    className='graph',
                    id='accident-map'
                )
            ])
        ])
    ])


create_template()

app = dash.Dash(__name__)
app.title = 'Quebec Road Accidents'

df_bar = pd.read_csv('./assets/data/data_fusionnee.csv')
fig_bar = bar_chart.init_figure()
fig_bar = bar_chart.draw(fig_bar, df_bar, mode='count', time_col='AN', type_col='GRAVITE')

df_map = map_chart.prepare_region_data()
fig_map = map_chart.draw_geo_map(df_map)

app.layout = init_app_layout(fig_bar, fig_map)

if __name__ == '__main__':
    app.run_server(debug=True)

