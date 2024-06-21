import requests
import zipfile
import os
import pandas as pd
import datetime
import streamlit as st
import plotly.express as px
from io import BytesIO
from bs4 import BeautifulSoup
from streamlit_folium import st_folium
import folium

# Função para listar arquivos zip a partir de uma página HTML
def list_zip_files(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        zip_files = [url + '/' + a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.zip')]
        return zip_files
    else:
        print(f"Falha ao acessar {url}")
        return []

# Função para baixar e descompactar um arquivo zip
def download_and_extract_zip(url, extract_to='data'):
    response = requests.get(url)
    if response.status_code == 200:
        with zipfile.ZipFile(BytesIO(response.content)) as thezip:
            thezip.extractall(path=extract_to)
    else:
        print(f"Falha ao baixar {url}")

# Função para ler e processar arquivos descompactados
def process_data(extract_to='data'):
    all_files = [os.path.join(extract_to, f) for f in os.listdir(extract_to) if f.endswith('.csv')]
    dataframes = []
    for file in all_files:
        df = pd.read_csv(file)
        dataframes.append(df)
    combined_df = pd.concat(dataframes, ignore_index=True)
    combined_df['data'] = pd.to_datetime(combined_df['data'])
    combined_df.set_index('data', inplace=True)
    combined_df.sort_values('data', inplace=True)
    return combined_df

# Função principal para executar o pipeline de download e processamento
def main_download_process():
    urls = [
        'https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/anual/Brasil_sat_ref/',
        'https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/mensal/Brasil/'
    ]
    
    os.makedirs('data', exist_ok=True)

    for url in urls:
        zip_files = list_zip_files(url)
        for zip_file in zip_files:
            download_and_extract_zip(zip_file)
    
    dataset = process_data()
    dataset.to_csv('combined_dataset.csv', index=False)
    print("Dataset combinado salvo como 'combined_dataset.csv'")

# Executa o processo de download e processamento
main_download_process()

# Configuração da página do Streamlit
st.set_page_config(layout='wide', initial_sidebar_state='expanded')
st.title('Série Temporal de Focos de Calor')

# Função que carrega a tabela de queimadas
@st.cache_data
def carregar_dados():
    df = pd.read_csv('combined_dataset.csv')

    # Insere a coluna data como DateTime no DataFrame
    df['data'] = pd.to_datetime(df['data'])

    # Seta a coluna data com o index do dataframe
    df.set_index('data', inplace=True)

    # Coloca em ordem crescente de data
    df = df.sort_values('data')
    
    return df

# Sidebar
with st.sidebar:
    st.title('Filtros')
    st.divider()
    df = carregar_dados()

    # Seleciona o "ESTADO"
    estados = sorted(df['estado'].unique().tolist())
    estado_selecionado = st.selectbox('Selecione o **ESTADO**:', estados)

    # Seleciona a "DATA"
    data_inicial = st.date_input('Digite a data **INICIAL**:', datetime.date(2002, 1, 1))
    data_final = st.date_input('Digite a data **FINAL**:')

    # Filtra por Data
    df_filtrado = df.loc[str(data_inicial):str(data_final)]

    # Filtra por Estado  
    df_filtrado = df_filtrado[df_filtrado['estado'] == estado_selecionado]

# Mostra o estado
st.markdown(f'### Estado selecionado = {estado_selecionado}')

# Esta parte será usada para os gráficos
col1, col2 = st.columns(2)  
col3, col4 = st.columns(2)  

# DIÁRIO TOTAL
diaria = df_filtrado.groupby(pd.Grouper(freq='1D')).count()['lat']
fig_diaria = px.line(diaria, width=300, height=300)
fig_diaria.update_layout(showlegend=False, xaxis_title="Mês/Ano", yaxis_title="Quantidade de Focos de Calor", 
                         title={'text': 'Diária',
                                'y': 0.93,
                                'x': 0.5,
                                'xanchor': 'center',
                                'yanchor': 'top',
                                'font_size': 20,
                                'font_color': 'red'})
col1.plotly_chart(fig_diaria, use_container_width=True)

# ANUAL TOTAL 
anual = df_filtrado.groupby(pd.Grouper(freq='1YE')).count()['lat']
fig_anual = px.bar(x=anual.index.year, y=anual.values, width=300, height=300)
fig_anual.update_layout(showlegend=False, xaxis_title="Ano", yaxis_title="Quantidade de Focos de Calor", 
                        title={'text': 'Anual',
                               'y': 0.93,
                               'x': 0.5,
                               'xanchor': 'center',
                               'yanchor': 'top',
                               'font_size': 20,
                               'font_color': 'red'})
col2.plotly_chart(fig_anual, use_container_width=True)

# MENSAL TOTAL
mensal = df_filtrado.groupby(pd.Grouper(freq='1ME')).count()['lat']
fig_mensal = px.line(mensal, width=300, height=300)
fig_mensal.update_layout(showlegend=False, xaxis_title="Mês/Ano", yaxis_title="Quantidade de Focos de Calor", 
                         title={'text': 'Mensal',
                                'y': 0.93,
                                'x': 0.5,
                                'xanchor': 'center',
                                'yanchor': 'top',
                                'font_size': 20,
                                'font_color': 'red'})
col3.plotly_chart(fig_mensal, use_container_width=True)

# MENSAL MÉDIO
mensal_climatologia = mensal.groupby(mensal.index.month).mean()
fig_mensal_climatologia = px.bar(mensal_climatologia, width=300, height=300)
fig_mensal_climatologia.update_layout(showlegend=False, xaxis_title="Mês", yaxis_title="Quantidade de Focos de Calor", 
                         title={'text': 'Mensal Média',
                                'y': 0.93,
                                'x': 0.5,
                                'xanchor': 'center',
                                'yanchor': 'top',
                                'font_size': 20,
                                'font_color': 'red'})
col4.plotly_chart(fig_mensal_climatologia, use_container_width=True)

# Finalização do APP
st.sidebar.divider()
st.sidebar.markdown('Desenvolvido por [Prof. Enrique Mattos]("https://github.com/evmpython")')
