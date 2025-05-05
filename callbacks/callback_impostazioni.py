from dash import Input, Output, State, callback_context, callback, dash, ctx, ALL
from funzioni import *
from app import *
import json, io, base64

@callback(
    Output('salvataggio-status', 'children'),
    Output('salvataggio-status', 'is_open'),
    Input('salva-impostazioni-btn', 'n_clicks'),
    State('colonna-imponibile-imp', 'value'),
    State('colonna-data-imp', 'value'),
    State('colonna-agente-imp', 'value'),
    State('colonna-settore-imp', 'value'),
    prevent_initial_call=True
)
def salva_su_json(n_clicks, imponibile, data, agente, settore):
    if n_clicks is None:
            return dash.no_update
    impostazioni = {
        "colonnaImponibile": imponibile,
        "colonnaData": data,
        "colonnaAgente": agente,
        "colonnaSettore": settore
    }

    with open(impostazioni_path, "w") as f:
        json.dump(impostazioni, f, indent=4)

    return ["Modifiche salvate con successo ✅"], True


@callback(
    Output('store-file-lista', 'data'),
    Input('upload-data-imp', 'contents'),
    State('upload-data-imp', 'filename'),
    State('store-file-lista' \
    '', 'data'),
    prevent_initial_call=True
)
def salva_file(contents, filename, store_data):
    if not contents:
        return dash.no_update

    decoded = base64.b64decode(contents.split(',')[1])
    xls = pd.ExcelFile(io.BytesIO(decoded))
    

    data = pd.DataFrame()
    for mese_corrente, sh in enumerate(xls.sheet_names, start=1):
        aux = xls.parse(sheet_name=sh, header=2)


        
        aux.columns = aux.columns.str.strip().str.replace("'", "", regex=False)
        aux[colonnaData] = pd.to_datetime(aux[colonnaData], errors='coerce')
        aux = aux[aux[colonnaData].dt.month == mese_corrente]
        data = pd.concat([data, aux], ignore_index=True)

    data = pulisci_data(data)
    data=aggiungi_colonna_tipo(data)

    

    data=data.to_dict('records')

    store_data = store_data or []

    # Evita duplicati per nome file
    store_data = [f for f in store_data if f["nome"] != filename]
    store_data.append({"nome": filename, "dati": data})

    return store_data





@callback(
    Output("lista-file-imp", "children"),
    Input("store-file-lista", "data"),
    prevent_initial_call=False
)
def aggiorna_lista_file(files):
    if not files:

        return [html.Li("Nessun file caricato.")]
    
    return [
        html.Li([
            f["nome"],
            html.Button("❌", id={'type': 'elimina-file', 'index': f['nome']}, n_clicks=0, style={'marginLeft': '5px','background': 'none', 'border':'0'})
        ])
        for f in files
    ]

@callback(
    Output('store-file-lista', 'data', allow_duplicate=True),
    Input({'type': 'elimina-file', 'index': ALL}, 'n_clicks'),
    State('store-file-lista', 'data'),
    prevent_initial_call=True
)
def elimina_file(n_clicks_list, dati):
    
    if not any(n_clicks_list) or not dati:
        raise dash.exceptions.PreventUpdate

   
    triggered_id = ctx.triggered_id  
    nome_da_rimuovere = triggered_id['index']

    nuovi_file = [f for f in dati if f['nome'] != nome_da_rimuovere]
   
    return nuovi_file

