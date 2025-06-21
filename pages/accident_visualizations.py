import pandas as pd
import plotly.graph_objects as go
from dash import html, dcc, Output, Input
from data import get_dataframe
import pandas as pd
import plotly.graph_objects as go

pd.set_option('future.no_silent_downcasting', True)

# Function to create Bar chart for Accidents by User Type (Day vs Night)
def accidents_by_user_type_day_night(df):
    usager_cols = {
        'IND_AUTO_CAMION_LEGER': 'Light vehicles',
        'IND_VEH_LOURD': 'Heavy vehicles',
        'IND_MOTO_CYCLO': 'Motorcycles',
        'IND_VELO': 'Bicycles',
        'IND_PIETON': 'Pedestrians'
    }

    df[list(usager_cols.keys())] = (
        df[list(usager_cols.keys())]
        .replace({'O': 1, 'N': 0})
        .infer_objects(copy=False) 
    )



    # Define Day/Night based on HR_ACCDN
    def classify_period(hr):
        if pd.isna(hr):
            return 'Unknown'
        if hr in ['08:00:00-11:59:00', '12:00:00-15:59:00', '16:00:00-19:59:00']:
            return 'Day'
        elif hr in ['00:00:00-03:59:00', '04:00:00-07:59:00', '20:00:00-23:59:00']:
            return 'Night'
        else:
            return 'Unknown'

    df['DAY_NIGHT'] = df['HR_ACCDN'].apply(classify_period)

    data_by_period = {}
    for period in ['Day', 'Night']:
        subset = df[df['DAY_NIGHT'] == period]
        counts = subset[list(usager_cols.keys())].sum()
        counts.index = [usager_cols[col] for col in counts.index]
        data_by_period[period] = counts.sort_values(ascending=False)

    fig = go.Figure()

    # Add traces for Day and Night
    fig.add_trace(go.Bar(
        x=data_by_period['Day'].index,
        y=data_by_period['Day'].values,
        name='Day',
        visible=True
    ))

    fig.add_trace(go.Bar(
        x=data_by_period['Night'].index,
        y=data_by_period['Night'].values,
        name='Night',
        visible=False
    ))

    # Buttons for interactivity
    fig.update_layout(
        title="Number of accidents by road user type (Day vs Night)",
        xaxis_title="User type",
        yaxis_title="Number of accidents",
        updatemenus=[dict(
    type="buttons",
    direction="right",
    buttons=[
        dict(label="Day",
             method="update",
             args=[
                 {"visible": [True, False]},
                 {"layout": {"title": "Number of accidents by road user type - Day"}}
             ]),
        dict(label="Night",
             method="update",
             args=[
                 {"visible": [False, True]},
                 {"layout": {"title": "Number of accidents by road user type - Night"}}
             ])
    ],
    showactive=True,
    x=0.57,
    y=1.15
)]

    )
    return fig

# Function to create bar chart for Severity by Month
def accident_severity_month(df):
    gravite_map = {
        "Léger": "Minor",
        "Mortel ou grave": "Severe",
        "Dommages matériels seulement": "Material damage",
        "Dommages matériels inférieurs au seuil de rapportage": "Low damage"
    }

    df_clean = df.copy()
    df_clean['GRAVITE'] = df_clean['GRAVITE'].map(gravite_map)
    df_clean['MS_ACCDN'] = pd.to_numeric(df_clean['MS_ACCDN'], errors='coerce').astype("Int64")

    # Define DAY/NIGHT based on HR_ACCDN
    def classify_period(hr):
        if pd.isna(hr):
            return 'Unknown'
        if hr in ['08:00:00-11:59:00', '12:00:00-15:59:00', '16:00:00-19:59:00']:
            return 'Day'
        elif hr in ['00:00:00-03:59:00', '04:00:00-07:59:00', '20:00:00-23:59:00']:
            return 'Night'
        else:
            return 'Unknown'

    df_clean['DAY_NIGHT'] = df_clean['HR_ACCDN'].apply(classify_period)
    df_clean = df_clean.dropna(subset=['GRAVITE', 'MS_ACCDN'])

    grouped = df_clean.groupby(['DAY_NIGHT', 'MS_ACCDN', 'GRAVITE']).size().reset_index(name='Count')

    # Month Labels
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    fig = go.Figure()

    # Set colors
    color_map = {
        "Severe": "darkred",
        "Minor": "lightgreen",
        "Material damage": "steelblue",
        "Low damage": "lightgrey"
    }

    # Add traces for Day and Night
    for grav in grouped['GRAVITE'].unique():
        df_day = grouped[(grouped['DAY_NIGHT'] == 'Day') & (grouped['GRAVITE'] == grav)]
        counts = df_day.set_index('MS_ACCDN').reindex(range(1, 13), fill_value=0)['Count']
        fig.add_trace(go.Bar(
            x=month_labels, y=counts, name=grav,
            marker_color=color_map.get(grav, 'gray'),
            visible=True
        ))

    for grav in grouped['GRAVITE'].unique():
        df_night = grouped[(grouped['DAY_NIGHT'] == 'Night') & (grouped['GRAVITE'] == grav)]
        counts = df_night.set_index('MS_ACCDN').reindex(range(1, 13), fill_value=0)['Count']
        fig.add_trace(go.Bar(
            x=month_labels, y=counts, name=grav,
            marker_color=color_map.get(grav, 'gray'),
            visible=False
        ))

    # Buttons for interactivity
    n_grav = len(grouped['GRAVITE'].unique())
    buttons = [
        dict(label="Day",
             method="update",
             args=[{"visible": [True]*n_grav + [False]*n_grav},
                   {"title": "Monthly Accident Severity (Daytime)"}]),
        dict(label="Night",
             method="update",
             args=[{"visible": [False]*n_grav + [True]*n_grav},
                   {"title": "Monthly Accident Severity (Nighttime)"}])
    ]
    fig.update_layout(
        title="Monthly accident severity (Day vs Night)",
        xaxis_title="",
        yaxis_title="Number of accidents",
        barmode='stack',
        updatemenus=[dict(
            type="buttons",
            direction="right",
            buttons=buttons,
            showactive=True,
            x=0.6,
            y=1.15
        )]
    )
    return fig



# Function to generate a heatmap of severe accidents by region and month
def generate_severe_accidents_heatmap(df):
    # Mapping mois → abréviations
    month_map = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
        9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }

    # Préparation des données
    df_grave = df[df['GRAVITE'] == 'Mortel ou grave'].dropna(subset=['REG_ADM', 'MS_ACCDN'])

    # Convertir et filtrer les mois
    df_grave['MS_ACCDN'] = pd.to_numeric(df_grave['MS_ACCDN'], errors='coerce').astype('Int64')
    df_grave = df_grave[df_grave['MS_ACCDN'].between(1, 12)]

    # Nettoyage des noms de régions
    df_grave['REG_ADM'] = df_grave['REG_ADM'].str.replace(r"\s*\(\d+\)", "", regex=True)

    # Pivot table
    pivot = df_grave.pivot_table(index='REG_ADM', columns='MS_ACCDN', aggfunc='size', fill_value=0)

    # Forcer tous les mois
    for m in range(1, 13):
        if m not in pivot.columns:
            pivot[m] = 0

    # Réordonner
    pivot = pivot[sorted(pivot.columns)]

    # Noms formatés pour x et y
    x_labels = [month_map[m] for m in pivot.columns]
    y_labels = pivot.index.tolist()
    z_values = pivot.values

    # Construction du texte de hover
    hover_text = [[f"{val} severe accidents in {y_labels[i]} during {x_labels[j]}"
                   for j, val in enumerate(row)] for i, row in enumerate(z_values)]

    # Création de la figure interactive
    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=x_labels,
        y=y_labels,
        text=hover_text,
        hoverinfo="text",
        colorscale='Reds',
        colorbar=dict(title="Severe accidents")
    ))

    fig.update_layout(
        title="Severe accidents by region and month ",
        xaxis_title="",
        yaxis_title="Region",
        width=1200,   
        height=800   
    )

    return fig


df = get_dataframe("data") 


COLUMNS = "IND_AUTO_CAMION_LEGER, IND_VEH_LOURD, IND_MOTO_CYCLO, IND_VELO, IND_PIETON, HR_ACCDN, MS_ACCDN, JR_SEMN_ACCDN, GRAVITE"
df_global = get_dataframe("data", cols=COLUMNS)
df.columns = df.columns.str.strip().str.replace('"', '')
df = df.rename(columns=lambda x: x.strip())


# -- Layout principal de la page --
layout = html.Div([
    html.H1("Road users and severity analysis", style={
        'textAlign': 'center',
        'marginTop': '30px',
        'marginBottom': '30px',
        'fontSize': '34px',
        'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
        'color': '#2c3e50'
    }),

    html.Div([
    html.P("This interactive dashboard offers clear insights into road accident patterns across Quebec. It helps identify which types of road users are most frequently involved in accidents, as well as when and where the most severe accidents tend to occur. This dashboard supports a deeper understanding of road safety dynamics across the province.", style={'marginTop': '20px'}),
     ], style={'textAlign': 'center','fontSize': '18px', 'maxWidth': '900px','color': '#2c3e50','marginLeft': 'auto',
                'marginRight': 'auto'}),


  html.Div([
    dcc.Tabs([
        dcc.Tab(label='Accidents by road user', children=[
            html.Div([
                html.H3("Road user type involvement", style={'textAlign': 'center','marginTop': '30px','marginBottom': '20px','fontSize': '34px','fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",'color': '#2c3e50'}),
                html.P("This bar chart breaks down accidents by user type, segmented into day and night and you can toggle between day and night stats.", style={'textAlign': 'center','fontSize': '18px', 'maxWidth': '900px','color': '#2c3e50','marginLeft': 'auto','marginRight': 'auto'} ),
                dcc.Graph(figure=accidents_by_user_type_day_night(df))
            ], style={'padding': '30px'})
        ]),

        dcc.Tab(label='Severity by month', children=[
            html.Div([
                html.H3("Monthly distribution of accident types", style={'textAlign': 'center','marginTop': '30px','marginBottom': '20px','fontSize': '34px','fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",'color': '#2c3e50'}),
                html.P("This stacked bar chart shows the monthly distribution of road accidents by type. You can toggle between day and night. You can also deselect types by clicking on a category in the legend to hide or show it.", style={'textAlign': 'center','fontSize': '18px', 'maxWidth': '900px','color': '#2c3e50','marginLeft': 'auto','marginRight': 'auto',}),
                dcc.Graph(figure=accident_severity_month(df))
            ], style={'padding': '30px'})
        ]),
        dcc.Tab(label='Severe accidents heatmap', children=[
            html.Div([
                html.H3("Severe accidents by region and month", style={'textAlign': 'center','marginTop': '30px','marginBottom': '20px','fontSize': '34px','fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",'color': '#2c3e50'}),
                html.P("This interactive heatmap shows the monthly distribution of severe road accidents across Quebec’s administrative regions. "
                       "Darker red cells indicate more severe accidents. When you hover over a cell, you’ll see the region, month, and exact number of accidents.", style={'textAlign': 'center','fontSize': '18px', 'maxWidth': '900px','color': '#2c3e50','marginLeft': 'auto','marginRight': 'auto',}),
                dcc.Graph(figure=generate_severe_accidents_heatmap(df)),

                
            ], style={'padding': '30px'})
        ]),

        
    ])
], style={'width': '95%', 'margin': '0 auto'})
])