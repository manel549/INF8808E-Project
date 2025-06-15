from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pages.dashboard
import pages.polar_grave_surface
import pages.temporal_spatial
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

sidebar = dbc.Nav(
    [
        dbc.NavLink("Accueil", href="/", active="exact"),
        dbc.NavLink("Dashboard", href="/dashboard", active="exact"),
        dbc.NavLink("Accident visualizations", href="/accident_visualizations", active="exact"),
        dbc.NavLink("Road Severity", href="/road_severity", active="exact"),
        dbc.NavLink("BarPolar: Road Surface, Season, and Accident Severity", href="/polar_grave_surface", active="exact"),
        dbc.NavLink("Spatial and temporel", href="/temporal_spatial", active="exact")

    ],
    vertical=True,
    pills=True,
    style={"height": "100vh", "padding": "2rem", "background-color": "#f8f9fa"},
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
        from pages.accident_visualizations import layout as polar_grave_surface_layout
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

if __name__ == "__main__":
    app.run_server(debug=True)
