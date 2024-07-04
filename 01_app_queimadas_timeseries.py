import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import io
import streamlit as st
import plotly.express as px
from datetime import datetime, date
import zipfile
import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from streamlit_folium import st_folium
import folium
import numpy as np

# ==============================================================================================================#
#                                     DEFINE FUNÇÕES
# ==============================================================================================================#
# Cache the conversion to prevent computation on every rerun
# Função que carrega os dados de focos tabulares


@st.cache_data
def load_data():

    # leitura do dataframe
    # df = pd.read_csv(
    #    'C:/Users/enriq/Downloads/PROCESSAMENTO_PYTHON/dashboards/01_queimadas/focos_br_AQUA_2003_2024.csv', compression='zip')

    # lendo todos dataframes
    df_lat = pd.read_csv(
        'dados/lat.csv', compression='zip')
    df_lon = pd.read_csv(
        'dados/lon.csv', compression='zip')
    df_municipios = pd.read_csv(
        'dados/municipios.csv', compression='zip')
    df_estados = pd.read_csv(
        'dados/estados.csv', compression='zip')
    df_biomas = pd.read_csv(
        'dados/biomas.csv', compression='zip')
    
    df_lat['lat'] = df_lat['lat'] / 10000
    df_lon['lon'] = df_lon['lon'] / 10000

    # junta
    df = pd.concat([df_lat, df_lon, df_municipios,
                   df_estados, df_biomas], axis=1)

    # insere a coluna data como DateTime no DataFrame
    df['data'] = pd.to_datetime(df['data'])

    # seta a coluna data com o index do dataframe
    df.set_index('data', inplace=True)

    # coloca em ordem crescente de data
    df = df.sort_values('data')

    return df

# Função que tranforma dataframe para CSV


@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")
    
####################################################APP###########################################################

# configuração da página
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# load Style css
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

#adiciona logo
st.logo('cropped-simbolo_RGB.png',
        link= 'https://meteorologia.unifei.edu.br')

st.title('Série Temporal de Focos de Calor')  
tab1, tab2 = st.tabs(["Mapa de Distribuição","Tabela" ])

#carrega o dataframe
df = load_data()
# sidebar
with st.sidebar:

    st.title('Filtros')
    st.divider()

    # seleciona o "ESTADO"
    estados = sorted(df['estado'].unique().tolist())
    estado_selecionado = st.selectbox('Selecione o **ESTADO**:', estados)

    # seleciona a "DATA"
    data_inicial = st.date_input('Data **INICIAL**:', datetime.date(2024, 1, 1))
    data_final = st.date_input('Data **FINAL**:')

    # filtra por Data
    df_filtrado = df.loc[str(data_inicial):str(data_final)]

    # filtra por Estado  
    df_filtrado = df_filtrado[df_filtrado['estado'] == estado_selecionado]

# Aba do Mapa de Distribuição
with tab1:
# Criando o mapa
    m = folium.Map(location=[-15.7801, -47.9292], zoom_start=4, tiles='cartodbdark_matter')

    # Iterando sobre o DataFrame
    for i, row in df_filtrado.iterrows():
        folium.CircleMarker(location=[row['lat'], row['lon']],
                            radius=2,  # Tamanho menor do marcador
                            fill=True,
                            color='red',  # Cor vermelha
                            fill_color='red').add_to(m)  # Cor de preenchimento vermelha

    # Exibindo o mapa com Streamlit
    st_folium(m, width=1500, height=800)

with tab2:
    # mostra o estado
    st.markdown(f'### Estado selecionado = {estado_selecionado}')

    # esta parte será usada para os gráficos
    col1, col2 = st.columns(2)  # Isto significa 2 
    col3, col4 = st.columns(2)  # Isto significa 2 
    # https://plotly.com/python/figure-labels/

    # DIÁRIO TOTAL
    diaria = df_filtrado.groupby(pd.Grouper(freq='1D')).count()['lat']
    fig_diaria = px.line(diaria, width=300, height=300)
    fig_diaria.update_traces(line=dict(color='white'))
    fig_diaria.update_layout(showlegend=False,  xaxis_title="Mês/Ano", yaxis_title="Quantidade de Focos de Calor", 
                            title={'text': 'Diária',
                                    'y': 0.93,
                                    'x': 0.5,
                                    'xanchor': 'center',
                                    'yanchor': 'top',
                                    'font_size': 20,
                                    'font_color': '#FF902A'})
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
                                  'font_color': '#FF902A'})
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
                                    'font_color': '#FF902A'})
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
                                    'font_color': '#FF902A'})
    col4.plotly_chart(fig_mensal_climatologia, use_container_width=True)



with st.sidebar:
    #botao de download
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV",             #Nome do botao
                       csv,                        #Dataset escolhido
                       "dataframe_2003_atual.csv", #Nome pro arquivo
                       "text/csv")                 #Informação do dataset



# finalização do APP
st.sidebar.divider()
