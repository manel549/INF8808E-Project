from dash import Dash, dcc, html, callback, Output, Input
import plotly.graph_objects as go
import pandas as pd

df = pd.read_csv('assets/data_fusionnee.csv')
df['MS_ACCDN'] = df['MS_ACCDN'].astype(int)

def month_to_season(month):
    if month in [1, 2, 3]: return 'Winter'
    elif month in [4, 5, 6]: return 'Spring'
    elif month in [7, 8, 9]: return 'Summer'
    else: return 'Autumn'

df['SEASON'] = df['MS_ACCDN'].apply(month_to_season)
df['Severity'] = df['GRAVITE'].apply(lambda x: 'Severe' if x == 'Mortel ou grave' else 'Other')

surface_state_labels = ["Dry", "Wet", "Hydroplaning", "Sand/Gravel", "Melting snow",
                        "Snow", "Compacted snow", "Icy", "Muddy", "Other"]
surface_state_codes = [11, 12, 13, 14, 15, 16, 17, 18, 19, 99]
theta = [i * (360 / len(surface_state_codes)) for i in range(len(surface_state_codes))]

lighting_colors = {1: "#FFD700", 2: "#FFA500", 3: "#1E90FF", 4: "#2F4F4F"}
lighting_labels = {1: "Daylight and clear", 2: "Daylight and twilight",
                   3: "Night and lit road", 4: "Night and unlit road"}
seasons = sorted(df['SEASON'].dropna().unique().tolist())

layout = html.Div([
    html.H2("Severe accidents by surface type and season (Barpolar)", style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='season-dropdown',
        options=[{'label': s, 'value': s} for s in seasons],
        value=seasons[0],
        style={'width': '50%', 'margin': '0 auto'}
    ),
    html.Div(id='polar-graph-container')
])

@callback(
    Output('polar-graph-container', 'children'),
    Input('season-dropdown', 'value')
)
def update_polar_chart(season):
    season_df = df[(df['SEASON'] == season) & (df['Severity'] == 'Severe')]
    fig = go.Figure()
    max_val = 0
    for lighting in lighting_colors:
        subset = season_df[season_df['CD_ECLRM'] == lighting]
        counts = subset.groupby('CD_ETAT_SURFC').size().reset_index(name='Number of Severe Accidents')
        r_vals, hover_texts = [], []
        for code, label in zip(surface_state_codes, surface_state_labels):
            n = counts[counts['CD_ETAT_SURFC'] == code]['Number of Severe Accidents'].values[0] if code in counts['CD_ETAT_SURFC'].values else 0
            max_val = max(max_val, n)
            r_vals.append(n)
            hover_texts.append(
                f"Season: {season}<br>Surface: {label}<br>Lighting: {lighting_labels[lighting]}<br>Severe accidents: {n}"
            )
        fig.add_trace(go.Barpolar(
            r=r_vals, theta=theta,
            name=lighting_labels[lighting],
            marker_color=lighting_colors[lighting],
            hoverinfo='text', hovertext=hover_texts
        ))
    fig.update_layout(
        title=f"Polar Bar Chart – Number of Severe Accidents ({season})",
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max_val * 1.05]),
            angularaxis=dict(tickvals=theta, ticktext=surface_state_labels, rotation=90, direction="clockwise")
        ),
        template="plotly_white", width=900, height=800
    )
    return dcc.Graph(figure=fig)
