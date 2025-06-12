# -*- coding: utf-8 -*- 

'''
    File name: app.py
    Python Version: 3.11.0
    Simplified version: displays a stacked bar chart of accident counts
    by year and severity, along with a Sankey diagram.
'''

import dash
from dash import dcc, html
import pandas as pd
import map_chart  
import bar_chart
from template import create_template
from Rihem import create_sankey_chart  # Import Sankey chart function


# Initialisation de l'application Dash
app = dash.Dash(__name__)
app.title = 'Quebec Road Accidents'


def prep_data():
    '''
    Lit le fichier CSV contenant les données d’accidents.

    Returns:
        pd.DataFrame: Données des accidents
    '''
    df = pd.read_csv(r'C:\Users\RBerbere\Downloads\code (1) - Copie\code\src\data_fusionnee.csv')
    df.columns = df.columns.str.strip().str.replace('"', '').str.replace('\t', '')
    return df


def init_app_layout(fig_bar, fig_map, fig_sankey):
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
            ]), 
            html.Div(className='viz-container', children=[ 
                html.H2("Accident Severity Sankey Diagram"), 
                dcc.Graph( 
                    figure=fig_sankey, 
                    config=dict(scrollZoom=True), 
                    className='graph', 
                    id='sankey-chart' 
                ) 
            ]) 
        ]) 
    ])

create_template()

app = dash.Dash(__name__)
app.title = 'Quebec Road Accidents'

# Load and prepare data
df = prep_data()

# Create the bar chart
fig_bar = bar_chart.init_figure()
fig_bar = bar_chart.draw(fig_bar, df, mode='count', time_col='AN', type_col='GRAVITE')

# Prepare the map
df_map = map_chart.prepare_region_data()
fig_map = map_chart.draw_geo_map(df_map)

# Create the Sankey chart by calling the function from sankey_chart.py
fig_sankey = create_sankey_chart(df)

# Set layout
app.layout = init_app_layout(fig_bar, fig_map, fig_sankey)

if __name__ == '__main__':
    app.run(debug=True)
