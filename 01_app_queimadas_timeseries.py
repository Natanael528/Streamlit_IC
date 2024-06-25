# importa bibliotecas
import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import numpy as np
import time
from datetime import datetime
import requests                  # HTTP library for Python
from bs4 import BeautifulSoup    # Pulling data out of HTML and XML files
import re                        # Regular expression operations
import io
import zipfile
# vamos ignorar vários avisos
import warnings
warnings.filterwarnings('ignore')


####################################################DOWNLOAD DOS DADOS###########################################################################################
# URLs dos dados de queimadas do INPE
url_ano_anteriores = 'https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/anual/Brasil_sat_ref/' # dados de 2003 - 2023
url_ano_atual = 'https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/mensal/Brasil/' # dados de 2024

# Função para baixar e ler arquivos ZIP diretamente para um DataFrame
def baixar_dados_zip(url_base):
    result = requests.get(url_base)
    soup = BeautifulSoup(result.content, 'html.parser')
    zip_files = soup.find_all('a', href=re.compile("\.zip"))
    
    dataframes = []
    for zip_file in zip_files:
        filename = zip_file.get_text()
        url = f'{url_base}{filename}'
        
        myfile = requests.get(url)
        with zipfile.ZipFile(io.BytesIO(myfile.content)) as z:
            for file_name in z.namelist():
                with z.open(file_name) as f:
                    df = pd.read_csv(f)
                    # Renomear colunas específicas se necessário
                    if 'focos*.zip' in filename:
                        df.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)
                    dataframes.append(df)
    
    return pd.concat(dataframes, ignore_index=True)

# Função para baixar e ler arquivos CSV diretamente para um DataFrame
def baixar_dados_csv(url_base):
    result = requests.get(url_base)
    soup = BeautifulSoup(result.content, 'html.parser')
    csv_files = soup.find_all('a', href=re.compile("\.csv"))
    
    dataframes = []
    for csv_file in csv_files:
        filename = csv_file.get_text()
        url = f'{url_base}{filename}'
        
        myfile = requests.get(url)
        df = pd.read_csv(io.StringIO(myfile.content.decode('utf-8')), usecols=['lat', 'lon', 'data_hora_gmt', 'satelite', 'municipio', 'estado', 'bioma'])
        dataframes.append(df)
    
    df = pd.concat(dataframes, ignore_index=True)
    return df[df['satelite'] == 'AQUA_M-T'].drop(columns=['satelite'])

# Baixar dados de 2003 a 2023
df_2003_a_2023 = baixar_dados_zip(url_ano_anteriores)

# remove colunas
df_2003_a_2023.drop(['id_bdq','foco_id','pais'], axis=1, inplace=True)
# renomeia coluna
df_2003_a_2023.rename(columns={'data_pas': 'data'}, inplace=True)
# reposiciona as colunas
df_2003_a_2023 = df_2003_a_2023[['data','lat','lon','municipio','estado','bioma']]



# Baixar dados de 2024
df_2024 = baixar_dados_csv(url_ano_atual)

# renomeia coluna
df_2024.rename(columns={'data_hora_gmt': 'data'}, inplace=True)
# reposiciona as colunas
df_2024 = df_2024[['data','lat','lon','municipio','estado','bioma']]



# Combinar os dados em um único DataFrame
df_final = pd.concat([df_2003_a_2023, df_2024], ignore_index=True)

####################################################APP###########################################################################################

# configuração da página
st.set_page_config(layout='wide', initial_sidebar_state='expanded')
#st.image("logo_queimadas.png", use_column_width=True)
st.title('Série Temporal de Focos de Calor')
# função que carrega a tabela de queimadas
@st.cache_data
def carregar_dados():
    # leitura do dataframe
    df = pd.read_csv(df_final)

    # insere a coluna data como DateTime no DataFrame
    df['data'] = pd.to_datetime(df['data'])

    # seta a coluna data com o index do dataframe
    df.set_index('data', inplace=True)

    # coloca em ordem crescente de data
    df = df.sort_values('data')
    
    return df

# sidebar
with st.sidebar:

    st.title('Filtros')
    st.divider()
    df = carregar_dados()

    # seleciona o "ESTADO"
    estados = sorted(df['estado'].unique().tolist())
    estado_selecionado = st.selectbox('Selecione o **ESTADO**:', estados)

    # seleciona a "DATA"
    data_inicial = st.date_input('Digite a data **INICIAL**:', datetime.date(2002, 1, 1))
    data_final = st.date_input('Digite a data **FINAL**:')

    # filtra por Data
    df_filtrado = df.loc[str(data_inicial):str(data_final)]

    # filtra por Estado  
    df_filtrado = df_filtrado[df_filtrado['estado'] == estado_selecionado]

# botão de exibbir gráfico
#if st.sidebar.button('Exibir Gráfico'):
    #st.dataframe(df_filtrado, use_container_width=True)

# mostra o estado
st.markdown(f'### Estado selecionado = {estado_selecionado}')

# esta parte será usada para os gráficos
col1, col2 = st.columns(2)  # Isto significa 2 
col3, col4 = st.columns(2)  # Isto significa 2 
# https://plotly.com/python/figure-labels/

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

#print(anual)
#print(anual.index.year)

# finalização do APP
st.sidebar.divider()
st.sidebar.markdown('Desenvolvido por [Prof. Enrique Mattos]("https://github.com/evmpython")')
