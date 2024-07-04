import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
import io
import streamlit as st
import plotly.express as px
from datetime import datetime, date
import zipfile


##########################################DOWNLOAD#####################################################################
# URLs dos dados de queimadas do INPE
url_ano_anteriores = 'https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/anual/Brasil_sat_ref/' # dados de 2003 - 2023
url_ano_atual = 'https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/mensal/Brasil/' # dados de 2024


#           ANOS ANTERIORES: focos_br_ref_2003.zip	

result = requests.get(url_ano_anteriores)                   # Make the connection
soup = BeautifulSoup(result.content, 'html.parser')         # Parse the HTML file
zip_files = soup.find_all('a', href=re.compile("\.zip"))    # Find all "zip" files in the server

df_2003_a_2023 = pd.DataFrame()                             # Create an empty dataframe

for zip_file in zip_files:
    filename = zip_file.get_text()
    url = f'{url_ano_anteriores}{filename}'
    print("O seguinte arquivo será baixado: ", filename)

    # envia uma requisição para a URL especificada
    myfile = requests.get(url)

    # lê o arquivo zip diretamente em um dataframe
    with zipfile.ZipFile(io.BytesIO(myfile.content)) as z:
        for zip_info in z.infolist():
            with z.open(zip_info) as f:
                df0 = pd.read_csv(f)
                # muda o nome da "latitude' para "lat" e "longitude" para "lon" do arquivo de 2023
                if filename == 'focos_br_ref_2023.zip':
                    df0.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)

                # junta a tabela que foi lida com a anterior
                df_2003_a_2023 = pd.concat([df_2003_a_2023, df0], ignore_index=True)

# remove colunas
df_2003_a_2023.drop(['id_bdq','foco_id','pais'], axis=1, inplace=True)

# renomeia coluna
df_2003_a_2023.rename(columns={'data_pas': 'data'}, inplace=True)

# reposiciona as colunas
df_2003_a_2023 = df_2003_a_2023[['data','lat','lon','municipio','estado','bioma']]

# mostra o dataframe
print(df_2003_a_2023)


#            ANO ATUAL: focos_mensal_br_202401.csv	

result = requests.get(url_ano_atual)                       
soup = BeautifulSoup(result.content, 'html.parser')        
csv_files = soup.find_all('a', href=re.compile("\.csv"))   

df_2024 = pd.DataFrame()                                   

for csv_file in csv_files:
    filename = csv_file.get_text()
    url = f'{url_ano_atual}{filename}'
    print("O seguinte arquivo será baixado: ", filename)

    # envia uma requisição para a URL especificada
    myfile = requests.get(url)

    # lê o arquivo csv diretamente em um dataframe
    df0 = pd.read_csv(io.StringIO(myfile.content.decode('utf-8')), usecols=['lat', 'lon', 'data_hora_gmt', 'satelite', 'municipio', 'estado', 'bioma'])

    # junta a tabela que foi lida com a anterior
    df_2024 = pd.concat([df_2024, df0], ignore_index=True)

# seleciona para o satélite de referência AQUA_M-T
df_2024 = df_2024[df_2024['satelite']=='AQUA_M-T']

# remove colunas
df_2024.drop(['satelite'], axis=1, inplace=True)

# renomeia coluna
df_2024.rename(columns={'data_hora_gmt': 'data'}, inplace=True)

# reposiciona as colunas
df_2024 = df_2024[['data','lat','lon','municipio','estado','bioma']]

# cria um dataframe combinado
df_total = pd.concat([df_2003_a_2023, df_2024], ignore_index=True)

df_total['data'] = pd.to_datetime(df_total['data'])

# seta a coluna data com o index do dataframe
df_total.set_index('data', inplace=True)

# coloca em ordem crescente de data
df_total.sort_values('data', inplace=True)

####################################################APP###########################################################

# sidebar
with st.sidebar:
    st.title('Filtros')
    st.divider()
    

    # seleciona o "ESTADO"
    estados = sorted(df_total['estado'].unique().tolist())
    estado_selecionado = st.selectbox('Selecione o **ESTADO**:', estados)

    # seleciona a "DATA"
    data_inicial = st.date_input('Digite a data **INICIAL**:', date(2002, 1, 1))
    data_final = st.date_input('Digite a data **FINAL**:')

    # filtra por Data
    df_filtrado = df_total.loc[str(data_inicial):str(data_final)]

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
