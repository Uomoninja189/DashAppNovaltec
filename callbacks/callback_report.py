from funzioni import *
from app import *
from dash import Input, Output, MATCH, callback, dash, ALL, State, ctx, exceptions
import pandas as pd
import plotly.express as px
import io
import base64


@callback(
        Output('store-data-home', 'data'),
        [Output('month-dropdown', 'options'),
        Output('month-dropdown', 'value'),],
        Input('store-file-lista', 'data'),
        Input('anno-dropdown', 'value')
)

def update_output(dati,anno):
    if not dati or not anno:
        return dash.no_update, [], None

    for d in dati:
        if d["nome"]==anno:
            data=d.get("dati")
            break

    data=pd.DataFrame(data)
    
    data[colonnaData] = pd.to_datetime(data[colonnaData], errors="coerce")
    data=riordina_per_mese(data)
    mesi=data['Mese'].dropna().unique()
    dropdown_mese = [{"label": m, "value": m} for m in (mesi)]

    return data.to_dict('records'), dropdown_mese, None

@callback(
    Output("filtri-collapse", "is_open"),
    Input("filtri-header-btn", "n_clicks"),
    State("filtri-collapse", "is_open"),
)
def open_close_filtri_collapse(n, current_state):
    if n == 0:
        raise exceptions.PreventUpdate()
    return not current_state


@callback(
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
@callback(
    Output('bar-chart', 'figure'),
    Output('pie-chart-settori', 'figure'),
    Output('pie-chart-categorie', 'figure'),
    Output('pie-chart-origine', 'figure'),
    Output('pie-chart-telem', 'figure'),
    Output('bar-chart-pagamenti', 'figure'),
    
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
        return {}, {}, {}, {}, {}, {}, [], None, [], None, [], None, "", "", ""

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
        title="Imponibile per Categoria e Modello",
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
    

    fig5=crea_barre_h(data, colonnaImponibile, 'MET. PAG.', 'Imponibile per tipo di pagamento', 6)


    totale=data[colonnaImponibile].sum()
    totale_str = f"{totale:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")
    
    return fig0, fig1, fig2, fig3, fig4, fig5, agente_options, val_agente, origine_options, val_origine, settore_options, val_settore, f"{titolo}", totale_str, totale_salt





@callback(
    Output('anno-dropdown','options'),
    Input('store-file-lista','data'),
    prevent_initial_call=True
)
def opzioni_anno(dati):
    anni=[]
    for d in dati:
        anni.append(d["nome"])
    return anni


@callback(
    Output('store-file-lista', 'data', allow_duplicate=True), 
    Input('interval-trigger-initial-load', 'n_intervals'),
    State('store-file-lista', 'data'), 
    prevent_initial_call=True 
)
def re_trigger_list_update(n, current_store_data):
    # Questo callback si attiva una volta dopo 1ms dal caricamento
    # e semplicemente riscrive il contenuto attuale dello store nello store stesso.
    # Questo forzerà il callback aggiorna_lista_file a ri-eseguire
    # quando il layout è presumibilmente pronto.
    print("--- re_trigger_list_update TRIGGERED ---")
    if current_store_data is not None:
         print(f"Re-triggering store update with {len(current_store_data)} files.")
    else:
         print("Re-triggering store update with None data.")
    return current_store_data


@callback(
    Output('store-file-lista', 'data', allow_duplicate=True), 
    Input('url', 'pathname'),  # Trigger sul cambio di pagina
    State('store-file-lista', 'data'), 
    prevent_initial_call=True
)
def re_trigger_list_update(pathname, current_store_data):
    print(f"--- PAGE NAVIGATION TRIGGERED: {pathname} ---")
    if current_store_data is not None:
        print(f"Re-triggering store update with {len(current_store_data)} files.")
    else:
        print("Re-triggering store update with None data.")
    return current_store_data