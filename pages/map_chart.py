import pandas as pd
import plotly.express as px
from data import get_dataframe





REGION_COORDS = {
    "Bas-Saint-Laurent (01)": (48.5, -68.5),
    "Saguenay―Lac-Saint-Jean (02)": (48.3, -71.1),
    "Capitale-Nationale (03)": (47.0, -71.5),
    "Mauricie (04)": (46.6, -72.7),
    "Estrie (05)": (45.5, -71.9),
    "Montréal (06)": (45.5, -73.6),
    "Outaouais (07)": (45.5, -76.0),
    "Abitibi-Témiscamingue (08)": (48.0, -78.5),
    "Côte-Nord (09)": (50.2, -63.0),
    "Nord-du-Québec (10)": (53.0, -76.0),
    "Gaspésie―Îles-de-la-Madeleine (11)": (49.0, -64.3),
    "Chaudière-Appalaches (12)": (46.5, -70.9),
    "Laval (13)": (45.6, -73.8),
    "Lanaudière (14)": (46.0, -73.4),
    "Laurentides (15)": (46.3, -74.0),
    "Montérégie (16)": (45.3, -73.0),
    "Centre-du-Québec (17)": (46.4, -72.0)
}


def prepare_region_data():
    '''
    Prépare les données agrégées par région pour la carte à partir de la base Supabase.

    Returns:
        pd.DataFrame: données prêtes avec lat/lon/nb_accidents
    '''
    df = get_dataframe("data")
    if df is None or df.empty:
        print("Aucune donnée disponible depuis Supabase.")
        return pd.DataFrame(columns=['region', 'nb_accidents', 'latitude', 'longitude'])

    # Nettoyage des colonnes si nécessaire
    df.columns = df.columns.str.strip().str.replace('"', '').str.replace("'", '').str.replace('\t', '')

    # Identifier la bonne colonne
    if 'REG_ADM' not in df.columns:
        for col in df.columns:
            if 'REG_ADM' in col:
                df.rename(columns={col: 'REG_ADM'}, inplace=True)
                break

    df['region'] = df['REG_ADM']

    df_counts = df['region'].value_counts().reset_index()
    df_counts.columns = ['region', 'nb_accidents']

    # Ajouter les coordonnées depuis le dictionnaire
    df_counts['latitude'] = df_counts['region'].map(lambda r: REGION_COORDS.get(r, (None, None))[0])
    df_counts['longitude'] = df_counts['region'].map(lambda r: REGION_COORDS.get(r, (None, None))[1])

    return df_counts

import plotly.express as px
import plotly.graph_objects as go

def draw_geo_map(df_counts, center_lat=47.5, center_lon=-71.5, zoom=4.5):
    fig = px.scatter_geo(
        df_counts,
        lat='latitude',
        lon='longitude',
        size='nb_accidents',
        color='region',
        hover_name='region',
        hover_data={'nb_accidents': True, 'latitude': False, 'longitude': False},
        projection='natural earth',
        title='Click on a region on the map to explore accident trends over time in the panel on the right',
        custom_data=['region']
    )

    fig.update_layout(
        legend_title=dict(text='Region'),
        template='plotly_white',  # Assure l'application du style
        font=dict(
            family='Open Sans, sans-serif',
            size=14,
            color='#333333'
        ),
        title_font=dict(
            family='Open Sans, sans-serif',
            size=14,
            color='#333333'
        ),
        legend=dict(
            font=dict(
                family='Open Sans, sans-serif',
                size=12,
                color='#333333'
            )
        ),
        geo=dict(
            scope='north america',
            showland=True,
            landcolor='lightgray',
            center=dict(lat=center_lat, lon=center_lon),
            projection_scale=zoom
        )
    )

    return fig
