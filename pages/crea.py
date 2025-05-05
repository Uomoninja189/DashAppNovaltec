from dash import html, dcc
from funzioni import *
from app import *
import dash
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/crea")



layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("CREA IL TUO GRAFICO", className="text-center", style={'fontFamily': 'Roboto, sans-serif', 'marginBottom': '1rem'})
        ])
    ]),

    dbc.Row(
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader(
                        [
                            dbc.Button(
                                [
                                    html.P("Filtri", className="m-0"),
                                    html.Span(
                                        "keyboard_arrow_down",
                                        id="filtri-header-icon-crea",
                                        className="material-symbols-outlined",
                                    ),
                                ],
                                id="filtri-header-btn-crea",
                                className="w-100 p-3 d-flex justify-content-between",
                                color="light",
                                n_clicks=0,
                            ),
                        ],
                        className="p-0 m-0",
                    ),
                    dbc.Collapse(
                        dbc.CardBody(
                            dbc.Stack([

                                # Dropdown Filtri 1
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label(
                                                    "Anno",
                                                    html_for="anno",
                                                ),
                                        dcc.Upload(
                                            id='upload-data-crea',
                                            children=html.Button('Carica File', className='btn btn-primary'),
                                            multiple=False,  # Permette di caricare solo un file
                                        ),
                                        dcc.Store(id='store-data-crea')
                                    ], width=4),
                                    dbc.Col([
                                        dbc.Label(
                                                    "Mese",
                                                    html_for="mese",
                                                ),
                                        dcc.Dropdown(
                                            id='month-dropdown-crea',
                                            placeholder="Seleziona...",
                                            multi=True,
                                            searchable=False,
                                            style={'fontFamily': 'Roboto, sans-serif'}
                                        )
                                    ], width=4)
                                ], className="mb-3"),

                                # Dropdown Filtri 2
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("X del grafico"),
                                        dcc.Dropdown(
                                            id='x-dropdown-crea',
                                            placeholder="Seleziona...",
                                            style={'fontFamily': 'Roboto, sans-serif'}
                                        )
                                    ], width=4),
                                    dbc.Col([
                                        dbc.Label("Y del grafico",),
                                        dcc.Dropdown(
                                            id='y-dropdown-crea',
                                            placeholder="Seleziona...",
                                            style={'fontFamily': 'Roboto, sans-serif'}
                                        )
                                    ], width=4),
                                    dbc.Col([
                                        dbc.Label("Tipo di grafico"),
                                        dcc.Dropdown(
                                            id='tipo-dropdown-crea',
                                            placeholder="Seleziona...",
                                            style={'fontFamily': 'Roboto, sans-serif'},
                                            options=["Barre orizzontali", "Barre verticali", "Torta"]
                                        )
                                    ], width=4)
                                ], className="mb-4"),
                            ])
                        ),
                    id="filtri-collapse-crea",
                    is_open=False,
                    )
                ],className="rounded border mb-3")
        ),
        id="filtri",
     ),
     dbc.Row([
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(
                                id='chart-crea',
                                config={
                                    'displaylogo': False,
                                    'modeBarButtonsToRemove': ['select2d', 'lasso2d']
                                }
                            )))
                ])
            ]),
    ], fluid=True, className="mt-4", style={'fontFamily': 'Roboto, sans-serif', 'backgroundColor': '#f5f5f5'})