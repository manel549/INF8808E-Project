from dash import dcc, html, callback, Output, Input
import plotly.graph_objects as go
import pandas as pd

df = pd.read_csv('assets/data_fusionnee.csv')
df['MS_ACCDN'] = df['MS_ACCDN'].astype(int)

def mois_vers_saison(mois):
    if mois in [1, 2, 3]: return 'Hiver'
    elif mois in [4, 5, 6]: return 'Printemps'
    elif mois in [7, 8, 9]: return 'Été'
    else: return 'Automne'

df['SAISON'] = df['MS_ACCDN'].apply(mois_vers_saison)
df['Gravité'] = df['GRAVITE'].apply(lambda x: 'Grave' if x == 'Mortel ou grave' else 'Autre')

etat_surface_labels = ["Sec", "Mouillé", "Aquaplanage", "Sable/Gravier", "Neige fondante",
                       "Neige", "Neige durcie", "Glacé", "Boueux", "Autre"]
etat_surface_codes = [11, 12, 13, 14, 15, 16, 17, 18, 19, 99]
theta = [i * (360 / len(etat_surface_codes)) for i in range(len(etat_surface_codes))]

couleur_eclairement = {1: "#FFD700", 2: "#FFA500", 3: "#1E90FF", 4: "#2F4F4F"}
label_eclairement = {1: "Jour et clarté", 2: "Jour et demi-obscurité",
                     3: "Nuit et chemin éclairé", 4: "Nuit et chemin non éclairé"}
saisons = sorted(df['SAISON'].dropna().unique().tolist())

layout = html.Div([
    html.H2("Accidents graves par type de surface et saison (Barpolar)", style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='saison-dropdown',
        options=[{'label': s, 'value': s} for s in saisons],
        value=saisons[0],
        style={'width': '50%', 'margin': '0 auto'}
    ),
    html.Div(id='polar-graph-container')
])

@callback(
    Output('polar-graph-container', 'children'),
    Input('saison-dropdown', 'value')
)
def update_polar_chart(saison):
    saison_df = df[(df['SAISON'] == saison) & (df['Gravité'] == 'Grave')]
    fig = go.Figure()
    max_val = 0
    for eclairement in couleur_eclairement:
        subset = saison_df[saison_df['CD_ECLRM'] == eclairement]
        counts = subset.groupby('CD_ETAT_SURFC').size().reset_index(name='Nb Accidents Graves')
        r_vals, hover_texts = [], []
        for code, label in zip(etat_surface_codes, etat_surface_labels):
            n = counts[counts['CD_ETAT_SURFC'] == code]['Nb Accidents Graves'].values[0] if code in counts['CD_ETAT_SURFC'].values else 0
            max_val = max(max_val, n)
            r_vals.append(n)
            hover_texts.append(
                f"Saison : {saison}<br>Surface : {label}<br>Éclairement : {label_eclairement[eclairement]}<br>Accidents graves : {n}"
            )
        fig.add_trace(go.Barpolar(
            r=r_vals, theta=theta,
            name=label_eclairement[eclairement],
            marker_color=couleur_eclairement[eclairement],
            hoverinfo='text', hovertext=hover_texts
        ))
    fig.update_layout(
        title=f"Polar Bar Chart – Nb d'accidents graves ({saison})",
        polar=dict(
            radialaxis=dict(visible=True, range=[0, max_val * 1.05]),
            angularaxis=dict(tickvals=theta, ticktext=etat_surface_labels, rotation=90, direction="clockwise")
        ),
        template="plotly_white", width=900, height=800
    )
    return dcc.Graph(figure=fig)
