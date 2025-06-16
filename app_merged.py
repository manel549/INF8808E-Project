import dash
from dash import dcc, html
from dash import dcc, html
import pandas as pd
import map_chart
import bar_chart
from template import create_template
from Rihem import create_sankey_chart  # Import Sankey chart function
from Arnaud import accidents_by_user_type_day_night, accident_severity_month, generate_severe_accidents_heatmap, generate_accident_severity_bar_chart

# Initialize Dash app
app = dash.Dash(__name__)
app.title = 'Quebec Road Accidents'


# Function to load and clean accident data
def prep_data():
    df = pd.read_csv(r'C:\Users\RBerbere\Downloads\code (1) - Copie\code\src\data_fusionnee.csv')
    df.columns = df.columns.str.strip().str.replace('"', '').str.replace('\t', '')
    return df


# Function to initialize layout with graphs
def init_app_layout(fig_bar, fig_map, fig_sankey, fig_user_type, fig_severity_month, fig_heatmap, fig_severity_bar):
    return html.Div(className='content', children=[
        html.Header([ 
            html.H1('Quebec Road Accidents')
        ]),
        html.Main(children=[ 
            html.Div(className='viz-container', children=[ 
                html.H2("Accidents by Year and Severity"), 
                dcc.Graph( 
                    figure=fig_bar, 
                    config=dict(scrollZoom=False), 
                    className='graph', 
                    id='bar-chart' 
                ) 
            ]), 
            html.Div(className='viz-container', children=[ 
                html.H2("Accidents by Region"), 
                dcc.Graph( 
                    figure=fig_map, 
                    config=dict(scrollZoom=True), 
                    className='graph', 
                    id='accident-map' 
                ) 
            ]), 
            html.Div(className='viz-container', children=[ 
                html.H2("Accident Severity by Road Conditions"), 
                dcc.Graph( 
                    figure=fig_sankey, 
                    config=dict(scrollZoom=True), 
                    className='graph', 
                    id='sankey-chart' 
                ) 
            ]), 
            # Adding the new visualizations to the layout
            html.Div(className='viz-container', children=[ 
                html.H2("Accidents by User Type (Day vs Night)"), 
                dcc.Graph( 
                    figure=fig_user_type, 
                    config=dict(scrollZoom=False), 
                    className='graph', 
                    id='user-type-accidents' 
                ) 
            ]),
            html.Div(className='viz-container', children=[ 
                html.H2("Accident Severity by Month"), 
                dcc.Graph( 
                    figure=fig_severity_month, 
                    config=dict(scrollZoom=True), 
                    className='graph', 
                    id='severity-month-accidents' 
                ) 
            ]),
            html.Div(className='viz-container', children=[ 
                html.H2("Severe Accidents by Region and Month"), 
                dcc.Graph( 
                    figure=fig_heatmap, 
                    config=dict(scrollZoom=True), 
                    className='graph', 
                    id='heatmap-accidents' 
                ) 
            ]),
            html.Div(className='viz-container', children=[ 
                html.H2("Accident Severity by Month, Week, and Hour Range"), 
                dcc.Graph( 
                    figure=fig_severity_bar, 
                    config=dict(scrollZoom=True), 
                    className='graph', 
                    id='severity-bar-accidents' 
                ) 
            ])
        ]) 
    ])

create_template()

# Load and prepare data
df = prep_data()

# Create the bar chart using the bar_chart module
fig_bar = bar_chart.init_figure()
fig_bar = bar_chart.draw(fig_bar, df, mode='count', time_col='AN', type_col='GRAVITE')

# Prepare the map
df_map = map_chart.prepare_region_data()
fig_map = map_chart.draw_geo_map(df_map)

# Create the Sankey chart by calling the function from Rihem.py
fig_sankey = create_sankey_chart(df)

# Create the new visualizations using the Arnaud functions
fig_user_type = accidents_by_user_type_day_night(df)
fig_severity_month = accident_severity_month(df)

# Generate heatmap and severity bar chart using the functions from Arnaud
fig_heatmap = generate_severe_accidents_heatmap(df)
fig_severity_bar = generate_accident_severity_bar_chart(df)

# Set layout
app.layout = init_app_layout(fig_bar, fig_map, fig_sankey, fig_user_type, fig_severity_month, fig_heatmap, fig_severity_bar)

if __name__ == '__main__':
    app.run(debug=True)
