import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from dash import html, dcc
pio.renderers.default = 'browser'




# Load and clean data
df = pd.read_csv('assets/data_fusionnee.csv')
df.columns = df.columns.str.strip().str.replace('"', '').str.replace('\t', '')


# Aggregate data
route_severity = df.groupby(['CD_CATEG_ROUTE', 'GRAVITE']).size().reset_index(name='Count')
config_severity = df.groupby(['CD_CONFG_ROUTE', 'GRAVITE']).size().reset_index(name='Count')

# Ensure that severity_order includes all unique values from the 'GRAVITE' column
severity_order = df['GRAVITE'].unique().tolist()


# Create a figure 
fig = go.Figure()

# Add traces for road categories (visible by default)
for severity in severity_order:
    filtered = route_severity[route_severity['GRAVITE'] == severity]
    fig.add_trace(go.Bar(
        x=filtered['CD_CATEG_ROUTE'],
        y=filtered['Count'],
        name=severity,
        visible=True
    ))

# Add traces for road configuration (invisible by default)
for severity in severity_order:
    filtered = config_severity[config_severity['GRAVITE'] == severity]
    fig.add_trace(go.Bar(
        x=filtered['CD_CONFG_ROUTE'],
        y=filtered['Count'],
        name=severity,
        visible=False
    ))

# Total number of traces for each severity group
n_severity = len(severity_order)


# Prepare nodes and links for Sankey
road_categories = list(df['CD_CATEG_ROUTE'].unique())
road_configs = list(df['CD_CONFG_ROUTE'].unique())
severities = severity_order

# Create nodes list for Sankey (all unique labels)
nodes = road_categories + road_configs + severities

# Map label to index (ensure all labels are accounted for)
label_to_index = {label: i for i, label in enumerate(nodes)}

# Aggregate flows: from road category to severity
flows_cat_sev = df.groupby(['CD_CATEG_ROUTE', 'GRAVITE']).size().reset_index(name='count')

# Aggregate flows: from road config to severity
flows_conf_sev = df.groupby(['CD_CONFG_ROUTE', 'GRAVITE']).size().reset_index(name='count')

# Build source, target, value lists
source = []
target = []
value = []

# plotting.py

def create_sankey_chart(df):
    # Prepare nodes and links for Sankey
    road_categories = list(df['CD_CATEG_ROUTE'].unique())
    road_configs = list(df['CD_CONFG_ROUTE'].unique())
    severities = df['GRAVITE'].unique().tolist()

    # Create nodes list for Sankey (all unique labels)
    nodes = road_categories + road_configs + severities

    # Map label to index (ensure all labels are accounted for)
    label_to_index = {label: i for i, label in enumerate(nodes)}

    # Aggregate flows: from road category to severity
    flows_cat_sev = df.groupby(['CD_CATEG_ROUTE', 'GRAVITE']).size().reset_index(name='count')

    # Aggregate flows: from road config to severity
    flows_conf_sev = df.groupby(['CD_CONFG_ROUTE', 'GRAVITE']).size().reset_index(name='count')

    # Build source, target, value lists
    source = []
    target = []
    value = []

    # Road category → severity
    for _, row in flows_cat_sev.iterrows():
        source.append(label_to_index[row['CD_CATEG_ROUTE']])
        target.append(label_to_index[row['GRAVITE']])
        value.append(row['count'])

    # Road config → severity (shift indices by len(road_categories))
    offset = len(road_categories)
    for _, row in flows_conf_sev.iterrows():
        source.append(offset + road_configs.index(row['CD_CONFG_ROUTE']))
        target.append(label_to_index[row['GRAVITE']])
        value.append(row['count'])

    # Create Sankey diagram figure
    fig_sankey = go.Figure()

    # Trace 1: Road Category to Severity (first half)
    fig_sankey.add_trace(go.Sankey(
        node=dict(label=nodes, pad=15, thickness=20),
        link=dict(source=source[:len(flows_cat_sev)],
                  target=target[:len(flows_cat_sev)],
                  value=value[:len(flows_cat_sev)]),
        domain=dict(x=[0, 0.48], y=[0, 1]),
        visible=True,
        name='Road Category to Severity'
    ))

    # Trace 2: Road Config to Severity (second half)
    fig_sankey.add_trace(go.Sankey(
        node=dict(label=nodes, pad=15, thickness=20),
        link=dict(source=source[len(flows_cat_sev):],
                  target=target[len(flows_cat_sev):],
                  value=value[len(flows_cat_sev):]),
        domain=dict(x=[0.52, 1], y=[0, 1]),
        visible=False,
        name='Road Config to Severity'
    ))

    buttons = [
        dict(label="Road Category",
             method="update",
             args=[{"visible": [True, False]}, {"title": "Accident Severity: Road Category → Severity"}]),
        dict(label="Road Configuration",
             method="update",
             args=[{"visible": [False, True]}, {"title": "Accident Severity: Road Configuration → Severity"}])
    ]

    fig_sankey.update_layout(
        title="Sankey Diagram",
        updatemenus=[dict(type="buttons", buttons=buttons, x=0.5, xanchor="center", y=1.1, yanchor="top")],
        template="plotly_white",
        height=600,
        width=900
    )

    return fig_sankey

layout = html.Div([
    html.H2("Road Accident Severity"),
  
    html.P("This visualization answers the following target questions:"),
    html.Ul([
        html.Li("Are accidents more severe on certain types of roads?"),
        html.Li("Are severe accidents more likely based on road configuration (e.g., curves, intersections)?"),
    ]),

    html.H3("Description"),
    html.P("This Sankey diagram clearly represents the flow and distribution of accident severity "
           "across two dimensions: Road Category (such as public road, off public road, other) and Road Configuration "
           "(including one way, two way, separated by median, other). By visualizing these flows, "
           "the diagram reveals how accidents are spread with respect to severity and road characteristics."),

dcc.Graph(figure=create_sankey_chart(df))
    
], style={"width": "80%", "margin": "0 auto", "marginBottom": "40px", "lineHeight": "1.6"})

