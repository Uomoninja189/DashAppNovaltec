from dash import Dash, html
import dash
import dash_bootstrap_components as dbc

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP, "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined"], prevent_initial_callbacks="initial_duplicate")
app.title = "Novaltec Dashboard App"
server = app.server  # per il deploy (es: su Heroku)

app.layout = html.Div(
    [
            dbc.NavbarSimple(
                children=[
                    dbc.NavItem(dbc.NavLink("Home", href="/")),
                    dbc.NavItem(dbc.NavLink("Confronto", href="/confronto")),
                ],
                brand=html.Img(src="/assets/logo.png", height="60px"), 
                brand_href="/", 
                color="#0180c3",  
                dark=True, 
                fluid=True,
            ),
            dbc.Container(dash.page_container, fluid=True, className="p-5"),
        ],
    id="page"
)

