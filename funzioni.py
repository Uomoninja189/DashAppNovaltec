import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import re
from dash import html

colori = ['rgb(127, 60, 141)', 'rgb(17, 165, 121)', 'rgb(242, 183, 1)', 'rgb(57, 105, 172)', 'rgb(231, 63, 116)', 'rgb(128, 186, 90)', 'rgb(230, 131, 16)', 'rgb(0, 134, 149)', 'rgb(207, 28, 144)', 'rgb(249, 123, 114)', 'rgb(165, 170, 153)']

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

        aux['DATA '] = pd.to_datetime(aux['DATA '], errors='coerce')

        aux = aux[
            (aux['DATA '].dt.year == int(anno)) &
            (aux['DATA '].dt.month == mese_corrente)
        ]
        data = pd.concat([data, aux], ignore_index=True)

    
    data=pulisci_data(data)
    
    return data


def layout_base(children):
    return html.Div(
        children=children,
        style={'backgroundColor': '#dce2f0', 'width': '100%', 'minHeight': '100vh'}
    )

def filtro_anno(anno, data):
    return data[data['DATA '].dt.year == anno]

def filtro_agente(nomeAgente, data):
    return data[data['AGENTE'] == nomeAgente]

def filtro_settore(nomeSettore, data):
    return data[data['SETTORE ']==nomeSettore]
     

def filtro_origine(nomeOrigine, data):
    return data[data['Origine']==nomeOrigine]

def filtro_categoria(nomeCategoria, data):
    return data[data['CATEGORIA']==nomeCategoria]

def filtro_mese(mesi,data):
    mappa_mesi = {
        'Gen': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
        'Mag': 5, 'Giu': 6, 'Lug': 7, 'Ago': 8,
        'Set': 9, 'Ott': 10, 'Nov': 11, 'Dic': 12
    }
    
    def ottieni_numero_mese(nome_mese):
        mese_norm = nome_mese.strip().lower().capitalize()
        for mese, numero in mappa_mesi.items():
            if mese_norm.startswith(mese):
                return numero
        return None  # Se non trova corrispondenza
    
    mesi_numerici= [ottieni_numero_mese(mese) for mese in mesi]
    
    # Filtra il dataframe per i mesi numerici selezionati
    return data[data['DATA '].dt.month.isin(mesi_numerici)]


def pulisci_data(data):
    
    data=data.replace(r'^\s*$', pd.NA, regex=True)
    data['IMPONIBILE'] = pd.to_numeric(data['IMPONIBILE'], errors='coerce')
    
    data = data.dropna(subset=['IMPONIBILE'])
    

    data = data[~data.iloc[:, 1:].isna().all(axis=1)]

    for col in data.select_dtypes(include=['object', 'category']).columns:
        data[col] = data[col].apply(lambda x: str(x).strip().lower().capitalize() if pd.notna(x) else x)

    data['Q.'] = pd.to_numeric(data['Q.'], errors='coerce')  # DA CONTROLLARE SE IGNORA DATI
    data = data.rename(columns={'?': 'Origine'})
    data=riempi_vuoti(data)
    data['MOD']=data['MOD'].str.upper()
    data['Origine'] = data['Origine'].str.upper()
    data = data[~((data['IMPONIBILE'] == 0) | (data['IMPONIBILE'].isna()))]

    return data

def riempi_vuoti(data):
    data[['SETTORE ', 'MOD', 'AGENTE','Origine']] = data[['SETTORE ', 'MOD', 'AGENTE','Origine']].fillna("Sconosciuto")
    data['CATEGORIA']=data['CATEGORIA'].fillna('Acc')
    data['Q.'] = data['Q.'].fillna(1)   
    return data

def pulisci_mese(mesi):
    return [re.sub(r'[^\w\s]', '', mese).split()[0] for mese in mesi]

def aggiungi_colonna_tipo(data):
    data['Tipo'] = data.apply(
        lambda row: 
            'Effettuata' if str(row['FT. ']).startswith(('F', 'f')) 
            else 'Saltata' if str(row['FT. ']).strip().lower() == 'saltata' 
            else 'Altro', 
        axis=1
    )

    data['Tipo'] = data.apply(lambda row: 'Saltata' if str(row['NOTE']).startswith('saltata') else row['Tipo'], axis=1)
    order = ['Effettuata', 'Altro', 'Saltata']
    data['Tipo'] = pd.Categorical(data['Tipo'], categories=order, ordered=True)

    return data

def riordina_per_mese(data):
    mesi_dict = {
        1: 'Gennaio', 2: 'Febbraio', 3: 'Marzo', 4: 'Aprile',
        5: 'Maggio', 6: 'Giugno', 7: 'Luglio', 8: 'Agosto',
        9: 'Settembre', 10: 'Ottobre', 11: 'Novembre', 12: 'Dicembre'
    }

    data['Mese'] = data['DATA '].dt.month.map(mesi_dict)
    ordine_completo = list(mesi_dict.values())
    data['Mese'] = pd.Categorical(data['Mese'], categories=ordine_completo, ordered=True)

    return data

def riordina_per_anno(data):

    data['Anno'] = data['DATA '].dt.year
    data['Anno'] = pd.Categorical(data['Anno'], ordered=True)

    return data

def crea_torta(data, group, disc):
    
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
                color_discrete_sequence=colori,
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
                labels={'IMPONIBILE': 'Imponibile', 'AGENTE': 'Agente'},
                color_discrete_map={'Effettuata': '#2ecc71',  'Saltata': '#e74c3c',   'Altro': '#3498db'  },
                
                )

    #per impilare le barre
    fig.update_layout(
        barmode='stack')
    return fig

def crea_barre_multi_v(data, x, y, colore, title):
    grouped = data.groupby([x, colore])[y].sum().reset_index()

    return px.bar(grouped, x=x, y=y, color=colore, barmode='group', title=title, color_discrete_sequence=colori)
    
def crea_barre_multi_h(data, x, y, colore, title):
    grouped = data.groupby([y, colore])[x].sum().reset_index()

    totali_y = grouped.groupby(y)[x].transform('sum')

    # Aggiunge colonna percentuale
    grouped['percentuale'] = grouped[x] / totali_y * 100

    grouped = grouped.sort_values(by='percentuale', ascending=False)

    fig= px.bar(grouped, x='percentuale', y=y, color=colore, barmode='stack', title=title, color_discrete_sequence=colori, orientation='h')

    return fig


def crea_vuoto():
    fig = go.Figure()
    fig.add_annotation(
        text="⚠️ Nessun dato disponibile per i filtri selezionati.",
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