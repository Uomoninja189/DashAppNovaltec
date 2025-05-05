import os
from dash import Dash, html
import dash, json
import dash_bootstrap_components as dbc
from dash import dcc

impostazioni_path = "assets/impostazioni.json"

with open(impostazioni_path, "r") as f:
    impostazioni = json.load(f)

# Assegna alle variabili che usi nel layout
colonnaData = impostazioni.get("colonnaData", "")
colonnaSettore = impostazioni.get("colonnaSettore", "")
colonnaAgente = impostazioni.get("colonnaAgente", "")
colonnaImponibile = impostazioni.get("colonnaImponibile", "")

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.BOOTSTRAP, "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined"], prevent_initial_callbacks="initial_duplicate")
app.title = "Novaltec Dashboard App"
server = app.server  # per il deploy (es: su Heroku)

app.layout = html.Div(
    [    
        dcc.Store(id='store-file-lista', storage_type='local'),   

        dbc.NavbarSimple(
            children=[
                dbc.NavItem(dbc.NavLink("Report", href="/")),
                dbc.NavItem(dbc.NavLink("Confronto", href="/confronto")),
                dbc.NavItem(dbc.NavLink("Crea", href="/crea")),
                dbc.NavItem(dbc.NavLink("Impostazioni", href="/impostazioni"))

            ],
            brand=html.Img(src="/assets/logo.png", height="60px"), 
            brand_href="/", 
            color="#0180c3",  
            dark=True, 
            fluid=True,
        ),
        dcc.Interval(id='interval-trigger-initial-load', interval=2, max_intervals=1),
        dcc.Location(id='url', refresh=False),
        dbc.Container(dash.page_container, fluid=True, className="p-5"),
    ],
    id="page"
)

