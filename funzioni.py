import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import re
from dash import html
from unidecode import unidecode
import random

mappa_mesi = {
        'Gen': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
        'Mag': 5, 'Giu': 6, 'Lug': 7, 'Ago': 8,
        'Set': 9, 'Ott': 10, 'Nov': 11, 'Dic': 12
    }

mesi_mappa={
    1:'Gennaio', 2:'Febbraio', 3:'Marzo', 4:'Aprile',
    5:'Maggio', 6:'Giugno', 7:'Luglio', 8:'Agosto',
    9:'Settembre', 10:'Ottobre', 11:'Novembre', 12:'Dicembre'
}
colori1 = [
    '#007ec9',  # Blu primario - deciso, professionale
    '#005b99',  # Blu scuro - profondo, elegante
    '#339ddc',  # Azzurro chiaro - fresco, tech
    '#00b6e5',  # Azzurro vivace - moderno, brillante

    '#ffc900',  # Giallo primario - energico, solare
    '#ffdf57',  # Giallo chiaro - allegro, acceso
    '#f5a623',  # Arancio miele - caldo, visibile

    '#eb3c89',  # Rosa acceso - creativo, giovanile
    '#a38cf5',  # Lavanda - delicato, futuristico
    '#5ac47d',  # Verde menta - rilassante, naturale
]

colori = [
 '#ff6347',  # Rosso Pomodoro / Corallo chiaro (Rosso-Arancio)
 '#f2ad54',  # Arancio chiaro (Arancio)
 '#f8cb46',  # Giallo senape (Giallo)
 '#5ac47d',  # Verde menta (Verde)
 '#008080',  # Ottanio / Teal (Verde-Blu)
 '#3886bb',  # Blu oceano (Blu scuro)
 '#669df5',  # Azzurro brillante (Blu chiaro)
 '#a38cf5',  # Lilla/viola lavanda (Viola)
 '#ed69c0',  # Rosa bubblegum (Rosa chiaro/freddo)
 '#eb3c89'   # Rosa acceso (Rosa/Magenta acceso)
]

colonnaData = 'DATA'
colonnaSettore='SETTORE'
colonnaAgente='AGENTE'
colonnaImponibile='IMPONIBILE'

def carica_anni():
    folder = './'  

    excel_files = [f for f in os.listdir(folder) if re.match(r'OrdiniAgenti\d{4}\.xlsx', f)]

    anni = sorted([re.search(r'\d{4}', f).group() for f in excel_files])

    return anni

def leggi_excel(anno):
    data = pd.DataFrame()
    file_path = f'OrdiniAgenti{anno}.xlsx'
    xls = pd.ExcelFile(file_path)
    
    for mese_corrente, sh in enumerate(xls.sheet_names, start=1):
        aux = pd.read_excel(file_path, sheet_name=sh, header=2)
        


        aux.columns = aux.columns.str.strip().str.replace("'", "", regex=False)

        aux[colonnaData] = pd.to_datetime(aux[colonnaData], errors='coerce')

        aux = aux[
            (aux[colonnaData].dt.year == int(anno)) &
            (aux[colonnaData].dt.month == mese_corrente)
        ]
        data = pd.concat([data, aux], ignore_index=True)

    
    data=pulisci_data(data)
    
    return data



def filtro_anno(anno, data):
    return data[data[colonnaData].dt.year == anno]

def filtro_agente(nomeAgente, data):
    return data[data[colonnaAgente] == nomeAgente]

def filtro_settore(nomeSettore, data):
    return data[data[colonnaSettore]==nomeSettore]
    
def filtro_origine(nomeOrigine, data):
    return data[data['Origine']==nomeOrigine]

def filtro_categoria(nomeCategoria, data):
    return data[data['CATEGORIA']==nomeCategoria]

def filtro_mese(mesi,data):
    
    
    mesi_numerici = [ottieni_numero_mese(mese) for mese in mesi]
    
    # Filtra il dataframe per i mesi numerici selezionati
    return data[data[colonnaData].dt.month.isin(mesi_numerici)]


def pulisci_data(data):
    
    data=data.replace(r'^\s*$', pd.NA, regex=True)
    data['IMPONIBILE'] = pd.to_numeric(data['IMPONIBILE'], errors='coerce')
    
    data = data.dropna(subset=['IMPONIBILE'])
    

    data = data[~data.iloc[:, 1:].isna().all(axis=1)]

    for col in data.select_dtypes(include=['object', 'category']).columns:
        data[col] = data[col].apply(lambda x: str(x).strip().lower().capitalize() if pd.notna(x) else x)

    
    if 'Q.' not in data.columns:
        data['Q.'] = pd.NA
    else:
        data['Q.'] = pd.to_numeric(data['Q.'], errors='coerce') 
    data = data.rename(columns={'?': 'Origine'})
    data=riempi_vuoti(data)
    data['MOD']=data['MOD'].str.upper()
    data['Origine'] = data['Origine'].str.upper()
    data = data[~((data['IMPONIBILE'] == 0) | (data['IMPONIBILE'].isna()))]

    return data

def riempi_vuoti(data):
    data[[colonnaSettore, 'MOD', colonnaAgente,'Origine']] = data[[colonnaSettore, 'MOD', colonnaAgente,'Origine']].fillna("Sconosciuto")
    data['CATEGORIA']=data['CATEGORIA'].fillna('Acc')
    
    data.loc[data['Q.'].isna() & (data['CATEGORIA'].str.upper() == 'ACC'), 'Q.'] = 0
    data.loc[data['Q.'].isna() & (data['CATEGORIA'].str.upper() != 'ACC'), 'Q.'] = 1
    return data

def pulisci_mese(mesi):
    return [re.sub(r'[^\w\s]', '', mese).split()[0] for mese in mesi]



def aggiungi_colonna_tipo(data):
    data['Tipo'] = data.apply(
        lambda row: 
            'Effettuata' if str(row['FT.']).startswith(('F', 'f')) 
            else 'Saltata' if str(row['FT.']).strip().lower() == 'saltata' 
            else 'Altro', 
        axis=1
    )

    data['Tipo'] = data.apply(lambda row: 'Saltata' if str(row['NOTE']).startswith('saltata') else row['Tipo'], axis=1)
    order = ['Effettuata', 'Altro', 'Saltata']
    data['Tipo'] = pd.Categorical(data['Tipo'], categories=order, ordered=True)

    return data

def riordina_per_mese(data):

    data['Mese'] = data[colonnaData].dt.month.map(mesi_mappa)
    ordine_completo = list((mesi_mappa).values())
    data['Mese'] = pd.Categorical(data['Mese'], categories=ordine_completo, ordered=True)
    return data

def riordina_per_anno(data):

    data['Anno'] = data[colonnaData].dt.year
    data['Anno'] = pd.Categorical(data['Anno'], ordered=True)

    return data

def ottieni_numero_mese(nome_mese):
        mese_norm = nome_mese.strip().lower().capitalize()
        for mese, numero in mappa_mesi.items():
            if mese_norm.startswith(mese):
                return numero
        return None

def ottieni_nome_mese(numero_mese):
    for mese, numero in mappa_mesi.items():
        if numero == numero_mese:
            return mese
    return None

def spezza_sequenza(sequenza, seed=None):

    if not sequenza:
        return sequenza 
    if not seed:
        seed = random.randint(1, len(sequenza) - 1)  # Punto casuale per spezzare
    return sequenza[seed:] + sequenza[:seed]



def crea_torta(data, group, disc, primo=None):
    
    data= data.groupby([group], as_index=True).agg({
            disc: 'sum',
            'Q.': 'sum'
        }).rename(columns={'Q.': 'N° vendite'})
    
    
    pie= px.pie(data, 
                names=data.index,
                values=disc, 
                title=f'Distribuzione Percentuale per {group}',
                hole=.4,
                hover_data=["N° vendite"],
                hover_name=data.index,
                color_discrete_sequence=spezza_sequenza(colori, primo)
    )
    pie.update_traces(
        textposition='inside', 
        textinfo='percent'
    )
    pie.update_layout(showlegend=False)
    return pie

def crea_barre(data, x, y, title):
    data = data.groupby([x, 'Tipo'], as_index=False)['IMPONIBILE'].sum()
    fig=px.bar(data, 
                x=x, 
                y=y, 
                color='Tipo',  # Differenza tra vendite saltate e non saltate
                title=title,
                labels={'IMPONIBILE': 'Imponibile', colonnaAgente: 'Agente'},
                color_discrete_map={'Effettuata': '#5ac47d',  'Saltata': '#d1515f',   'Altro': '#f2ad54' },
                
                )

    #per impilare le barre
    fig.update_layout(
        barmode='stack',
        xaxis_title=None,
        yaxis_title=None,
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig

def crea_barre_h(data, x, y, titolo, primo=None):
    data = data.dropna(subset=[y])
    if data.empty:
        return crea_vuoto()
    data = data.groupby([y], as_index=False).agg({x: 'sum', 'Q.': 'sum'})

    data = data.sort_values(by=x, ascending=False)
    data = data.rename(columns={'Q.': 'N° Vendite'})

    
    fig= px.bar(
        data,
        x=x,
        y=y,
        title=titolo,
        color=y,
        barmode='stack',
        color_discrete_sequence=spezza_sequenza(colori, primo),
        orientation='h',
        hover_data={x: True, 'N° Vendite': True, y: False} 
    )
    fig.update_layout(
        showlegend=False,
        xaxis_title=None,
        yaxis_title=None,
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig

def crea_barre_multi_v(data, x, y, colore, title, primo=None):
    grouped = data.groupby([x, colore])[y].sum().reset_index()

    fig= px.bar(grouped, x=x, y=y, color=colore, barmode='group', title=title, color_discrete_sequence=spezza_sequenza(colori, primo))
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        plot_bgcolor='rgba(0,0,0,0)',
    )
    return fig
    
def crea_barre_multi_h(data, x, y, colore, title, primo=None):
    grouped = data.groupby([y, colore])[x].sum().reset_index()

    totali_y = grouped.groupby(y)[x].transform('sum')

    # Aggiunge colonna percentuale
    grouped['percentuale'] = grouped[x] / totali_y * 100

    grouped = grouped.sort_values(by='percentuale', ascending=False)

    fig= px.bar(grouped, x='percentuale', y=y, color=colore, barmode='stack', title=title, color_discrete_sequence=spezza_sequenza(colori, primo), orientation='h')
    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        plot_bgcolor='rgba(0,0,0,0)',
    )

    return fig

def crea_vuoto():
    fig = go.Figure()
    fig.add_annotation(
        text="⚠️Nessun dato disponibile per i filtri selezionati⚠️",
        xref="paper", yref="paper",
        showarrow=False,
        font=dict(size=16),
        x=0.5, y=0.5,
        align="center"
    )
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor='white'
    )
    return fig

def crea_tabella(df, righe, colonne, valore):
    pivot = pd.pivot_table(df, index=righe, columns=colonne, values=valore, aggfunc='sum', fill_value=0)

    percentuali = pivot.div(pivot.sum(axis=0), axis=1) * 100

    tabella_combinata = pivot.astype(float).round(2).astype(str)

    percentuali_formattate = percentuali.round(1).astype(str) + '%'


    tabella_combinata = tabella_combinata + ' (' + percentuali_formattate + ')'

    tabella_combinata = tabella_combinata.where((pivot != 0) & (pivot.notna()), "")

    if pivot.shape[1] == 2:
        anni = list(pivot.columns)
        anno1, anno2 = anni[0], anni[1]

        val_anno1 = pivot[anno1]
        val_anno2 = pivot[anno2]

        variazione_percentuale = ((val_anno2 - val_anno1) / val_anno1.replace(0, float('nan'))) * 100
        variazione_percentuale = variazione_percentuale.replace([float('inf'), -float('inf')], float('nan')).round(1)

        colonna_variazione = variazione_percentuale.apply(lambda x: f"+{x}%" if x > 0 else (f"{x}%" if pd.notna(x) else "")).fillna("")
        tabella_combinata["Variazione %"] = colonna_variazione

    tabella_combinata.reset_index(inplace=True)



    return tabella_combinata

