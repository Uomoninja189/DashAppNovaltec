from dash import html, dcc, dash_table 
from funzioni import *
import dash
import dash_bootstrap_components as dbc


dash.register_page(__name__, path="/confronto")

indici = ['primo', 'secondo', 'terzo']

layout = dbc.Container([    
    html.H1(
        children='PAGINA CONFRONTO',
        style={'fontFamily': 'Roboto, sans-serif', 'marginBottom': '1rem', 'textAlign': 'center'}
    ),


    # Filtri dropdown iniziali
    # Nuova sezione Filtri (adattata come il primo)
    dbc.Row(
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader(
                        dbc.Button(
                            [
                                html.P("Filtri", className="m-0"),
                                html.Span(
                                    "keyboard_arrow_down",
                                    id="filtri-confronto-header-icon",
                                    className="material-symbols-outlined",
                                ),
                            ],
                            id="filtri-confronto-header-btn",
                            className="w-100 p-3 d-flex justify-content-between",
                            color="light",
                            n_clicks=0,
                        ),
                        className="p-0 m-0",
                    ),
                    dbc.Collapse(
                        dbc.CardBody(
                            dbc.Stack([
                                # Prima riga di filtri
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Mese", html_for="dropdown-mese-confronto"),
                                        dcc.Dropdown(
                                            id='dropdown-mese-confronto',
                                            placeholder="Seleziona un mese",
                                            style={'fontFamily': 'Roboto, sans-serif'},
                                            value=None, multi=True
                                        )
                                    ], width=4),
                                    dbc.Col([
                                        dbc.Label("Settore", html_for="dropdown-settore-confronto"),
                                        dcc.Dropdown(
                                            id='dropdown-settore-confronto',
                                            placeholder="Seleziona un Settore",
                                            style={'fontFamily': 'Roboto, sans-serif'},
                                            value=None, searchable=False
                                        )
                                    ], width=4),
                                ], className="mb-3"),
                                
                                # Seconda riga di filtri
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label("Agente", html_for="dropdown-agente-confronto"),
                                        dcc.Dropdown(
                                            id='dropdown-agente-confronto',
                                            placeholder="Seleziona un Agente",
                                            style={'fontFamily': 'Roboto, sans-serif'},
                                            value=None
                                        )
                                    ], width=4),
                                    dbc.Col([
                                        dbc.Label("Origine", html_for="dropdown-origine-confronto"),
                                        dcc.Dropdown(
                                            id='dropdown-origine-confronto',
                                            placeholder="Seleziona un Origine",
                                            style={'fontFamily': 'Roboto, sans-serif'},
                                            value=None
                                        )
                                    ], width=4),
                                    dbc.Col([
                                        dbc.Label("Categoria", html_for="dropdown-categoria-confronto"),
                                        dcc.Dropdown(
                                            id='dropdown-categoria-confronto',
                                            placeholder="Seleziona una Categoria",
                                            style={'fontFamily': 'Roboto, sans-serif'},
                                            value=None
                                        )
                                    ], width=4),
                                ], className="mb-3"),

                                html.Br(),html.Br(),

                                # Upload file invece dei Dropdown Anni
                                dbc.Row([
                                    dbc.Col([
                                        dbc.Label(f"Anno {idx}"),
                                        dcc.Dropdown(
                                            id={"type": "anno-dropdown", "index": idx},
                                            options=[{'label': anno, 'value': anno} for anno in carica_anni()],
                                            placeholder="Seleziona...",
                                            style={'marginBottom': '1em', 'fontFamily': 'Roboto, sans-serif'},
                                            searchable=False
                                        ),
                                        dcc.Store(id={"type": "anno-data", "index": idx})
                                    ], width=4) for idx in indici
                                ]),
                            ])
                        ),
                        id="filtri-confronto-collapse",
                        is_open=False,
                    )
                ],
                className="shadow-sm rounded border mb-3"
            )
        )
    ),


    dcc.Loading(
        type="circle",
        custom_spinner=html.H2(["Attendi...", dbc.Spinner()]),
        overlay_style={"visibility":"visible", "opacity": .3},
        children=[

            html.H2(id='titolo-report', style={
                'fontFamily': 'Roboto, sans-serif',
                'marginBottom': '1rem',
                'textAlign': 'center'
            }),

            # Cards per ogni indice
            dbc.Row([
                dbc.Col(
                        dbc.Card(
                            dbc.CardBody([
                                html.H4(id={"type": "titolo", "index": idx}, className="card-title"),
                                html.P(id={"type": "valore", "index": idx}, children="0 €", className="card-value text-green fw-bold"),
                                html.P(id={"type": "saltato", "index": idx}, children="", className="card-variazione text-red text-center"),
                            ]),
                        ),
                        width=4
                    )
                    for idx in indici
            ]),
            html.Br(),
            # Bar chart
            dbc.Row([
                dbc.Col([
                    dbc.Card(
                        dbc.CardBody(
                            dcc.Graph(
                                id='bar-chart-confronto',
                                style={'width': '100%', 'height': '400px'},
                                config={
                                    'displaylogo': False,
                                    'modeBarButtonsToRemove': ['select2d', 'lasso2d']
                                }
                            )))
                ])
            ]),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    dbc.Button("Tabella Settore", id="btn-settore", className="btn btn-primary"),
                ]),
                dbc.Col([
                    dbc.Button("Tabella Categoria", id="btn-categoria", className="btn btn-primary"),
                ]),
                dbc.Col([
                    dbc.Button("Tabella Origine", id="btn-origine", className="btn btn-primary"),
                ]),

            ]),

            # Tabelle dinamiche
            dbc.Row([
                dbc.Col([
                    dcc.Store(id='store-tabella-settore'),
                    dcc.Store(id='store-tabella-origine'),
                    dcc.Store(id='store-tabella-categoria'),
                    dash_table.DataTable(
                        id='tabella-dinamica-confronto',
                        columns=[{'name': 'Colonna', 'id': 'colonna'}],
                        data=[],
                        active_cell={'row': 0, 'column': 0, 'column_id': 'colonna', 'row_id': 0},
                        style_data_conditional=[
                            {'if': {'row_index': 'odd'}, 'backgroundColor': '#f5f5f5'},
                            {'if': {'column_type': 'numeric'}, 'textAlign': 'right'},
                            {'if': {'column_id': colonnaSettore}, 'textAlign': 'left'},
                            {'if': {'state': 'active'}, 'backgroundColor': 'transparent', 'border': 'none'}
                        ],
                    )
                ]),
            ])
        ]
    )
], fluid=True, className="mt-4", style={
    'fontFamily': 'Roboto, sans-serif',
    'marginBottom': '1em',
    'width': '100%',
    'backgroundColor': '#f5f5f5'
})
