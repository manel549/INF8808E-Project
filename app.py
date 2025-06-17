from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pages.dashboard
import pages.polar_grave_surface
import pages.temporal_spatial
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
import dash_bootstrap_components as dbc


import plotly.io as pio

# Définir le thème global, par exemple 'plotly_dark' ou 'ggplot2'
pio.templates.default = "seaborn"



sidebar = dbc.Nav(
    [
        html.H2("Menu", className="sidebar-title", style={"paddingBottom": "1rem", "color": "#2c3e50"}),
        dbc.NavLink("Home", href="/", active="exact", className="sidebar-link"),
        dbc.NavLink("Dashboard", href="/dashboard", active="exact", className="sidebar-link"),
        dbc.NavLink("Accident Visualizations", href="/accident_visualizations", active="exact", className="sidebar-link"),
        dbc.NavLink("Road Severity", href="/road_severity", active="exact", className="sidebar-link"),
        dbc.NavLink("BarPolar: Road Surface, Season, and Accident Severity", href="/polar_grave_surface", active="exact", className="sidebar-link"),
         dbc.NavLink("Spatial and temporel", href="/temporal_spatial", active="exact", className="sidebar-link")
    ],
    vertical=True,
    pills=True,
    style={
        "position": "fixed",
        "top": 0,
        "left": 0,
        "height": "100vh",
        "width": "250px",
        "padding": "2rem 1.5rem",
        "background-color": "#f0f2f5",
        "box-shadow": "2px 0 5px rgba(0,0,0,0.1)",
        "overflowY": "auto",
        "zIndex": "1000",
    },
)




app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(sidebar, width=2),
        dbc.Col([
            dcc.Location(id="url"),
            html.Div(id="page-content")
        ], width=10)
    ])
], fluid=True)

@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def render_page_content(pathname):
    if pathname == "/":
        from pages.home import layout as home_layout
        return home_layout
    elif pathname == "/dashboard":
        return pages.dashboard.layout
    elif pathname == "/road_severity":
        from pages.road_severity import layout as road_severity_layout
        return road_severity_layout
    elif pathname == "/accident_visualizations":
        from pages.accident_visualizations import layout as accident_visualizations_layout
        return accident_visualizations_layout
    elif pathname == "/polar_grave_surface":
        from pages.polar_grave_surface import layout as polar_grave_surface_layout
        return polar_grave_surface_layout
    elif pathname == "/temporal_spatial":
        pages.temporal_spatial.register_callbacks(app)
        return pages.temporal_spatial.layout

    return dbc.Container([
        html.H1("404: Page non trouvée", className="text-danger"),
        html.Hr(),
        html.P(f"Désolé, la page {pathname} n'existe pas."),
    ])
    
pages.temporal_spatial.register_callbacks(app)

server = app.server 
if __name__ == "__main__":
    app.run(debug=True, port=8050)
    
