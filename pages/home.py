from dash import html, dcc, callback, Output, Input
import pandas as pd
from data import get_dataframe

df = get_dataframe("data") 

# Chargement et préparation des données
df['MS_ACCDN'] = df['MS_ACCDN'].astype(int)
df['Gravité'] = df['GRAVITE'].apply(lambda x: 'Grave' if x == 'Mortel ou grave' else 'Autre')

def get_kpis(data):
    total_accidents = len(data)
    severe_accidents = len(data[data['Gravité'] == 'Grave'])
    
    surface_mode_code = data['CD_ETAT_SURFC'].mode()
    if len(surface_mode_code) > 0:
        surface_code = surface_mode_code.iloc[0]
        surface_labels = {
            11: "Sec", 12: "Mouillé", 13: "Aquaplanage", 14: "Sable/Gravier",
            15: "Neige fondante", 16: "Neige", 17: "Neige durcie",
            18: "Glacé", 19: "Boueux", 99: "Autre"
        }
        surface_label = surface_labels.get(surface_code, "Inconnu")
    else:
        surface_label = "Inconnu"
    
    return total_accidents, severe_accidents, surface_label

total_acc, severe_acc, common_surface = get_kpis(df)

layout = html.Div([
    html.H1(
        "Quebec Road Accidents Dashboard",
        style={
            'textAlign': 'center',
            'marginBottom': '40px',
            'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
            'color': '#2C3E50'
        }
    ),

    html.Div([
        html.P(
            "This dashboard presents various visualizations of road accidents in Quebec "
            "based on data related to severity, user types, weather, road surface conditions, "
            "lighting, and time patterns.",
            style={
                'fontSize': '18px',
                'textAlign': 'center',
                'marginBottom': '50px',
                'color': '#34495E',
                'maxWidth': '800px',
                'marginLeft': 'auto',
                'marginRight': 'auto',
                'lineHeight': '1.6',
                'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
            }
        ),
    ]),

    html.Div([
        html.H2("Key Statistics", style={'textAlign': 'center', 'marginBottom': '30px', 'color': '#34495E'}),

        html.Div([
            html.Div([
                html.H3("Total Accidents", style={'color': '#2980B9'}),
                html.P(f"{total_acc:,}",
                       style={
                           'fontSize': '36px',
                           'fontWeight': 'bold',
                           'color': '#2C3E50',
                           'margin': '5px 0'
                       })
            ], className='kpi-card'),

            html.Div([
                html.H3("Severe Accidents", style={'color': '#E74C3C'}),
                html.P(f"{severe_acc:,}",
                       style={
                           'fontSize': '36px',
                           'fontWeight': 'bold',
                           'color': '#2C3E50',
                           'margin': '5px 0'
                       })
            ], className='kpi-card'),

            html.Div([
                html.H3("Most Common Surface", style={'color': '#27AE60'}),
                html.P(common_surface,
                       style={
                           'fontSize': '36px',
                           'fontWeight': 'bold',
                           'color': '#2C3E50',
                           'margin': '5px 0'
                       })
            ], className='kpi-card'),

        ], style={
            'display': 'flex',
            'justifyContent': 'space-around',
            'flexWrap': 'wrap',
            'maxWidth': '900px',
            'margin': '0 auto',
            'gap': '30px'
        }),
    ]),
])
