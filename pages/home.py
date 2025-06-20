from dash import html, dcc, callback, Output, Input
import pandas as pd
from data import get_dataframe



COLUMNS = "CD_ETAT_SURFC, GRAVITE,MS_ACCDN "
df= get_dataframe("data", cols=COLUMNS)




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
            11: "Dry", 12: "Wet", 13: "Aquaplaning", 14: "Sand/Gravel",
            15: "Slushy Snow", 16: "Snow", 17: "Packed Snow",
            18: "Icy", 19: "Muddy", 99: "Other"
        }
        surface_label = surface_labels.get(surface_code, "Unknown")
    else:
        surface_label = "Unknown"

    
    return total_accidents, severe_accidents, surface_label

total_acc, severe_acc, common_surface = get_kpis(df)

layout = html.Div([
    html.H1(
        "Quebec road accidents insights",
        style={
            'textAlign': 'center',
            'marginBottom': '40px',
            'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
            'color': '#2C3E50'
        }
    ),

    html.Div([
        html.P(
            "This website presents various visualizations of road accidents in Quebec "
            "based on data related to severity, user types, weather, road surface conditions, "
            "lighting and time patterns.",
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
        html.H2("Key statistics", style={'textAlign': 'center', 'marginBottom': '30px', 'color': '#34495E'}),

        html.Div([
            html.Div([
                html.H3("Total accidents", style={'color': '#2980B9'}),
                html.P(f"{total_acc:,}",
                       style={
                           'fontSize': '36px',
                           'fontWeight': 'bold',
                           'color': '#2C3E50',
                           'margin': '5px 0'
                       })
            ], className='kpi-card'),

            html.Div([
                html.H3("Severe accidents", style={'color': '#E74C3C'}),
                html.P(f"{severe_acc:,}",
                       style={
                           'fontSize': '36px',
                           'fontWeight': 'bold',
                           'color': '#2C3E50',
                           'margin': '5px 0'
                       })
            ], className='kpi-card'),

            html.Div([
                html.H3("Most common surface", style={'color': '#27AE60'}),
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
