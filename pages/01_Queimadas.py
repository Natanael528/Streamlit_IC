import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from streamlit_folium import st_folium
import leafmap.foliumap as leafmap
import folium
import numpy as np


# ==============================================================================================================#
#                                     DEFINE FUNÇÕES
# ==============================================================================================================#
@st.cache_data
def load_data():
    # Lendo todos os dataframes
    df_lat = pd.read_csv('dados/lat.csv', compression='zip')
    df_lon = pd.read_csv('dados/lon.csv', compression='zip')
    df_municipios = pd.read_csv('dados/municipios.csv', compression='zip')
    df_estados = pd.read_csv('dados/estados.csv', compression='zip')
    df_biomas = pd.read_csv('dados/biomas.csv', compression='zip')
    
    # Normalizando latitude e longitude
    df_lat['lat'] = df_lat['lat'] / 10000
    df_lon['lon'] = df_lon['lon'] / 10000
    
    # Primeiro DataFrame
    df = pd.concat([df_lat, df_lon, df_municipios, df_estados, df_biomas], axis=1)
    df['data'] = pd.to_datetime(df['data'])
    df.set_index('data', inplace=True)
    df = df.sort_values('data')
    
        # Concatenar os DataFrames
    df_total = pd.concat([df_estados, df_lat, df_lon, df_municipios, df_biomas], axis=1)

    # Transformar a coluna "data" para o formato "datetime"
    df_total['data'] = pd.to_datetime(df_total['data'])

    # Setar a coluna "data" como o índice da tabela
    df_total.set_index('data', inplace=True)

    # Criar a coluna ano
    df_total['ano'] = df_total.index.year

    # Agrupar os dados por estado e ano, calculando as médias de latitude e longitude, e a quantidade de queimadas
    df2 = df_total.groupby(['estado', 'ano']).agg({
        'lat': 'mean',
        'lon': 'mean',
        'municipio': 'count'
    }).reset_index()

    # Renomear as colunas para clareza
    df2.rename(columns={'municipio': 'queimadas'}, inplace=True)

    # Ordenar o DataFrame pelo estado e ano
    df2.sort_values(by=['estado', 'ano'], inplace=True)
    
    return df, df2

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False)
  
###############################################################################################################

# configuração da página
st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

# load Style css
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

#adiciona logo
st.logo('Logos/cropped-simbolo_RGB.png',
        link= 'https://meteorologia.unifei.edu.br')

st.title('Série Temporal de Focos de Calor')  
tab1, tab2 ,tab3 = st.tabs(["Mapa maiores ocorrencias", 'Localização',"Tabela" ])

#carrega o dataframe
df,df2 = load_data()


df_filtrado
with tab1:
    
    # Seleção do ano
    anos_disponiveis = sorted(df2['ano'].unique())
    ano_selecionado = st.select_slider('Selecione o Ano:', options=anos_disponiveis, value=anos_disponiveis[0])
    df2_filtrado = df2[(df2['ano'] == ano_selecionado)]
    
    m = leafmap.Map(center=[-15.7801, -47.9292], zoom=4, tiles='cartodbdark_matter')
    m.add_heatmap(
        df2_filtrado,
        latitude="lat",
        longitude="lon",
        value="queimadas",
        name="Heat map",
        radius=40,
    )
    m.to_streamlit(width=1750, height=700)




# sidebar
with st.sidebar:

    st.title('Filtros')
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
with tab2: 

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

    
    

####################################################GRAFICOS###########################################################
with tab3:
    # mostra o estado
    st.markdown(f'### Estado selecionado = {estado_selecionado}')

    # esta parte será usada para os gráficos
    col1, col2 = st.columns(2)  # Isto significa 2 
    col3, col4 = st.columns(2)  # Isto significa 2 

    # DIÁRIO TOTAL
    diaria = df_filtrado.groupby(pd.Grouper(freq='1D')).count()['lat']
    fig_diaria = px.line(diaria, width=300, height=300)
    fig_diaria.update_traces(line=dict(color='#F11965'))
    fig_diaria.update_layout(showlegend=False,  xaxis_title="Mês/Ano", yaxis_title="Quantidade de Focos de Calor", 
                            title={'text': 'Diária',
                                    'y': 0.93,
                                    'x': 0.5,
                                    'xanchor': 'center',
                                    'yanchor': 'top',
                                    'font_size': 20,
                                    'font_color': 'white'})
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
                                  'font_color': 'white'})
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
                                    'font_color': 'white'})
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
                                    'font_color': 'white'})
    col4.plotly_chart(fig_mensal_climatologia, use_container_width=True)



with st.sidebar:
    #botao de download
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button("Download CSV",             #Nome do botao
                       csv,                        #Dataset escolhido
                       "dataframe_2003_atual.csv", #Nome pro arquivo
                       "text/csv")                 #Informação do dataset
