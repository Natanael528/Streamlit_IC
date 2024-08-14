import streamlit as st
import pandas as pd
import datetime 
from datetime import datetime
from streamlit_folium import st_folium
import folium
import leafmap.foliumap as leafmap


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
    data = datetime.now().strftime("%Y%m")
    df = pd.read_csv(f'https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/mensal/Brasil/focos_mensal_br_{data}.csv')
    df['data'] = pd.to_datetime(df['data_hora_gmt'])
    df.drop(['id',
            'municipio_id',
            'estado_id',
            'pais_id',
            'numero_dias_sem_chuva',
            'precipitacao',
            'data_hora_gmt'], inplace=True, axis= 1 )
    df.fillna(0, inplace=True)
    df.set_index('data',inplace=True)
    df = df[['lat','lon','satelite','pais','estado','municipio','bioma','risco_fogo','frp']]   
    df = df.rename(columns={'lat':'Lat','lon':'Lon','satelite':'Satelite','pais':'País','estado':'Estado','municipio':'Município','bioma':'Bioma','risco_fogo':'Risco de fogo','frp':'frp'})   
    return df


with st.sidebar:
    periodo = st.radio('Selecione o Período do dado', ['Diário', 'Ultimas 24 Horas'])


if periodo == 'Ultimas 24 Horas':
    
    st.title('Focos de Queimadas nas ultimas 24 horas')
    
    df1 = load_data()
    
    data = df1.groupby(pd.Grouper(freq='1H')).count()['Lat'].tail(24).index     #filtra por hora e seleciona as ultimas 24horas 
    df = df1[df1.index.floor('1H').isin(data)]                                   #floor('H') acha o valor no index mais proximo da data filtrada, isin filtra o index atras dos valores do filtro anterior
    
    st.sidebar.divider()

    sat = df['Satelite'].unique().tolist()
    # Verifica se 'AQUA_M-T' ou 'AQUA_M-M' está na lista
    if 'AQUA_M-T' in sat:
        indice = sat.index('AQUA_M-T')
    elif 'AQUA_M-M' in sat:
        indice = sat.index('AQUA_M-M')
    else:
        indice = 0
        
    # Seleciona o satélite
    selec = st.sidebar.selectbox('Selecione um Satélite', sat, index= indice)
    dfiltrado = df[df['Satelite'] == selec]
    
    #teste leafmap
    Map = leafmap.Map(center=[-15.7801, -47.9292], zoom=4, tiles='cartodbdark_matter')
    Map.add_points_from_xy(dfiltrado, x="Lon", y="Lat", layer_name="Marcadores") 
    Map.to_streamlit(width=1350, height=700)

else:
    
    st.title('Focos de queimadas diário')
    
        
    df1 = load_data()
    data = df1.groupby(pd.Grouper(freq='1D')).count()['Lat'].index
    data_formatada = data.strftime('%Y/%m/%d')
    
    ultimo_indice = len(data_formatada) - 1
    st.sidebar.divider()
    dataselec = st.sidebar.selectbox('Selecione o dia', options= data_formatada, index=ultimo_indice)
    st.subheader(f'Data: {dataselec}')
    df = df1[df1.index.floor('D').isin([dataselec])]                 
   

    sat = df['Satelite'].unique().tolist()

    # Verifica se 'AQUA_M-T' ou 'AQUA_M-M' está na lista
    if 'AQUA_M-T' in sat:
        indice = sat.index('AQUA_M-T')
    elif 'AQUA_M-M' in sat:
        indice = sat.index('AQUA_M-M')
    else:
        indice = 0
    selec = st.sidebar.selectbox('Selecione um Satelite', sat, index= indice)
    dfiltrado = df[df['Satelite'] == selec]


    Map = leafmap.Map(center=[-15.7801, -47.9292], zoom=4, tiles='cartodbdark_matter')
    Map.add_points_from_xy(dfiltrado, x="Lon", y="Lat", layer_name="Marcadores")             #NAO FUNCIONA :(
    Map.to_streamlit(width=1350, height=700)


