from funzioni import *
from app import app
from dash import Input, Output, MATCH, callback, dash, ALL, State, ctx, exceptions
import pandas as pd
import plotly.express as px
import io
import base64

@callback(
    Output("filtri-collapse-crea", "is_open"),
    Input("filtri-header-btn-crea", "n_clicks"),
    State("filtri-collapse-crea", "is_open"),
)
def open_close_filtri_collapse(n, current_state):
    if n == 0:
        raise exceptions.PreventUpdate()
    return not current_state


@callback(
    Output("filtri-header-icon-crea", "children"), 
    Input("filtri-collapse-crea", "is_open")
)
def switch_filtri_header_icon(is_open):
    if is_open:
        return "keyboard_arrow_up"
    else:
        return "keyboard_arrow_down"
    
    
@callback(
        Output('store-data-crea', 'data'),
        [Output('month-dropdown-crea', 'options'),
        Output('month-dropdown-crea', 'value'),],
        Input('upload-data-crea', 'contents'),
        State('upload-data-crea', 'filename'),
        State('upload-data-crea', 'last_modified'))

def update_output(contents, list_of_names, list_of_dates):
    if contents is None:
        return dash.no_update, [], None

    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)

    xls = pd.ExcelFile(io.BytesIO(decoded))

    mesi = pulisci_mese(xls.sheet_names)
    month_options = [{'label': m, 'value': m} for m in mesi]
    month_value = None  

    data = pd.DataFrame()
    for mese_corrente, sh in enumerate(xls.sheet_names, start=1):
        aux = pd.read_excel(io.BytesIO(decoded), sheet_name=sh, header=2)

        
        aux.columns = aux.columns.str.strip().str.replace("'", "", regex=False)
        aux[colonnaData] = pd.to_datetime(aux[colonnaData], errors='coerce')
        aux = aux[aux[colonnaData].dt.month == mese_corrente]
        data = pd.concat([data, aux], ignore_index=True)

    data = pulisci_data(data) 

    return data.to_dict('records'), month_options, month_value

###### CALLBACK PER OTTENERE LE OPZIONI DEI DROPDOWN ######
@callback(
    Output("x-dropdown-crea", "options"),
    Output("y-dropdown-crea", "options"),
    Input("store-data-crea", "data")
)
def aggiorna_dropdown_filtri(anno):

    if not anno:
        return [],[]

    data=pd.DataFrame(anno)
    data[colonnaData] = pd.to_datetime(data[colonnaData], errors="coerce")
    
    colonne = data.columns.tolist()

    opzioni = [{"label": col, "value": col} for col in colonne]


    return opzioni, opzioni



@callback(
    Output("chart-crea", "figure"),

    Input("x-dropdown-crea", "value"),
    Input("y-dropdown-crea", "value"),
    Input("tipo-dropdown-crea", "value"),
    Input("month-dropdown-crea", "value"),
    Input("store-data-crea", "data")
)
def crea_grafico(x,y,tipo, mese, anno):

    if not x or not y or not tipo or x==y:
        return crea_vuoto()
    
    data=pd.DataFrame(anno)
    data[colonnaData] = pd.to_datetime(data[colonnaData], errors="coerce")

    if mese:
        data=filtro_mese(mese,data)

    if tipo=="Barre orizzontali":
        return crea_barre_h(data, x, y, f"{y} per {x}")
    elif tipo=="Barre verticali":
        return crea_barre(data, x, y, f"{x} per {y}")
    elif tipo=="Torta":
        return crea_torta(data, x, y)
    else:
        return crea_vuoto()
    
