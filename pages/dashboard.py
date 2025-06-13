from dash import Dash, dcc, html, callback, Output, Input, no_update
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


# Chargement des données
df = pd.read_csv('assets/data_fusionnee.csv')
df.columns = df.columns.str.strip().str.replace('"', '')
df = df.rename(columns=lambda x: x.strip())

# Préparation des colonnes
df['GRAVITE'] = df['GRAVITE'].replace({
    'Dommages matériels seulement': 'Matériels',
    'Dommages matériels inférieurs au seuil de rapportage': 'Mineurs',
    'Léger': 'Léger',
    'Mortel ou grave': 'Grave'
})

# Mappings
weather_mapping = {11: 'Clear', 12: 'Overcast', 13: 'Fog/Mist', 14: 'Rain/Drizzle', 15: 'Heavy Rain',
                   16: 'Strong Wind', 17: 'Snow/Hail', 18: 'Blowing Snow/Storm',
                   19: 'Freezing Rain', 99: 'Other'}
surface_mapping = {11: 'Dry', 12: 'Wet', 13: 'Aquaplaning', 14: 'Sand/Gravel', 15: 'Slush/Snow',
                   16: 'Snow-covered', 17: 'Hard-packed Snow', 18: 'Icy', 19: 'Muddy', 20: 'Oily', 99: 'Other'}
lighting_mapping = {1: 'Daylight - Clear Visibility', 2: 'Daylight - Low Visibility',
                    3: 'Night - Road Illuminated', 4: 'Night - Not Illuminated'}
env_mapping = {1: 'School Zone', 2: 'Residential', 3: 'Business / Commercial', 4: 'Industrial',
               5: 'Rural', 6: 'Forestry', 7: 'Recreational', 9: 'Other', 0: 'Not Specified'}

df['CD_COND_METEO'] = df['CD_COND_METEO'].map(weather_mapping)
df['CD_ETAT_SURFC'] = df['CD_ETAT_SURFC'].map(surface_mapping)
df['Lighting_Label'] = df['CD_ECLRM'].map(lighting_mapping)
df['Environment_Label'] = df['CD_ENVRN_ACCDN'].map(env_mapping)

# Régions pour carte
df['Region'] = df['REG_ADM'].str.strip()

region_coords = {
    'Bas-Saint-Laurent (01)': (48.5, -68.5),
    'Saguenay/-Lac-Saint-Jean (02)': (48.4, -71.1),
    'Capitale-Nationale (03)': (47.0, -71.2),
    'Mauricie (04)': (46.5, -72.7),
    'Estrie (05)': (45.4, -71.9),
    'Montréal (06)': (45.5, -73.6),
    'Outaouais (07)': (45.6, -76.0),
    'Abitibi-Témiscamingue (08)': (48.1, -78.0),
    'Côte-Nord (09)': (50.0, -63.0),
    'Nord-du-Québec (10)': (52.0, -75.0),
    'Gaspésie/-Îles-de-la-Madeleine (11)': (49.1, -65.4),
    'Chaudière-Appalaches (12)': (46.5, -70.5),
    'Laval (13)': (45.6, -73.8),
    'Lanaudière (14)': (46.0, -73.4),
    'Laurentides (15)': (46.5, -74.2),
    'Montérégie (16)': (45.3, -73.0),
    'Centre-du-Québec (17)': (46.0, -72.0)
}
df['lat'] = df['REG_ADM'].map(lambda x: region_coords.get(x.strip(), (None, None))[0] if pd.notna(x) else None)
df['lon'] = df['REG_ADM'].map(lambda x: region_coords.get(x.strip(), (None, None))[1] if pd.notna(x) else None)



# Dropdown options
gravite_options = [{'label': g, 'value': g} for g in df['GRAVITE'].unique()]

# Layout principal
layout = html.Div([
    html.H1("Road Accident Dashboard – Quebec", className='text-center pb-3'),

    dbc.Row([
    dbc.Col([
        html.Div([
            dcc.Dropdown(
                id='dashboard-dropdown',
                options=[
                    {'label': '1. Weather', 'value': 'weather'},
                    {'label': '2. Road Surface', 'value': 'surface'},
                    {'label': '3. Lighting', 'value': 'lighting'},
                    {'label': '4. Environment', 'value': 'environment'},
                    {'label': '5. Road Defects', 'value': 'defects'},
                    {'label': '6. Construction Zones', 'value': 'construction'},
                    {'label': '7. Weather vs Surface Heatmap', 'value': 'heatmap'},
                    {'label': '8. Before / After COVID-19', 'value': 'covid'}
                ],
                value='weather'
            )
        ], style={'width': '20%', 'margin': '0 auto',  'marginBottom': '30px'})  # ← largeur + centrage
    ], width=12)
]),


    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id='filter-gravite', options=gravite_options, placeholder="Gravité"),
        ], width=2),
        dbc.Col([
            dcc.Dropdown(id='filter-meteo', placeholder="Météo"),
        ], width=2),
        dbc.Col([
            dcc.Dropdown(id='filter-surface', placeholder="Surface"),
        ], width=2),
        dbc.Col([
            dcc.Dropdown(id='filter-env', placeholder="Environnement"),
        ], width=2),
        dbc.Col([
            dcc.Dropdown(id='filter-road', placeholder="Road Defect"),
        ], width=2),
        dbc.Col([
            dcc.Dropdown(id='filter-const', placeholder="Construction Zone"),
        ], width=2),
    ], className='mb-4'),

    dbc.Row([
        dbc.Col([
            html.Div(id='main-graph')
        ], width=8),
        dbc.Col([
            html.Div(id='map-container')
        ], width=4),
    ]),

    dbc.Row([
        dbc.Col([
            html.Label("Filter by year"),
            dcc.Slider(
                id='filter-annee',
                min=df['AN'].min(),
                max=df['AN'].max(),
                value=df['AN'].min(),
                marks={int(year): str(int(year)) for year in sorted(df['AN'].unique())},
                step=1,
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], width=12, className='mt-5')
    ])
], className='container-fluid')



@callback(
    Output('filter-gravite', 'disabled'),
    Output('filter-meteo', 'disabled'),
    Output('filter-surface', 'disabled'),
    Output('filter-env', 'disabled'),
    Output('filter-road', 'disabled'),
    Output('filter-const', 'disabled'),
    Input('dashboard-dropdown', 'value')
)
def toggle_filters(selected):
    return (
        selected != 'covid',
        selected in ['weather', 'heatmap'],
        selected in ['surface', 'heatmap'],
        selected == 'environment',
        selected == 'defects',
        selected == 'construction'
    )


@callback(
    Output('filter-meteo', 'options'),
    Output('filter-surface', 'options'),
    Output('filter-env', 'options'),
    Output('filter-road', 'options'),
    Output('filter-const', 'options'),
    Input('filter-annee', 'value'),
    Input('filter-gravite', 'value')
)
def update_filter_options(annee, gravite):
    filtered_df = df[df['AN'] == annee]
    if gravite:
        filtered_df = filtered_df[filtered_df['GRAVITE'] == gravite]

    return [
        [{'label': v, 'value': v} for v in filtered_df['CD_COND_METEO'].dropna().unique()],
        [{'label': v, 'value': v} for v in filtered_df['CD_ETAT_SURFC'].dropna().unique()],
        [{'label': v, 'value': v} for v in filtered_df['Environment_Label'].dropna().unique()],
        [{'label': v, 'value': v} for v in filtered_df['CD_ASPCT_ROUTE'].dropna().unique()],
        [{'label': v, 'value': v} for v in filtered_df['CD_ZON_TRAVX_ROUTR'].dropna().unique()]
    ]


@callback(
    Output('main-graph', 'children'),
    Output('map-container', 'children'),
    Input('dashboard-dropdown', 'value'),
    Input('filter-annee', 'value'),
    Input('filter-gravite', 'value'),
    Input('filter-meteo', 'value'),
    Input('filter-surface', 'value'),
    Input('filter-env', 'value'),
    Input('filter-road', 'value'),
    Input('filter-const', 'value')
)
def update_graph(selected, annee, gravite, meteo, surface, env, road, const):


    if selected == 'covid':
        dff = df.copy()  # Keep all years for COVID analysis
    else:
        dff = df[df['AN'] == annee]

    if gravite: dff = dff[dff['GRAVITE'] == gravite]
    if meteo: dff = dff[dff['CD_COND_METEO'] == meteo]
    if surface: dff = dff[dff['CD_ETAT_SURFC'] == surface]
    if env: dff = dff[dff['Environment_Label'] == env]
    if road: dff = dff[dff['CD_ASPCT_ROUTE'] == road]
    if const: dff = dff[dff['CD_ZON_TRAVX_ROUTR'] == const]

     
    if gravite: dff = dff[dff['GRAVITE'] == gravite]
    if meteo: dff = dff[dff['CD_COND_METEO'] == meteo]
    if surface: dff = dff[dff['CD_ETAT_SURFC'] == surface]
    if env: dff = dff[dff['Environment_Label'] == env]
    if road: dff = dff[dff['CD_ASPCT_ROUTE'] == road]
    if const: dff = dff[dff['CD_ZON_TRAVX_ROUTR'] == const]

    # Create main graph based on selection
    if selected == 'weather':
        fig = px.histogram(dff, x='CD_COND_METEO', color='GRAVITE',
                          barmode='group', 
                          title=f"Accidents by Weather Conditions - {annee}",
                          labels={'CD_COND_METEO': 'Weather Condition', 'count': 'Number of Accidents'})
        
    elif selected == 'surface':
        fig = px.histogram(dff, x='CD_ETAT_SURFC', color='GRAVITE',
                          barmode='group',
                          title=f"Accidents by Road Surface - {annee}",
                          labels={'CD_ETAT_SURFC': 'Road Surface Condition'})
        
    elif selected == 'lighting':
        fig = px.histogram(dff, x='Lighting_Label', color='GRAVITE',
                          barmode='group',
                          title=f"Accidents by Lighting Conditions - {annee}",
                          labels={'Lighting_Label': 'Lighting Condition'})
        
    elif selected == 'environment':
        fig = px.histogram(dff, x='Environment_Label', color='GRAVITE',
                          title=f"Accidents by Environment - {annee}",
                          labels={'Environment_Label': 'Environment Type'})
        
    elif selected == 'defects':
        fig = px.histogram(dff, x='CD_ASPCT_ROUTE', color='GRAVITE',
                          barmode='group',
                          title=f"Accidents by Road Defects - {annee}",
                          labels={'CD_ASPCT_ROUTE': 'Road Defect Type'})
        
    elif selected == 'construction':
        fig = px.histogram(dff, x='CD_ZON_TRAVX_ROUTR', color='GRAVITE',
                          barmode='group',
                          title=f"Accidents in Construction Zones - {annee}",
                          labels={'CD_ZON_TRAVX_ROUTR': 'Construction Zone Presence'})
        
    elif selected == 'heatmap':
        
        fig = px.density_heatmap(
            dff[dff['GRAVITE'] == 'Grave'], 
            x='CD_COND_METEO', 
            y='CD_ETAT_SURFC',
            title=f"Severe Accidents: Weather vs Road Surface - {annee}",
            labels={'CD_COND_METEO': 'Weather', 'CD_ETAT_SURFC': 'Road Surface'},
            color_continuous_scale='Reds'
        )
            
    elif selected == 'covid':
        # Ne pas filtrer par année pour garder toutes les données historiques
        covid_data = dff.groupby('AN').agg(
            Total=('AN', 'size'),
            Severe=('GRAVITE', lambda x: (x == 'Grave').sum())
        ).reset_index()
        
        fig = go.Figure()
        
        # Total accidents line
        fig.add_trace(go.Scatter(
            x=covid_data['AN'],
            y=covid_data['Total'],
            mode='lines+markers',
            name='Total Accidents',
            line=dict(color='blue', width=2)
        ))
        
        # Severe accidents line
        fig.add_trace(go.Scatter(
            x=covid_data['AN'],
            y=covid_data['Severe'],
            mode='lines+markers',
            name='Severe Accidents',
            line=dict(color='red', width=2)
        ))
        
        # Mettre à jour la ligne verticale dynamiquement
        fig.add_vline(
            x=annee, 
            line_width=3, 
            line_dash="dash", 
            line_color="green",
            annotation_text=f"Selected Year: {annee}", 
            annotation_position="top right"
        )
        
        # COVID period shading
        fig.add_vrect(
            x0=2020, x1=covid_data['AN'].max(),
            fillcolor="lightgray", opacity=0.2,
            annotation_text="COVID-19 Period", 
            annotation_position="top left"
        )
        
        fig.update_layout(
            title="Accident Trends Before/After COVID-19",
            xaxis_title="Year",
            yaxis_title="Number of Accidents",
            hovermode="x unified"
        )
    
    else:
        fig = go.Figure()

    # Carte corrigée
    map_df = dff.copy()
    
    # Debug: vérifiez les données avant création de la carte
    print("Régions présentes:", map_df['Region'].unique())
    print("Valeurs de lat:", map_df['lat'].unique())
    print("Valeurs de lon:", map_df['lon'].unique())
    
    # Création de la carte seulement s'il y a des données
    if not map_df.empty and 'lat' in map_df.columns and 'lon' in map_df.columns:
        map_fig = px.scatter_mapbox(
            map_df,
            lat='lat',
            lon='lon',
            hover_name='Region',
            hover_data=['GRAVITE', 'CD_COND_METEO', 'CD_ETAT_SURFC'],
            color='GRAVITE',
            zoom=5,
            center={"lat": 46.8, "lon": -71.2},  # Centre sur Québec
            height=500,
            title=f"Accidents by Region - {annee}"
        )
        map_fig.update_layout(
            mapbox_style="open-street-map",
            margin={"r":0,"t":30,"l":0,"b":0}
        )
    else:
        map_fig = go.Figure()
        map_fig.update_layout(
            title="No data to display for selected filters",
            xaxis={"visible": False},
            yaxis={"visible": False}
        )

    return dcc.Graph(figure=fig), dcc.Graph(figure=map_fig)