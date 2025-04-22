from dash import html, dcc
from funzioni import *
import dash


dash.register_page(__name__, path="/confronto")

indici = ['primo', 'secondo', 'terzo']

layout = layout_base([
        
        html.H1(children='PAGINA CONFRONTO', style={'fontFamily': 'Roboto, sans-serif', 'marginBottom': '1rem', 'textAlign' : 'center'}),


        html.Br(),
        html.Div([
                        dcc.Dropdown(
                            id='dropdown-settore-confronto',
                            placeholder="Seleziona un Settore",
                            style={'width': '80%', 'marginBottom': '1em', 'fontFamily': 'Roboto, sans-serif'},
                            value=None,
                            #options=[{'label': settore, 'value': settore} for settore in carica_settori()],
                            searchable=False
                        ),
                        dcc.Dropdown(
                            id='dropdown-agente-confronto',
                            placeholder="Seleziona un Agente",
                            style={'width': '80%', 'marginBottom': '1em', 'fontFamily': 'Roboto, sans-serif'},
                            value=None
                        ),
                        dcc.Dropdown(
                            id='dropdown-origine-confronto',
                            placeholder="Seleziona un Origine",
                            style={'width': '80%', 'marginBottom': '1em', 'fontFamily': 'Roboto, sans-serif'},
                            value=None
                        ),
                        dcc.Dropdown(
                            id='dropdown-cateogoria-confronto',
                            placeholder="Seleziona una Categoria",
                            style={'width': '80%', 'marginBottom': '1em', 'fontFamily': 'Roboto, sans-serif'},
                            value=None
                        ),
                    ], className="row-container"
                ),
        # Contenitore per i filtri
        html.Div(
            [
                html.Div([
                    dcc.Dropdown(
                        id={"type": "anno-dropdown", "index": idx},
                        options=[{'label': anno, 'value': anno} for anno in carica_anni()],
                        placeholder="Seleziona un anno",
                        style={'width': '100%', 'marginBottom': '1em', 'fontFamily': 'Roboto, sans-serif'},
                        searchable=False
                    ),
                    dcc.Store(id={"type": "anno-data", "index": idx})
                ], style={'width': '32%'})  # stile opzionale per disporre 3 colonne
                for idx in indici
            ], className="row-container"
        ),

        html.H2(id='titolo-report', style={'fontFamily': 'Roboto, sans-serif', 'marginBottom': '1rem', 'textAlign' : 'center'}),
        html.Div([

            
            html.Div([
            html.H4(id={"type": "titolo", "index": idx}, className="card-title"),
            html.P(id={"type": "valore", "index": idx}, children="0 €", className="card-value text-green")
            ], className="card-container")
            for idx in indici



            ],className="row-container"),
        
         
            
            html.Div([
                dcc.Graph(
                    id='bar-chart-confronto',
                    style={'width': '100%', 'height': '400px'}, 
                    config={
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['select2d', 'lasso2d']
                    }
                ),
            ], className="row-container"),
            html.Div([
                dcc.Graph(
                    id='bar-chart-settore-confronto',
                    style={'width': '50%', 'height': '400px'}, 
                    config={
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['select2d', 'lasso2d']
                    }
                ),
                dcc.Graph(
                    id='bar-chart-categoria-confronto',
                    style={'width': '50%', 'height': '400px'}, 
                    config={
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['select2d', 'lasso2d']
                    }
                ),
            ], className="row-container"),
            
            html.Div([
                dcc.Graph(
                    id='pie-chart-settore-confronto-primo',
                    style={'width': '30%', 'height': '400px'},  # Applica direttamente le dimensioni
                    config={
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['select2d', 'lasso2d']
                    }
                ),
                dcc.Graph(
                    id='pie-chart-settore-confronto-secondo',
                    style={'width': '30%', 'height': '400px'},  # Applica direttamente le dimensioni
                    config={
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['select2d', 'lasso2d']
                    }
                ),
                dcc.Graph(
                    id='pie-chart-settore-confronto-terzo',
                    style={'width': '30%', 'height': '400px'},  # Applica direttamente le dimensioni
                    config={
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['select2d', 'lasso2d']
                    }
                ),
            ], className="row-container"
        ),
    ]
)