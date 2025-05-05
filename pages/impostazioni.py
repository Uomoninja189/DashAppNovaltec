from dash import html, dcc
from funzioni import *
from app import *
import dash
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/impostazioni")

layout = dbc.Container([

    dbc.Row(
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    html.H1("IMPOSTAZIONI", className="text-center", style={'fontFamily': 'Roboto, sans-serif'}),
                    className="p-0 m-0",
                ),
                dbc.CardBody(
                    dbc.Stack([

                        # Dropdown Filtri 1
                        dbc.Row([
                            html.P("PERSONALIZZAZIONE", className="m-0"),
                            dbc.Col([
                                dbc.Label("Palette"),
                                dcc.Dropdown(
                                    id='palette-dropdown-imp',
                                    placeholder="Seleziona...",
                                    multi=False,
                                    searchable=False,
                                    style={'fontFamily': 'Roboto, sans-serif'},
                                    options=['colori1','colori2']
                                )
                            ], width=4),
                            dbc.Col([
                                dbc.Label("X"),
                                dcc.Dropdown(
                                    id='x-dropdown-imp',
                                    placeholder="Seleziona...",
                                    multi=False,
                                    searchable=False,
                                    style={'fontFamily': 'Roboto, sans-serif'}
                                )
                            ], width=4)
                        ], className="mb-3"),

                        # Dropdown Filtri 2
                        dbc.Row([
                            html.P("MODIFICA COLONNE", className="m-0"),
                            dbc.Col([
                                dbc.Label("Colonna Imponibile"),
                                dcc.Input(id="colonna-imponibile-imp", value=colonnaImponibile)
                            ], width=3),
                            dbc.Col([
                                dbc.Label("Colonna Data"),
                                dcc.Input(id="colonna-data-imp", value=colonnaData)
                            ], width=3),
                            dbc.Col([
                                dbc.Label("Colonna Agente"),
                                dcc.Input(id="colonna-agente-imp", value=colonnaAgente)
                            ], width=3),
                            dbc.Col([
                                dbc.Label("Colonna Settore"),
                                dcc.Input(id="colonna-settore-imp", value=colonnaSettore)
                            ], width=3),
                        ], className="mb-4"),

                        # Pulsante Salva
                        dbc.Row(
                            dbc.Col(
                                dbc.Button("Salva modifiche", id="salva-impostazioni-btn", className="w-100", style={"backgroundColor": "#FFC603", "color": "black", "border": "none"}),
                                width=3
                            ),
                            className="mb-3"
                        )
                    ])
                )
            ],className="rounded border mb-3"),
            dbc.Alert(id='salvataggio-status', is_open=False, duration=4000, children="")
        ])
    ),

    dbc.Row(
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    html.H1("SELEZIONE FILE", className="text-center", style={'fontFamily': 'Roboto, sans-serif'}),
                    className="p-0 m-0",
                ),
                dbc.CardBody(
                    dbc.Stack([
                        dbc.Row([
                            dbc.Col(
                                dcc.Upload(
                                            id='upload-data-imp',
                                            children=html.Button('Carica File', className='btn btn-primary'),
                                            multiple=False
                                        ),
                            ),
                            dbc.Col([
                                html.Ul(id='lista-file-imp', children=[])
                            ]
                            )
                        ])
                      
                    ])
                )
            ],className="rounded border mb-3"),
        ])
    )
], fluid=True, className="mt-4", style={'fontFamily': 'Roboto, sans-serif', 'backgroundColor': '#f5f5f5'})


