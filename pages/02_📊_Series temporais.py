import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

st.set_page_config(layout='wide',
                   page_icon=':fire:',
                   page_title='Unifei Queimadas',
                   initial_sidebar_state='expanded',
                   )
# Leitura arquivo css
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)
st.logo('Logos/cropped-simbolo_RGB.png',
        link= 'https://meteorologia.unifei.edu.br')

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
    
    return df

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False)

#carrega o dataframe
df = load_data()

# sidebar
with st.sidebar:
    rad = st.radio('Serie temporal',
                   ['Brasil','Por Estado'],
                   )
    if rad == 'Brasil':
        
        # seleciona a "DATA"
        anos_disponiveis = sorted(df.index.year.unique())
        
        st.sidebar.divider()
        data_inicial = st.selectbox('Ano inicial', anos_disponiveis)
        data_final = st.selectbox('Ano final', anos_disponiveis, index = 21)
        # filtra por Data
        df_filtrado = df.loc[str(data_inicial):str(data_final)]
        
        # filtra novo df para os tops 10 e 5 com base em um ano apenas
        df_filtrado2 = df_filtrado.loc[str(data_final):str(data_final)]


    else:
        # seleciona o "ESTADO"
        estados = sorted(df['estado'].unique().tolist())
        st.sidebar.divider()
        estado_selecionado = st.selectbox('Selecione o **ESTADO**:', estados)

        # Seleciona a "DATA"
        data_inicial = st.date_input('Data **INICIAL**:', datetime.date(2003, 1, 1))
        data_final = st.date_input('Data **FINAL**:', datetime.date(2024, 8, 16))

        # filtra por Data
        df_filtrado = df.loc[str(data_inicial):str(data_final)]

        # filtra por Estado  
        df_filtrado = df_filtrado[df_filtrado['estado'] == estado_selecionado]
        
        

# mostra o estado
if rad == 'Por Estado':
    st.title(f' Focos de Queimadas por Estado')
    st.subheader(f'Estado Selecionado: {estado_selecionado}')
else:
    st.title(f'Focos de Queimadas a Nível Brasil')


# esta parte será usada para os gráficos
col1, col2 = st.columns(2)  # Isto significa 2 
col3, col4 = st.columns(2)  # Isto significa 2 
col5, col6 = st.columns(2)
col7, col8, col9 = st.columns([2,6,2])

# DIÁRIO TOTAL
diaria = df_filtrado.groupby(pd.Grouper(freq='1D')).count()['lat']
fig_diaria = px.line(diaria, width=300, height=300)
fig_diaria.update_traces(line=dict(color='#FF902A'))
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
fig_anual.update_traces(line=dict(color='#FF902A'))
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
fig_mensal.update_traces(line=dict(color='#FF902A'))
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
mensal_climatologia = mensal.groupby(mensal.index.month).sum() #sum
fig_mensal_climatologia = px.bar(mensal_climatologia, width=300, height=300)
fig_mensal.update_traces(line=dict(color='#FF902A'))
fig_mensal_climatologia.update_layout(showlegend=False, xaxis_title="Mês", yaxis_title="Quantidade de Focos de Calor", 
                        title={'text': 'Total mensal',
                                'y': 0.93,
                                'x': 0.5,
                                'xanchor': 'center',
                                'yanchor': 'top',
                                'font_size': 20,
                                'font_color': 'white'})
col4.plotly_chart(fig_mensal_climatologia, use_container_width=True)

if rad == 'Brasil':
    
#focos por municipio
    df_filtrado['ano'] = df_filtrado.index.year
    queimadas_por_municipio = df_filtrado.groupby(['municipio']).size().reset_index(name='num_queimadas')
    top10municipio = queimadas_por_municipio.nlargest(10, 'num_queimadas')
    top10municipio = top10municipio.sort_values(by='num_queimadas', ascending=True)
    anoo = df_filtrado['ano'].unique()
    
    fig_max_municipio = px.bar(
        top10municipio, y='municipio', x='num_queimadas')
    
    fig_max_municipio.update_traces(line=dict(color='#FF902A'))
    fig_max_municipio.update_layout(showlegend=False, xaxis_title="Quantidade de Focos de Calor", yaxis_title="Cidades", title={'text': f'Top 10 Municípios<br><span style="color:rgba(250, 250, 250, 0.644); font-size:16px;">Período: {anoo.min()} à {anoo.max()}</span>',
               'y': 0.93,
               'x': 0.5,
               'xanchor': 'center',
               'yanchor': 'top',
               'font_size': 20,
               'font_color': 'white'})
    col5.plotly_chart(fig_max_municipio, use_container_width=False, width=400, height=300)



#focos por estado
    df_filtrado['ano'] = df_filtrado.index.year
    queimadas_por_estado = df_filtrado.groupby(['estado']).size().reset_index(name='num_queimadas')
    top10estados = queimadas_por_estado.nlargest(10, 'num_queimadas')
    top10estados = top10estados.sort_values(by='num_queimadas', ascending=True)
    anoo = df_filtrado['ano'].unique()
    
    fig_max_estado = px.bar(
        top10estados, y='estado', x='num_queimadas',)
    fig_max_estado.update_traces(line=dict(color='#FF902A'))
    fig_max_estado.update_layout(showlegend=False, xaxis_title="Quantidade de Focos de Calor", yaxis_title="Estado", title={'text': f'Top 10 Estados<br><span style="color:rgba(250, 250, 250, 0.644); font-size:16px;">Período: {anoo.min()} à {anoo.max()}</span>',
               'y': 0.93,
               'x': 0.5,
               'xanchor': 'center',
               'yanchor': 'top',
               'font_size': 20,
               'font_color': 'white'})
    col6.plotly_chart(fig_max_estado, use_container_width=False, width=400, height=300)


#focos por bioma

    df_filtrado['ano'] = df_filtrado.index.year
    queimadas_por_bioma = df_filtrado.groupby(['bioma']).size().reset_index(name='num_queimadas')
    top10bioma = queimadas_por_bioma.nlargest(5, 'num_queimadas')
    top10bioma = top10bioma.sort_values(by='num_queimadas', ascending=True)
    
    anoo = df_filtrado['ano'].unique()
    
    fig_max_bioma = px.bar(
        top10bioma, y='bioma', x='num_queimadas')
    fig_max_bioma.update_traces(line=dict(color='#FF902A'))
    fig_max_bioma.update_layout(showlegend=False, xaxis_title="Quantidade de Focos de Calor", yaxis_title="Bioma", title={'text': f'Top 5 Biomas<br><span style="color:rgba(250, 250, 250, 0.644); font-size:16px;">Período: {anoo.min()} à {anoo.max()}</span>',
               'y': 0.93,
               'x': 0.5,
               'xanchor': 'center',
               'yanchor': 'top',
               'font_size': 20,
               'font_color': 'white'})
    col8.plotly_chart(fig_max_bioma, use_container_width=False, width=400, height=300)
    
else:
    
    #focos por municipio

    df_filtrado['ano'] = df_filtrado.index.year
    queimadas_por_municipio = df_filtrado.groupby(['municipio']).size().reset_index(name='num_queimadas')
    top10municipio = queimadas_por_municipio.nlargest(10, 'num_queimadas')
    top10municipio = top10municipio.sort_values(by='num_queimadas', ascending=True)
    anoo = df_filtrado['ano'].unique()

    fig_max_municipio = px.bar(
        top10municipio, y='municipio', x='num_queimadas')
    fig_max_municipio.update_traces(line=dict(color='#FF902A'))
    fig_max_municipio.update_layout(showlegend=False, xaxis_title="Quantidade de Focos de Calor", yaxis_title="Cidades", title={'text': f'Top 10 Municípios<br><span style="color:rgba(250, 250, 250, 0.644); font-size:16px;">Período: {anoo.min()} à {anoo.max()}</span>',
                'y': 0.93,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font_size': 20,
                'font_color': 'white'})
    col8.plotly_chart(fig_max_municipio, use_container_width=False, width=400, height=300)
        