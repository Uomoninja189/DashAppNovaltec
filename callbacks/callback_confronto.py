from funzioni import *
from app import *
from dash import Input, Output, MATCH, callback, dash, ALL, State, ctx, exceptions
import pandas as pd
import plotly.express as px
import io
import base64


######## CALLBACK PER AGGIORNARE I GRAFICI DELLA PAGINA CONFRONTO #######
@callback(
    Output('bar-chart-confronto', 'figure'),
    [
        Output('store-tabella-settore', 'data'),
        Output('store-tabella-settore', 'columns'),
        Output('store-tabella-origine', 'data'),
        Output('store-tabella-origine', 'columns'),
        Output('store-tabella-categoria', 'data'),
        Output('store-tabella-categoria', 'columns')
    ],
    Output('card-valore-primo', "children"),
    Output('card-saltato-primo', "children"),
    Output('card-valore-secondo', "children"),
    Output('card-saltato-secondo', "children"),
    Output('card-valore-terzo', "children"),
    Output('card-saltato-terzo', "children"),
    Output('tabella-dinamica-confronto', 'data', allow_duplicate=True),
    Output('tabella-dinamica-confronto', 'columns', allow_duplicate=True),

    Input('store-anno-confronto-primo', 'data'),
    Input('store-anno-confronto-secondo', 'data'),
    Input('store-anno-confronto-terzo', 'data'),
    Input('dropdown-settore-confronto', 'value'),
    Input('dropdown-origine-confronto', 'value'),
    Input('dropdown-agente-confronto', 'value'),
    Input('dropdown-categoria-confronto', 'value'),
    Input('dropdown-mese-confronto', 'value'),
    prevent_initial_call=True 
)
def aggiorna_grafici_confronto(data1, data2,data3, settore, origine, agente, categoria, mesi):
    
    tutti_i_dati=[data1,data2,data3]
    
    if not any(tutti_i_dati):
        return {},[],[], [],[],[],[],["0 €"], ["0 €"],["0 €"], ["0 €"],["0 €"], ["0 €"],[],[]



    def elabora(df):
        df[colonnaData] = pd.to_datetime(df[colonnaData], errors="coerce")
        if settore:
            df = filtro_settore(settore, df)
        if origine:
            df = filtro_origine(origine, df)
        if agente:
            df = filtro_agente(agente, df)
        if categoria:
            df = filtro_categoria(categoria, df)
        if mesi:
            df = filtro_mese(mesi, df)
        effettuata_o_altro = df[df["Tipo"].isin(["Effettuata", "Altro"])]
        saltata = df[df["Tipo"] == "Saltata"]
        totale_effettuata = effettuata_o_altro["IMPONIBILE"].sum()
        totale_saltata = saltata["IMPONIBILE"].sum()
        totale_str = f"{totale_effettuata:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
        salt_str = f"{totale_saltata:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
        return totale_str, salt_str, df
        

    totale1, salt1, df1 = elabora(pd.DataFrame(data1)) if data1 else ("0 €", "0 €", pd.DataFrame())
    totale2, salt2, df2 = elabora(pd.DataFrame(data2)) if data2 else ("0 €", "0 €", pd.DataFrame())
    totale3, salt3, df3 = elabora(pd.DataFrame(data3)) if data3 else ("0 €", "0 €", pd.DataFrame())

    data = pd.concat([df1, df2, df3], ignore_index=True)

    data= data[data["Tipo"].isin(["Effettuata", "Altro"])]
    data = riordina_per_mese(data)
    data = riordina_per_anno(data)
    
    

    fig0 = crea_barre_multi_v(data, 'Mese', colonnaImponibile, 'Anno', "Confronto Imponibile per Anno e Mese", 5)

    if not settore:
        tabella1 = crea_tabella(data, colonnaSettore, 'Anno', colonnaImponibile)
    else:
        tabella1=crea_tabella(data, 'TIPO ATTIVITA', 'Anno', colonnaImponibile)
    tabella3 = crea_tabella(data, 'CATEGORIA', 'Anno', colonnaImponibile)
    tabella2 = crea_tabella(data, 'Origine', 'Anno', colonnaImponibile)

   
    return (
        fig0,
        tabella1.to_dict('records'), [{'name': str(col), 'id': str(col)} for col in tabella1.columns],
        tabella2.to_dict('records'), [{'name': str(col), 'id': str(col)} for col in tabella2.columns],
        tabella3.to_dict('records'), [{'name': str(col), 'id': str(col)} for col in tabella3.columns],
        totale1, salt1, totale2, salt2, totale3, salt3,[],[]
    )





###### CALLBACK PER OTTENERE LE OPZIONI DEI DROPDOWN ######
@callback(
    Output("dropdown-agente-confronto", "options"),
    Output("dropdown-settore-confronto", "options"),
    Output("dropdown-origine-confronto", "options"),
    Output("dropdown-categoria-confronto", "options"),
    Output("dropdown-mese-confronto", "options"),

    Input('store-anno-confronto-primo', 'data'),
    Input('store-anno-confronto-secondo', 'data'),
    Input('store-anno-confronto-terzo', 'data'),
)
def aggiorna_dropdown_filtri(data1, data2, data3):
    agenti = set()
    settori = set()
    origini = set()
    categorie = set()
    mesi=set()

    for dati in [data1, data2, data3]:
        if dati:
            df = pd.DataFrame(dati)
            if colonnaAgente in df.columns:
                agenti.update(df[colonnaAgente].dropna().unique())
            if colonnaSettore in df.columns:
                settori.update(df[colonnaSettore].dropna().unique())
            if "Origine" in df.columns:
                origini.update(df["Origine"].dropna().unique())
            if "CATEGORIA" in df.columns:
                categorie.update(df["CATEGORIA"].dropna().unique())
            if colonnaData in df.columns:
                df[colonnaData] = pd.to_datetime(df[colonnaData], errors="coerce")
                df=riordina_per_mese(df)
                mesi.update(df['Mese'].dropna().unique())

    dropdown_agente = [{"label": a, "value": a} for a in sorted(agenti)]
    dropdown_settore = [{"label": s, "value": s} for s in sorted(settori)]
    dropdown_origine = [{"label": o, "value": o} for o in sorted(origini)]
    dropdown_categoria = [{"label": c, "value": c} for c in sorted(categorie)]

    ordine_completo = list((mesi_mappa).values())
    mesi = sorted(mesi, key=lambda m: ordine_completo.index(m))
    dropdown_mese = [{"label": m, "value": m} for m in (mesi)]

    return dropdown_agente, dropdown_settore, dropdown_origine, dropdown_categoria, dropdown_mese


######## CALLBACK PER EVIDENZIARE LA RIGA SELEZIONATA NELLA TABELLA #######
@callback(
    Output('tabella-dinamica-confronto', 'style_data_conditional'),
    Input('tabella-dinamica-confronto', 'active_cell')
)
def evidenzia_riga(active_cell):
    if active_cell:
        return [
            {
                'if': {'row_index': active_cell['row']},
                'backgroundColor': '#D6F1FF',
                'border': '1px solid #0074D9',
                'fontWeight': 'bold'
            }
        ]
    return []


@callback(
    Output('tabella-dinamica-confronto', 'data'),
    Output('tabella-dinamica-confronto', 'columns'),
    
    Input('btn-settore', 'n_clicks'),
    Input('btn-origine', 'n_clicks'),
    Input('btn-categoria', 'n_clicks'),

    State('store-tabella-settore', 'data'),
    State('store-tabella-settore', 'columns'),
    State('store-tabella-origine', 'data'),
    State('store-tabella-origine', 'columns'),
    State('store-tabella-categoria', 'data'),
    State('store-tabella-categoria', 'columns')
)
def aggiorna_tabella(btn_settore, btn_origine, btn_categoria, data_settore, cols_settore, data_origine, cols_origine, data_categoria, cols_categoria):
    
    if "btn-settore"  == ctx.triggered_id:
        return data_settore, cols_settore
    elif "btn-origine" == ctx.triggered_id:
        return data_origine, cols_origine
    elif "btn-categoria" == ctx.triggered_id:
        return data_categoria, cols_categoria
    else:
        return [], []  # Se nessun pulsante è stato premuto


@callback(
    Output("filtri-confronto-collapse", "is_open"),
    Input("filtri-confronto-header-btn", "n_clicks"),
    State("filtri-confronto-collapse", "is_open"),
)
def open_close_filtri_collapse(n, current_state):
    if n == 0:
        raise exceptions.PreventUpdate()
    return not current_state


@callback(
    Output("filtri-confronto-header-icon", "children"), 
    Input("filtri-confronto-collapse", "is_open")
)
def switch_filtri_header_icon(is_open):
    if is_open:
        return "keyboard_arrow_up"
    else:
        return "keyboard_arrow_down"
    



@callback(
    Output('card-titolo-primo', "children"),
    Output('store-anno-confronto-primo', "data"),
    Input('anno-dropdown-confronto-primo', "value"),
    Input('store-file-lista', 'data'),
)
def update_select_dropdown(anno, dati):
    if not anno:
        return "", None

    for d in dati:
        if d["nome"]==anno:
            data=d.get("dati")
            break

    data=pd.DataFrame(data)
    
    data=aggiungi_colonna_tipo(data)

    return f"ANNO {anno}", data.to_dict('records')


@callback(
    Output('card-titolo-secondo', "children"),
    Output('store-anno-confronto-secondo', "data"),
    Input('anno-dropdown-confronto-secondo', "value"),
    Input('store-file-lista', 'data'),
)
def update_select_dropdown(anno, dati):
    if not anno:
        return "", None

    for d in dati:
        if d["nome"]==anno:
            data=d.get("dati")
            break

    data=pd.DataFrame(data)
    
    data=aggiungi_colonna_tipo(data)

    return f"ANNO {anno}", data.to_dict('records')


@callback(
    Output('card-titolo-terzo', "children"),
    Output('store-anno-confronto-terzo', "data"),
    Input('anno-dropdown-confronto-terzo', "value"),
    Input('store-file-lista', 'data'),
)
def update_select_dropdown(anno, dati):
    if not anno:
        return "", None

    for d in dati:
        if d["nome"]==anno:
            data=d.get("dati")
            break

    data=pd.DataFrame(data)
    data=aggiungi_colonna_tipo(data)
    

    return f"ANNO {anno}", data.to_dict('records')


@callback(
    Output('anno-dropdown-confronto-primo','options'),
    Output('anno-dropdown-confronto-secondo','options'),
    Output('anno-dropdown-confronto-terzo','options'),
    Input('store-file-lista','data'),
    prevent_initial_call=True
)
def opzioni_anno_confronto(dati):
    anni=[]
    for d in dati:
        anni.append(d["nome"])
    return anni,anni,anni

