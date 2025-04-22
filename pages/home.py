from dash import html, dcc
from funzioni import *
import dash


dash.register_page(__name__, path="/")


layout = layout_base([
        
                html.H1(children='PAGINA REPORT', style={'fontFamily': 'Roboto, sans-serif', 'marginBottom': '1rem', 'textAlign' : 'center'}),

                # Contenitore per i filtri
                html.Div([
                        dcc.Dropdown(
                            id='anno-dropdown',
                            options=[{'label': anno, 'value': anno} for anno in carica_anni()],
                            placeholder="Seleziona un anno",
                            style={'width': '80%', 'marginBottom': '1em', 'fontFamily': 'Roboto, sans-serif'}
                        ),
                        dcc.Dropdown(
                            id='month-dropdown',
                            placeholder="Seleziona un mese",
                            style={'width': '80%', 'marginBottom': '1em', 'fontFamily': 'Roboto, sans-serif'},
                            value=None,
                            multi=True,
                            searchable=False
                        ),
                        dcc.Dropdown(
                            id='agente-dropdown',
                            placeholder="Seleziona un Agente",
                            style={'width': '80%', 'marginBottom': '1em', 'fontFamily': 'Roboto, sans-serif'},
                            value=None
                        ),
                        dcc.Dropdown(
                            id='origine-dropdown',
                            placeholder="Seleziona un Origine",
                            style={'width': '80%', 'marginBottom': '1em', 'fontFamily': 'Roboto, sans-serif'},
                            value=None
                        ),
                    ], className="row-container"
                ),

        html.H2(id='titolo-report', style={'fontFamily': 'Roboto, sans-serif', 'marginBottom': '1rem', 'textAlign' : 'center'}),

        # Seconda riga con il grafico a barre e il totale imponibile
        html.Div([
                # Grafico
                dcc.Graph(
                    id='bar-chart',
                    style={'width': '65%', 'height': '400px'}, 
                    config={
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['select2d', 'lasso2d']
                    }
                ),

        # Colonna di card
        html.Div([
            # Card Imponibile
            html.Div([
                html.H4("Imponibile", className="card-title"),
                html.P(id="imponibile-valore", children="0 €", className="card-value text-green")
            ], className="card-container"),

            # Card Saltato
            html.Div([
                html.H4("Saltato", className="card-title"),
                html.P(id="saltato-valore", children="0 €", className="card-value text-red")
            ], className="card-container"),

            ], style={
                'display': 'flex',
                'flexDirection': 'column',
                'gap': '1rem', 
                'marginLeft': '2rem',
                'width': '30%',
            })
        ], className="row-container"
    ),


        # Terza riga con i grafici a torta
        html.Div([
                dcc.Graph(
                    id='pie-chart-settori',
                    style={'width': '48%', 'height': '400px'},  # Applica direttamente le dimensioni
                    config={
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['select2d', 'lasso2d']
                    }
                ),
                dcc.Graph(
                    id='pie-chart-categorie',
                    style={'width': '48%', 'height': '400px'},  # Applica direttamente le dimensioni
                    config={
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['select2d', 'lasso2d']
                    }
                ),
            ], className="row-container"
        ),
        
        # Quarta riga con i grafici a torta
        html.Div(
            [
                dcc.Graph(
                    id='pie-chart-origine',
                    style={'width': '48%', 'height': '400px'},  # Applica direttamente le dimensioni
                    config={
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['select2d', 'lasso2d']
                    }
                ),
                dcc.Graph(
                    id='pie-chart-telem',
                    style={'width': '48%', 'height': '400px'},  # Applica direttamente le dimensioni
                    config={
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['select2d', 'lasso2d']
                    }
                ),
            ],className="row-container")

]
)
        