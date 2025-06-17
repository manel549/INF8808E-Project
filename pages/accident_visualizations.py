import pandas as pd
import plotly.graph_objects as go
#from data import df 

# Function to create Bar chart for Accidents by User Type (Day vs Night)
def accidents_by_user_type_day_night(df):
    usager_cols = {
        'IND_AUTO_CAMION_LEGER': 'Light Vehicles',
        'IND_VEH_LOURD': 'Heavy Vehicles',
        'IND_MOTO_CYCLO': 'Motorcycles',
        'IND_VELO': 'Bicycles',
        'IND_PIETON': 'Pedestrians'
    }

    df[list(usager_cols.keys())] = df[list(usager_cols.keys())].replace({'O': 1, 'N': 0})

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
        title="Number of Accidents by User Type (Day vs Night)",
        xaxis_title="User Type",
        yaxis_title="Number of Accidents",
        updatemenus=[dict(
            type="buttons",
            direction="right",
            buttons=[
                dict(label="Day",
                     method="update",
                     args=[{"visible": [True, False]}, {"title": "Number of Accidents by User Type - Day"}]),
                dict(label="Night",
                     method="update",
                     args=[{"visible": [False, True]}, {"title": "Number of Accidents by User Type - Night"}])
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
        "Dommages matériels seulement": "Material Damage",
        "Dommages matériels inférieurs au seuil de rapportage": "Low Damage"
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
        "Material Damage": "steelblue",
        "Low Damage": "lightgrey"
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
        title="Monthly Accident Severity (Daytime)",
        xaxis_title="Month",
        yaxis_title="Number of Accidents",
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

import pandas as pd
import plotly.graph_objects as go

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
        colorbar=dict(title="Accidents")
    ))

    fig.update_layout(
        title="Severe Accidents by Region and Month (Hover for Details)",
        xaxis_title="Month",
        yaxis_title="Administrative Region",
        width=1200,   
        height=800   
    )

    return fig

import pandas as pd
import plotly.graph_objects as go

# Function to generate a bar chart for accident severity by month, week type, and hour range
def generate_accident_severity_bar_chart(df):
    # Mapping gravité → anglais
    gravite_map = {
        "Léger": "Minor",
        "Mortel ou grave": "Severe",
        "Dommages matériels seulement": "Material Damage",
        "Dommages matériels inférieurs au seuil de rapportage": "Low Damage"
    }

    # Mapping jour/semaine → anglais
    weektype_map = {
        'SEM': 'Weekday',
        'FDS': 'Weekend'
    }

    # Chargement et nettoyage
    df_clean = df.copy()
    df_clean['GRAVITE'] = df_clean['GRAVITE'].map(gravite_map)
    df_clean['JR_SEMN_ACCDN'] = df_clean['JR_SEMN_ACCDN'].map(weektype_map)
    df_clean['MS_ACCDN'] = pd.to_numeric(df_clean['MS_ACCDN'], errors='coerce').astype("Int64")

    # Supprimer les lignes incomplètes
    df_clean = df_clean.dropna(subset=['GRAVITE', 'MS_ACCDN', 'JR_SEMN_ACCDN', 'HR_ACCDN'])

    # Labels d'affichage
    month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    weektype_order = ['Weekday', 'Weekend']
    hour_order = [
        '00:00:00-03:59:00', '04:00:00-07:59:00',
        '08:00:00-11:59:00', '12:00:00-15:59:00',
        '16:00:00-19:59:00', '20:00:00-23:59:00'
    ]

    # Fonction de regroupement
    def get_grouped_data(df, group_col, order_labels):
        grouped = df.groupby([group_col, 'GRAVITE']).size().reset_index(name='Count')
        pivot = grouped.pivot(index=group_col, columns='GRAVITE', values='Count').fillna(0)
        pivot = pivot.reindex(order_labels)
        return pivot

    # Données agrégées
    month_data = get_grouped_data(df_clean, 'MS_ACCDN', list(range(1, 13)))
    month_data.index = month_labels
    weektype_data = get_grouped_data(df_clean, 'JR_SEMN_ACCDN', weektype_order)
    hour_data = get_grouped_data(df_clean, 'HR_ACCDN', hour_order)

    # Couleurs personnalisées
    color_map = {
        "Severe": "darkred",
        "Minor": "lightgreen",
        "Material Damage": "steelblue",
        "Low Damage": "lightgrey"
    }
    gravities = ["Severe", "Minor", "Material Damage", "Low Damage"]

    # Création de la figure
    fig = go.Figure()

    # Traces pour MONTH
    for grav in gravities:
        y = month_data[grav] if grav in month_data else [0] * len(month_data)
        fig.add_trace(go.Bar(
            x=month_data.index,
            y=y,
            name=grav,
            marker_color=color_map.get(grav, 'gray'),
            visible=True
        ))

    # Traces pour WEEK TYPE
    for grav in gravities:
        y = weektype_data[grav] if grav in weektype_data else [0] * len(weektype_data)
        fig.add_trace(go.Bar(
            x=weektype_data.index,
            y=y,
            name=grav,
            marker_color=color_map.get(grav, 'gray'),
            visible=False
        ))

    # Traces pour HOUR RANGE
    for grav in gravities:
        y = hour_data[grav] if grav in hour_data else [0] * len(hour_data)
        fig.add_trace(go.Bar(
            x=hour_data.index,
            y=y,
            name=grav,
            marker_color=color_map.get(grav, 'gray'),
            visible=False
        ))

    # Boutons de sélection
    n = len(gravities)
    buttons = [
        dict(label="By Month",
             method="update",
             args=[{"visible": [True]*n + [False]*n + [False]*n},
                   {"title": "Accident Severity by Month"}]),
        dict(label="By Week Type",
             method="update",
             args=[{"visible": [False]*n + [True]*n + [False]*n},
                   {"title": "Accident Severity by Week Type"}]),
        dict(label="By Hour Range",
             method="update",
             args=[{"visible": [False]*n + [False]*n + [True]*n},
                   {"title": "Accident Severity by Time of Day"}])
    ]

    # Mise en page
    fig.update_layout(
        title="Accident Severity by Month",
        xaxis_title="Time Category",
        yaxis_title="Number of Accidents",
        barmode='stack',
        updatemenus=[dict(
            type="buttons",
            direction="right",
            buttons=buttons,
            showactive=True,
            x=0.6,
            y=1.15
        )],
        hoverlabel=dict(
            bgcolor="white",
            font=dict(color="black")
        )
    )

    return fig


from dash import html, dcc, Output, Input

# Charger les données

from data import get_dataframe

df = get_dataframe("data") 
df.columns = df.columns.str.strip().str.replace('"', '')
df = df.rename(columns=lambda x: x.strip())


# -- Layout principal de la page --
layout = html.Div([
    html.H1("Accident Visualizations Dashboard", style={
        'textAlign': 'center',
        'marginTop': '30px',
        'marginBottom': '40px',
        'color': '#2c3e50'
    }),

    html.Div([
    html.P("This dashboard provides clear, interactive insights into road accident patterns across Quebec. It helps answer key questions like:", style={'marginTop': '20px'}),
    html.Ul([
        html.Li("What types of road users are most frequently involved in road accidents?"),
        html.Li("When and where do the most severe accidents occur?")
    ]),
     html.Details([
            html.Summary("Click to expand full description", style={"cursor": "pointer"}),

  html.H3("Accidents by Road User and Time of Day", style={'marginTop': '40px'}),
    html.P("This bar chart breaks down accidents by user type, segmented into day (08:00–19:59) and night (20:00–07:59)."),
    html.Ul([
        html.Li("Light Vehicles (cars, small trucks)"),
        html.Li("Heavy Vehicles (trucks, buses)"),
        html.Li("Motorcycles"),
        html.Li("Bicycles"),
        html.Li("Pedestrians")
    ]),
    html.P("You can toggle between day and night stats. Hovering over the bars reveals exact accident counts."),

    html.H4("Insights:", style={'marginTop': '20px'}),
    html.P("Light vehicles consistently top the chart during both time frames. Pedestrian and bicycle accidents show noticeable variations between day and night.")
],  open=False)], style={'padding': '30px', 'maxWidth': '900px', 'margin': 'auto'}),


  html.Div([
    dcc.Tabs([
        dcc.Tab(label='Accidents by User Type (Day/Night)', children=[
            html.Div([
                html.H3("Comparison of User Type Involvement in Day vs Night", style={'textAlign': 'center'}),
                dcc.Graph(figure=accidents_by_user_type_day_night(df))
            ], style={'padding': '30px'})
        ]),

        dcc.Tab(label='Severity by Month (Day/Night)', children=[
            html.Div([
                html.H3("Monthly Severity Distribution: Day vs Night", style={'textAlign': 'center'}),
                dcc.Graph(figure=accident_severity_month(df))
            ], style={'padding': '30px'})
        ]),

        dcc.Tab(label='Severe Accidents Heatmap', children=[
            html.Div([
                html.H3("Severe Accidents by Region and Month", style={'textAlign': 'center'}),
                dcc.Graph(figure=generate_severe_accidents_heatmap(df)),

                html.H3(" Heatmap of Severe Accidents by Region and Month", style={'marginTop': '40px'}),
                html.P("This interactive heatmap shows the monthly distribution of severe road accidents across Quebec’s administrative regions. "
                       "Darker red cells indicate more severe accidents. The data is filtered to include only severe cases, and region names are standardized."),
                html.P("When you hover over a cell, you’ll see the region, month, and exact number of accidents."),
                html.P("For example: '142 severe accidents in Montérégie during July'. The layout is fully responsive."),

                html.H4("Insights:", style={'marginTop': '20px'}),
                html.P("Montérégie and Montréal are hotspots, especially from June to October. Winter months (January to March) show significantly lower accident counts.")
            ], style={'padding': '30px'})
        ]),

        dcc.Tab(label='Severity by Month / Week / Hour', children=[
            html.Div([
                html.H3("Severity Breakdown: Monthly, Weekly, and Hourly Views", style={'textAlign': 'center'}),
                dcc.Graph(figure=generate_accident_severity_bar_chart(df))
            ], style={'padding': '30px'})
        ]),
    ])
], style={'width': '95%', 'margin': '0 auto'})
])