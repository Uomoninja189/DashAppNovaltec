from dash import html, dcc
from funzioni import *
import dash
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/")



layout = dbc.Container([
    
    dbc.Row([
        dbc.Col([
            html.H1("PAGINA REPORT", className="text-center", style={'fontFamily': 'Roboto, sans-serif', 'marginBottom': '1rem'})
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
                                        id="filtri-header-icon",
                                        className="material-symbols-outlined",
                                    ),
                                ],
                                id="filtri-header-btn",
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
                                            id='upload-data-home',
                                            children=html.Button('Carica File', className='btn btn-primary'),
                                            multiple=False,  # Permette di caricare solo un file
                                        ),
                                        dcc.Store(id='store-data-home')
                                    ], width=4),
                                    dbc.Col([
                                        dbc.Label(
                                                    "Mese",
                                                    html_for="mese",
                                                ),
                                        dcc.Dropdown(
                                            id='month-dropdown',
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
                                        dbc.Label(
                                                    "Agente",
                                                    html_for="agente",
                                                ),
                                        dcc.Dropdown(
                                            id='agente-dropdown',
                                            placeholder="Seleziona...",
                                            style={'fontFamily': 'Roboto, sans-serif'}
                                        )
                                    ], width=4),
                                    dbc.Col([
                                        dbc.Label(
                                                    "Origine",
                                                    html_for="origine",
                                                ),
                                        dcc.Dropdown(
                                            id='origine-dropdown',
                                            placeholder="Seleziona...",
                                            style={'fontFamily': 'Roboto, sans-serif'}
                                        )
                                    ], width=4),
                                    dbc.Col([
                                        dbc.Label(
                                                    "Settore",
                                                    html_for="settore",
                                                ),
                                        dcc.Dropdown(
                                            id='settore-dropdown',
                                            placeholder="Seleziona...",
                                            style={'fontFamily': 'Roboto, sans-serif'}
                                        )
                                    ], width=4)
                                ], className="mb-4"),
                            ])
                        ),
                    id="filtri-collapse",
                    is_open=False,
                    )
                ])
        ),
        id="filtri",
     ),

    dcc.Loading(
        type="circle",
        custom_spinner=html.H2(["Attendi...", dbc.Spinner()]),
        overlay_style={"visibility":"visible", "opacity": .3},
        children=[
        
    

            # Titolo 
            dbc.Row([
                dbc.Col([
                    
                    html.H2(id='titolo-report', className="text-center", style={'fontFamily': 'Roboto, sans-serif'})
                ])
            ]),

            # Grafico a barre + Card Totali
            dbc.Row([
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(
                                id='bar-chart',
                                style={'height': '400px'},
                                config={'displaylogo': False, 'modeBarButtonsToRemove': ['select2d', 'lasso2d']}
                            )))
                ], width=8),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Imponibile", className="card-title"),
                            html.P(id="imponibile-valore", children="0 €", className="card-value text-green")
                        ])
                    ], className="mb-3"),
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Saltato", className="card-title"),
                            html.P(id="saltato-valore", children="0 €", className="card-value text-red")
                        ])
                    ]),
                ], width=4)
            ], className="mb-5"),

            # Torte prima riga
            dbc.Row([
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(
                                id='pie-chart-settori',
                                style={'height': '400px'},
                                config={'displaylogo': False, 'modeBarButtonsToRemove': ['select2d', 'lasso2d']}
                            )))
                ], width=6),
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(
                                id='pie-chart-categorie',
                                style={'height': '400px'},
                                config={'displaylogo': False, 'modeBarButtonsToRemove': ['select2d', 'lasso2d']}
                            )))
                ], width=6)
            ], className="mb-4"),

            # Torte seconda riga
            dbc.Row([
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(
                                id='pie-chart-origine',
                                style={'height': '400px'},
                                config={'displaylogo': False, 'modeBarButtonsToRemove': ['select2d', 'lasso2d']}
                            )))
                ], width=6),
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(
                                id='pie-chart-telem',
                                style={'height': '400px'},
                                config={'displaylogo': False, 'modeBarButtonsToRemove': ['select2d', 'lasso2d']}
                            )))
                ], width=6)
            ])
        ]
    )
], fluid=True, className="mt-4", style={'fontFamily': 'Roboto, sans-serif', 'backgroundColor': '#f5f5f5'})
