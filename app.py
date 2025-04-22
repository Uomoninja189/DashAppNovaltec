from dash import Dash
import dash
import dash_bootstrap_components as dbc

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "Novaltec Dashboard App"
server = app.server  # per il deploy (es: su Heroku)

app.layout = dbc.Container([
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.NavItem(dbc.NavLink("Confronto", href="/confronto")),
        ],
        brand="Novaltec Dashboard",
        color="primary",
        dark=True,
    ),
    dbc.Container(dash.page_container, fluid=True, className="mt-4"),
], fluid=True)

