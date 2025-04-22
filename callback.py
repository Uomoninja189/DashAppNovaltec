from funzioni import *
from app import app
from dash import Input, Output, MATCH, dash, ALL
import pandas as pd
import plotly.express as px



########    CALLBACK SELEZIONE ANNO     ########
#serve a raccogliere i mesi 
@app.callback(
    Output('month-dropdown', 'options'),
    Output('month-dropdown', 'value'),
    Input('anno-dropdown', 'value')
)
def aggiorna_mesi(anno):

    if not anno:
        return [], None
    
    file_path = f'OrdiniAgenti{anno}.xlsx'
    data = pd.ExcelFile(file_path)
    
    #Raccolta nomi dei mesi dai fogli
    mesi = pulisci_mese(data.sheet_names)
    month_options = [{'label': m, 'value': m} for m in mesi]
    month_value = None  

    return month_options, month_value





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
    Output('titolo-report', 'children'),
    Output("imponibile-valore", "children"),
    Output("saltato-valore", "children"),

    Input('anno-dropdown', 'value'),
    [Input('month-dropdown', 'value')],
    [Input('agente-dropdown', 'value')],
    [Input('origine-dropdown', 'value')]
)
def update_grafici(anno, mesi, agente, origine):
    if not anno:
        return {}, {}, {}, {}, {}, [], None, [], None, "", "", ""

    data=leggi_excel(anno)
        
    


    
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
        fig0= crea_barre(data,'AGENTE', 'IMPONIBILE', f'Imponibile per agente')
        agente_options=sorted(data['AGENTE'].dropna().unique()) 
    else:
        datam=riordina_per_mese(data)
        fig0 = crea_barre(datam,'Mese', 'IMPONIBILE', f'Imponibile per mese')
        
        if mesi:#RENDE COLORATE SOLO LE COLONNE DEI MESI SELEZIONATI
            data=filtro_mese(mesi, data)
            for trace in fig0.data:
                new_colors = []
                for mese in trace.x:
                    if mese in mesi:
                        new_colors.append(trace.marker.color) 
                    else:
                        new_colors.append('lightgrey') 
                trace.marker.color = new_colors
        agente_options=sorted(data['AGENTE'].dropna().unique())
        titolo=f"{agente} - {titolo}"


    da_sommare = data[data['Tipo']=='Saltata']
    totales=da_sommare['IMPONIBILE'].sum()
    totale_salt = f"{totales:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
        
    
    
          
    if(data.empty):
            return crea_vuoto(), crea_vuoto(), crea_vuoto(), crea_vuoto(), crea_vuoto(), agente_options, agente, origine_options, origine, "", "", ""

    data = data[(data['Tipo'] == 'Effettuata') | (data['Tipo'] == 'Altro')]#non mi interessa più il saltato

    
    

    fig1=crea_torta(data,'SETTORE ','IMPONIBILE')


  
    # Somma delle quantità per categoria
    somma_q_per_categoria = data.groupby('CATEGORIA')['Q.'].sum().reset_index()
    somma_q_per_categoria.rename(columns={'Q.': 'Q_TOT_CAT'}, inplace=True)

    # Aggregazione per categoria e MOD
    df = data.groupby(['CATEGORIA', 'MOD'], as_index=False).agg({
        'IMPONIBILE': 'sum',
        'Q.': 'sum'
    })

    # Merge con la somma per categoria
    df = pd.merge(df, somma_q_per_categoria, on='CATEGORIA', how='left')

    # Colonna custom per mostrare le quantità (formattate)
    df['Q_display'] = df['Q.'].apply(
        lambda x: "<br>" if pd.isna(x)
        else f"<br>Quantità MOD: {int(x):,}".replace(",", ".")
    )

    # Sunburst chart
    fig2 = px.sunburst(
        df,
        path=['CATEGORIA', 'MOD'],
        values='IMPONIBILE',
        custom_data=['Q_display', 'Q_TOT_CAT'],
        title="Sunburst Imponibile e Quantità",
        color_discrete_sequence=colori
    )

    # Template per il tooltip (hover)
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


    
    
    fig3=crea_torta(data,'Origine','IMPONIBILE')
    
    if 'Nome' in data.columns:
        aux = data.dropna(subset=['Nome'])
        

        
        fig4 = crea_torta(aux, 'Nome', 'IMPONIBILE')
        fig4.update_layout(title=f'Distribuzione Percentuale per Telemarketing')
    else:
        fig4={}
    
    totale=data['IMPONIBILE'].sum()
    totale_str = f"{totale:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    

    

    


    
    return fig0, fig1, fig2, fig3, fig4, agente_options, val_agente, origine_options, val_origine, f"{titolo}", totale_str, totale_salt



@app.callback(
    Output({"type": "titolo", "index": MATCH}, "children"),
    Output({"type": "valore", "index": MATCH}, "children"),
    Output({"type": "anno-data", "index": MATCH}, "data"),
    Input({"type": "anno-dropdown", "index": MATCH}, "value")
)
def update_select_dropdown(anno):
    if not anno:
        return "", "0 €", None

    data = leggi_excel(anno)
    data = aggiungi_colonna_tipo(data)
    data_cont = data[data["Tipo"].isin(["Effettuata", "Altro"])]

    totale = data_cont["IMPONIBILE"].sum()
    totale_str = f"{totale:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")

    return f"IMPONIBILE {anno}", totale_str, data_cont.to_dict('records')


@app.callback(
    Output('bar-chart-confronto', 'figure'),
    Output('bar-chart-settore-confronto', 'figure'),
    Output('bar-chart-categoria-confronto', 'figure'),
    Output('pie-chart-settore-confronto-primo', 'figure'),
    Output('pie-chart-settore-confronto-secondo', 'figure'),
    Output('pie-chart-settore-confronto-terzo', 'figure'),
    Input({"type": "anno-data", "index": ALL}, "data"),
    Input('dropdown-settore-confronto', 'value'),
    Input('dropdown-origine-confronto', 'value'),
    Input('dropdown-agente-confronto', 'value'),
    Input('dropdown-cateogoria-confronto', 'value')
)
def aggiorna_grafico(tutti_i_dati, settore, origine, agente, categoria):
    lista_dict = [pd.DataFrame(d) for d in tutti_i_dati if d]
    if not lista_dict:
        return {},{},{},{},{},{}
    
    data=pd.concat(lista_dict, ignore_index=True)

    data = aggiungi_colonna_tipo(data)
    data = data[data["Tipo"].isin(["Effettuata", "Altro"])]


    data["DATA "] = pd.to_datetime(data["DATA "], errors="coerce")

    data=riordina_per_mese(data)
    data=riordina_per_anno(data)

    if(settore):
        data=filtro_settore(settore, data)
    if(origine):
        data=filtro_origine(origine, data)
    if(agente):
        data=filtro_agente(agente, data)
    if(categoria):
        data=filtro_categoria(categoria, data)

    
    fig0=crea_barre_multi_v(data, 'Mese', 'IMPONIBILE', 'Anno', "Confronto Imponibile per Anno e Mese")

    print(data['CATEGORIA'].unique())

    if(settore):
        fig1=crea_barre_multi_h(data, 'IMPONIBILE', 'Anno','TIPO ATTIVITA', "Confronto Imponibile per Settore e Anno")
    else:
        fig1=crea_barre_multi_h(data, 'IMPONIBILE','Anno', 'SETTORE ',  "Confronto Imponibile per Settore e Anno")

    if(categoria):
        fig2=crea_barre_multi_h(data, 'IMPONIBILE', 'Anno', 'MOD', "Confronto Imponibile per Categoria e Anno")
    else:
        fig2=crea_barre_multi_h(data, 'IMPONIBILE', 'Anno', 'CATEGORIA', "Confronto Imponibile per MOD e Anno")

    anni = pd.to_datetime(data["DATA "], errors="coerce").dt.year.dropna().unique()
    anni = sorted(anni)  # ordina gli anni in ordine crescente

    anno1 = anno2 = anno3 = None  # inizializza

    if len(anni) == 1:
        anno1 = anni[0]
    elif len(anni) == 2:
        anno1, anno2 = anni
    elif len(anni) >= 3:
        anno1, anno2, anno3 = anni[:3]  # prendi solo i primi 3 (più vecchi)

    df_anno1 = data[data["DATA "].dt.year == anno1] if anno1 else pd.DataFrame()
    df_anno2 = data[data["DATA "].dt.year == anno2] if anno2 else pd.DataFrame()
    df_anno3 = data[data["DATA "].dt.year == anno3] if anno3 else pd.DataFrame()

    fig3=crea_torta(df_anno1, 'SETTORE ', 'IMPONIBILE') if not df_anno1.empty else {}
    fig4=crea_torta(df_anno2, 'SETTORE ', 'IMPONIBILE') if not df_anno2.empty else {}
    fig5=crea_torta(df_anno3, 'SETTORE ', 'IMPONIBILE') if not df_anno3.empty else {}



    return fig0, fig1, fig2, fig3, fig4, fig5


@app.callback(
    Output("dropdown-agente-confronto", "options"),
    Output("dropdown-settore-confronto", "options"),
    Output("dropdown-origine-confronto", "options"),
    Output("dropdown-cateogoria-confronto", "options"),
    Input({"type": "anno-data", "index": ALL}, "data")
)
def aggiorna_dropdown_filtri(tutti_i_dati):
    agenti = set()
    settori = set()
    origini = set()
    categorie = set()

    for dati in tutti_i_dati:
        if dati:
            df = pd.DataFrame(dati)
            if "AGENTE" in df.columns:
                agenti.update(df["AGENTE"].dropna().unique())
            if "SETTORE " in df.columns:
                settori.update(df["SETTORE "].dropna().unique())
            if "Origine" in df.columns:
                origini.update(df["Origine"].dropna().unique())
            if "CATEGORIA" in df.columns:
                categorie.update(df["CATEGORIA"].dropna().unique())

    dropdown_agente = [{"label": a, "value": a} for a in sorted(agenti)]
    dropdown_settore = [{"label": s, "value": s} for s in sorted(settori)]
    dropdown_origine = [{"label": o, "value": o} for o in sorted(origini)]
    dropdown_categoria = [{"label": c, "value": c} for c in sorted(categorie)]

    return dropdown_agente, dropdown_settore, dropdown_origine, dropdown_categoria
