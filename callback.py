from funzioni import *
from app import app
from dash import Input, Output, MATCH, dash, ALL, State, ctx, exceptions
import pandas as pd
import plotly.express as px
import io
import base64


@app.callback(Output('store-data-home', 'data'),
              [Output('month-dropdown', 'options'),
                Output('month-dropdown', 'value'),],
              Input('upload-data-home', 'contents'),
              State('upload-data-home', 'filename'),
              State('upload-data-home', 'last_modified'))
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
        aux = pd.read_excel(decoded, sheet_name=sh, header=2)

        
        aux.columns = aux.columns.str.strip().str.replace("'", "", regex=False)
        aux[colonnaData] = pd.to_datetime(aux[colonnaData], errors='coerce')
        aux = aux[aux[colonnaData].dt.month == mese_corrente]
        data = pd.concat([data, aux], ignore_index=True)

    data = pulisci_data(data) 

    return data.to_dict('records'), month_options, month_value

@app.callback(
    Output("filtri-collapse", "is_open"),
    Input("filtri-header-btn", "n_clicks"),
    State("filtri-collapse", "is_open"),
)
def open_close_filtri_collapse(n, current_state):
    if n == 0:
        raise exceptions.PreventUpdate()
    return not current_state


@app.callback(
    Output("filtri-header-icon", "children"), 
    Input("filtri-collapse", "is_open")
)
def switch_filtri_header_icon(is_open):
    if is_open:
        return "keyboard_arrow_up"
    else:
        return "keyboard_arrow_down"


########    CALLBACK SELEZIONE MESE     ########
#serve a aggiornare i grafici (mese input facoltativo così da vedere i dati sull'anno) 
@app.callback(
    Output('bar-chart', 'figure'),
    Output('pie-chart-settori', 'figure'),
    Output('pie-chart-categorie', 'figure'),
    Output('pie-chart-origine', 'figure'),
    Output('pie-chart-telem', 'figure'),
    Output('agente-dropdown', 'options'),
    Output('agente-dropdown', 'value'),
    Output('origine-dropdown', 'options'),
    Output('origine-dropdown', 'value'),
    Output('settore-dropdown', 'options'),
    Output('settore-dropdown', 'value'),
    Output('titolo-report', 'children'),
    Output("imponibile-valore", "children"),
    Output("saltato-valore", "children"),

    Input('store-data-home', 'data'),
    [Input('month-dropdown', 'value')],
    [Input('agente-dropdown', 'value')],
    [Input('origine-dropdown', 'value')],
    [Input('settore-dropdown', 'value')]
)
def update_grafici(anno, mesi, agente, origine, settore):
    if not anno:
        return {}, {}, {}, {}, {}, [], None, [], None, [], None, "", "", ""

    data=pd.DataFrame(anno)
    data[colonnaData] = pd.to_datetime(data[colonnaData], errors="coerce")
        
    
    anno = data[colonnaData].dt.year.unique()[0] if not data.empty else None

    
    if(agente):
        data=filtro_agente(agente, data)
        val_agente=agente
    else:
        val_agente=None
    
  
    origini = sorted(data['Origine'].dropna().unique())  
    origine_options = [{'label': origine, 'value': origine} for origine in origini]
    if(origine):
        data=filtro_origine(origine, data)
        val_origine=origine
    else:
        val_origine=None

    settori = sorted(data[colonnaSettore].dropna().unique())  
    settore_options = [{'label': settore, 'value': settore} for settore in settori]
    if(settore):
        data=filtro_settore(settore, data)
        val_settore=settore
    else:
        val_settore=None
    

    #colonna tipo, per le vendite effettuate o meno
    data=aggiungi_colonna_tipo(data)
    

    if not mesi:
        titolo = f"Anno {anno}"
    else:
        mesi=pulisci_mese(mesi)
        mesi_str = ", ".join(mesi)
        titolo = f"{mesi_str} {anno}"

    if not agente:
        if mesi:
            data=filtro_mese(mesi, data)
        fig0= crea_barre(data,colonnaAgente, colonnaImponibile, f'Imponibile per agente')
        agente_options=sorted(data[colonnaAgente].dropna().unique()) 
    else:
        datam=riordina_per_mese(data)
        fig0 = crea_barre(datam,'Mese', colonnaImponibile, f'Imponibile per mese')
        
        if mesi:#RENDE COLORATE SOLO LE COLONNE DEI MESI SELEZIONATI
            data=filtro_mese(mesi, data)
            for trace in fig0.data:
                new_colors = []
                new_hover = []
                for mese in trace.x:
                    if mese in mesi:
                        new_colors.append(trace.marker.color) 
                    else:
                        new_colors.append('lightgrey') 
                        #new_hover.append(None)
                trace.marker.color = new_colors
                #trace.hovertemplate = new_hover
        agente_options=sorted(data[colonnaAgente].dropna().unique())
        titolo=f"{agente} - {titolo}"


    da_sommare = data[data['Tipo']=='Saltata']
    totales=da_sommare[colonnaImponibile].sum()
    totale_salt = f"{totales:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
        
    
    
          
    if(data.empty):
            return crea_vuoto(), crea_vuoto(), crea_vuoto(), crea_vuoto(), crea_vuoto(), agente_options, agente, origine_options, origine, "", "", ""

    data = data[(data['Tipo'] == 'Effettuata') | (data['Tipo'] == 'Altro')]#non mi interessa più il saltato

    
    
    if not settore:
        fig1=crea_torta(data,colonnaSettore,colonnaImponibile, 2)
    else:
        fig1=crea_torta(data, 'TIPO ATTIVITA', colonnaImponibile, 2)

  
    
    somma_q_per_categoria = data.groupby('CATEGORIA')['Q.'].sum().reset_index()
    somma_q_per_categoria.rename(columns={'Q.': 'Q_TOT_CAT'}, inplace=True)

    
    df = data.groupby(['CATEGORIA', 'MOD'], as_index=False).agg({
        colonnaImponibile: 'sum',
        'Q.': 'sum'
    })

    
    df = pd.merge(df, somma_q_per_categoria, on='CATEGORIA', how='left')

    df['Q_display'] = df['Q.'].apply(
        lambda x: "<br>" if pd.isna(x)
        else f"<br>Quantità MOD: {int(x):,}".replace(",", ".")
    )

    fig2 = px.sunburst(
        df,
        path=['CATEGORIA', 'MOD'],
        values=colonnaImponibile,
        custom_data=['Q_display', 'Q_TOT_CAT'],
        title="Sunburst Imponibile e Quantità",
        color_discrete_sequence=colori
    )

    
    fig2.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Imponibile: %{value:,.2f} €"
            "%{customdata[0]}"
            "<br>Quantità CAT: %{customdata[1]:,.0f}<br>"
            "Percentuale: %{percentRoot:.2%}<br>"
            "<extra></extra>"
        )
    )


    
    
    fig3=crea_torta(data,'Origine',colonnaImponibile, 3)
    
    if 'Nome' in data.columns:        
        fig4 = crea_barre_h(data, colonnaImponibile, 'Nome', 'Imponibile per telemarketing', 8)
    else:
        fig4=crea_vuoto()
    
    totale=data[colonnaImponibile].sum()
    totale_str = f"{totale:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    

    
    
    return fig0, fig1, fig2, fig3, fig4, agente_options, val_agente, origine_options, val_origine, settore_options, val_settore, f"{titolo}", totale_str, totale_salt



@app.callback(
    Output({"type": "titolo", "index": MATCH}, "children"),
    Output({"type": "anno-data", "index": MATCH}, "data"),
    Input({"type": "anno-dropdown", "index": MATCH}, "value")
)
def update_select_dropdown(anno):
    if not anno:
        return "", None

    data = leggi_excel(anno)
    data = aggiungi_colonna_tipo(data)
    

    return f"ANNO {anno}", data.to_dict('records')



######## CALLBACK PER AGGIORNARE I GRAFICI DELLA PAGINA CONFRONTO #######
@app.callback(
    Output('bar-chart-confronto', 'figure'),
    [
        Output('store-tabella-settore', 'data'),
        Output('store-tabella-settore', 'columns'),
        Output('store-tabella-origine', 'data'),
        Output('store-tabella-origine', 'columns'),
        Output('store-tabella-categoria', 'data'),
        Output('store-tabella-categoria', 'columns')
    ],
    Output({"type": "valore", "index": ALL}, "children"),
    Output({"type": "saltato", "index": ALL}, "children"),
    Output('tabella-dinamica-confronto', 'data', allow_duplicate=True),
    Output('tabella-dinamica-confronto', 'columns', allow_duplicate=True),

    Input({"type": "anno-data", "index": ALL}, "data"),
    Input('dropdown-settore-confronto', 'value'),
    Input('dropdown-origine-confronto', 'value'),
    Input('dropdown-agente-confronto', 'value'),
    Input('dropdown-categoria-confronto', 'value'),
    Input('dropdown-mese-confronto', 'value')
)
def aggiorna_grafico(tutti_i_dati, settore, origine, agente, categoria, mesi):
    lista_card_tot=[]
    lista_card_salt=[]
    lista_dict = [pd.DataFrame(d) for d in tutti_i_dati if d]
    if not lista_dict:
        return {},[],[], [],[],[],[], ["0 €"] * len(tutti_i_dati), ["0 €"] * len(tutti_i_dati),[],[]

    dati_filtrati = []


    for d in lista_dict:
        d[colonnaData] = pd.to_datetime(d[colonnaData], errors="coerce")
        if settore:
            d = filtro_settore(settore, d)
        if origine:
            d = filtro_origine(origine, d)
        if agente:
            d = filtro_agente(agente, d)
        if categoria:
            d = filtro_categoria(categoria, d)
        if mesi:
            d=filtro_mese(mesi, d)

        effettuata_o_altro = d[d["Tipo"].isin(["Effettuata", "Altro"])]
        saltata = d[d["Tipo"] == "Saltata"]

        totale_effettuata = effettuata_o_altro["IMPONIBILE"].sum()
        totale_saltata = saltata["IMPONIBILE"].sum()

        totale_str = f"{totale_effettuata:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
        salt_str = f"{totale_saltata:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")

        lista_card_tot.append(totale_str)
        lista_card_salt.append(salt_str) 
        dati_filtrati.append(d.copy())
    
    data = pd.concat(dati_filtrati, ignore_index=True)
    data= data[data["Tipo"].isin(["Effettuata", "Altro"])]
    data = riordina_per_mese(data)
    data = riordina_per_anno(data)
    print(data.head())
    

    fig0 = crea_barre_multi_v(data, 'Mese', colonnaImponibile, 'Anno', "Confronto Imponibile per Anno e Mese", 5)

    if not settore:
        tabella1 = crea_tabella(data, colonnaSettore, 'Anno', colonnaImponibile)
    else:
        tabella1=crea_tabella(data, 'TIPO ATTIVITA', 'Anno', colonnaImponibile)
    tabella3 = crea_tabella(data, 'CATEGORIA', 'Anno', colonnaImponibile)
    tabella2 = crea_tabella(data, 'Origine', 'Anno', colonnaImponibile)

    while len(lista_card_tot) < 3:
        lista_card_tot.append("0 €")
    while len(lista_card_salt) < 3:
        lista_card_salt.append("0 €")
    return (
        fig0,
        tabella1.to_dict('records'), [{'name': str(col), 'id': str(col)} for col in tabella1.columns],
        tabella2.to_dict('records'), [{'name': str(col), 'id': str(col)} for col in tabella2.columns],
        tabella3.to_dict('records'), [{'name': str(col), 'id': str(col)} for col in tabella3.columns],
        lista_card_tot, lista_card_salt,[],[]
    )





###### CALLBACK PER OTTENERE LE OPZIONI DEI DROPDOWN ######
@app.callback(
    Output("dropdown-agente-confronto", "options"),
    Output("dropdown-settore-confronto", "options"),
    Output("dropdown-origine-confronto", "options"),
    Output("dropdown-categoria-confronto", "options"),
    Output("dropdown-mese-confronto", "options"),
    Input({"type": "anno-data", "index": ALL}, "data")
)
def aggiorna_dropdown_filtri(tutti_i_dati):
    agenti = set()
    settori = set()
    origini = set()
    categorie = set()
    mesi=set()

    for dati in tutti_i_dati:
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
    dropdown_mese = [{"label": m, "value": m} for m in sorted(mesi)]

    return dropdown_agente, dropdown_settore, dropdown_origine, dropdown_categoria, dropdown_mese


######## CALLBACK PER EVIDENZIARE LA RIGA SELEZIONATA NELLA TABELLA #######
@app.callback(
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


@app.callback(
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


@app.callback(
    Output("filtri-confronto-collapse", "is_open"),
    Input("filtri-confronto-header-btn", "n_clicks"),
    State("filtri-confronto-collapse", "is_open"),
)
def open_close_filtri_collapse(n, current_state):
    if n == 0:
        raise exceptions.PreventUpdate()
    return not current_state


@app.callback(
    Output("filtri-confronto-header-icon", "children"), 
    Input("filtri-confronto-collapse", "is_open")
)
def switch_filtri_header_icon(is_open):
    if is_open:
        return "keyboard_arrow_up"
    else:
        return "keyboard_arrow_down"
