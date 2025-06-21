import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from dash import html, dcc
from template import COLOR_PALETTE, GRAVITY_TRANSLATION
from data import get_dataframe

pio.renderers.default = 'browser'


from data import get_dataframe


# Charger et nettoyer les données
COLUMNS = "CD_CATEG_ROUTE, CD_CONFG_ROUTE, GRAVITE"
df = get_dataframe("data", cols=COLUMNS)
df.columns = df.columns.str.strip().str.replace('"', '')
df = df.rename(columns=lambda x: x.strip())

df['GRAVITE'] = df['GRAVITE'].map(GRAVITY_TRANSLATION)


# Agrégation pour histogrammes
route_severity = df.groupby(['CD_CATEG_ROUTE', 'GRAVITE']).size().reset_index(name='Count')
config_severity = df.groupby(['CD_CONFG_ROUTE', 'GRAVITE']).size().reset_index(name='Count')
severity_order = df['GRAVITE'].unique().tolist()

fig = go.Figure()
for severity in severity_order:
    filtered = route_severity[route_severity['GRAVITE'] == severity]
    fig.add_trace(go.Bar(x=filtered['CD_CATEG_ROUTE'], y=filtered['Count'], name=severity, visible=True))
for severity in severity_order:
    filtered = config_severity[config_severity['GRAVITE'] == severity]
    fig.add_trace(go.Bar(x=filtered['CD_CONFG_ROUTE'], y=filtered['Count'], name=severity, visible=False))

def create_sankey_chart(df):
    road_categories = list(df['CD_CATEG_ROUTE'].unique())
    road_configs = list(df['CD_CONFG_ROUTE'].unique())
    severities = df['GRAVITE'].unique().tolist()

    nodes = road_categories + road_configs + severities
    label_to_index = {label: i for i, label in enumerate(nodes)}

    flows_cat_sev = df.groupby(['CD_CATEG_ROUTE', 'GRAVITE']).size().reset_index(name='count')
    flows_conf_sev = df.groupby(['CD_CONFG_ROUTE', 'GRAVITE']).size().reset_index(name='count')

    source, target, value, link_colors = [], [], [], []

    # Road category → gravity
    for _, row in flows_cat_sev.iterrows():
        source.append(label_to_index[row['CD_CATEG_ROUTE']])
        target.append(label_to_index[row['GRAVITE']])
        value.append(row['count'])
        link_colors.append(COLOR_PALETTE.get(row['GRAVITE'], '#999999'))

    # Road config → gravity
    offset = len(road_categories)
    for _, row in flows_conf_sev.iterrows():
        source.append(offset + road_configs.index(row['CD_CONFG_ROUTE']))
        target.append(label_to_index[row['GRAVITE']])
        value.append(row['count'])
        link_colors.append(COLOR_PALETTE.get(row['GRAVITE'], '#999999'))

    fig_sankey = go.Figure()

    fig_sankey.add_trace(go.Sankey(
    node=dict(
        label=nodes,
        pad=15,
        thickness=20,
        color=[COLOR_PALETTE.get(label, '#cccccc') for label in nodes] 
    ),
    link=dict(
        source=source[:len(flows_cat_sev)],
        target=target[:len(flows_cat_sev)],
        value=value[:len(flows_cat_sev)],
        color=link_colors[:len(flows_cat_sev)]
    ),
    domain=dict(x=[0, 0.48], y=[0, 1]),
    visible=True,
    name='Road Category to Severity'
))


    fig_sankey.add_trace(go.Sankey(
         node=dict(
        label=nodes,
        pad=15,
        thickness=20,
        color=[COLOR_PALETTE.get(label, '#cccccc') for label in nodes] 
    ),
        link=dict(
            source=source[len(flows_cat_sev):],
            target=target[len(flows_cat_sev):],
            value=value[len(flows_cat_sev):],
            color=link_colors[len(flows_cat_sev):]
        ),
        domain=dict(x=[0.52, 1], y=[0, 1]),
        visible=False,
        name='Road Config to Severity'
    ))

    fig_sankey.update_layout(
        title="",
        updatemenus=[dict(
            type="buttons", direction="right",
            buttons=[
                dict(label="Road Category", method="update", args=[{"visible": [True, False]}, {"title": "Accident Severity: Road Category → Severity"}]),
                dict(label="Road Configuration", method="update", args=[{"visible": [False, True]}, {"title": "Accident Severity: Road Configuration → Severity"}])
            ],
            x=0.5, xanchor="center", y=1.1, yanchor="top"
        )],
        template="plotly_white",
        height=600,
        width=900
    )

    return fig_sankey

layout = html.Div([
    html.H2("Road accident severity", style={
        'textAlign': 'center', 'marginTop': '30px', 'marginBottom': '30px',
        'fontSize': '34px', 'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif", 'color': '#2c3e50'
    }),

    html.P("This visualization answers the following target questions:", style={
        'textAlign': 'left', 'fontSize': '18px', 'maxWidth': '900px', 'color': '#2c3e50',
        'marginLeft': 'auto', 'marginRight': 'auto', 'marginBottom': '5px'
    }),
    html.Ul([
        html.Li("Are accidents more severe on certain types of roads?", style={'textAlign': 'left', 'fontSize': '18px', 'maxWidth': '900px', 'color': '#2c3e50'}),
        html.Li("Are severe accidents more likely based on road configuration (e.g., curves, intersections)?", style={'textAlign': 'left', 'fontSize': '18px', 'maxWidth': '900px', 'color': '#2c3e50'})
    ]),

    html.H3("Description", style={
        'textAlign': 'center', 'marginTop': '80px', 'marginBottom': '30px',
        'fontSize': '34px', 'fontFamily': "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif", 'color': '#2c3e50'
    }),
    html.P("This Sankey diagram clearly represents the flow and distribution of accident severity "
           "across two dimensions: Road Category (such as public road, off public road, other) and Road Configuration "
           "(including one way, two way, separated by median, other). By visualizing these flows, "
           "the diagram reveals how accidents are spread with respect to severity and road characteristics.", style={
               'textAlign': 'center', 'fontSize': '18px', 'maxWidth': '900px', 'color': '#2c3e50',
               'marginLeft': 'auto', 'marginRight': 'auto'
           }),

    dcc.Graph(figure=create_sankey_chart(df))
], style={"width": "80%", "margin": "0 auto", "marginBottom": "40px", "lineHeight": "1.6"})
