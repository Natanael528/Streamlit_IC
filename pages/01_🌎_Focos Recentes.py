import streamlit as st
import pandas as pd
from datetime import datetime
import leafmap.foliumap as leafmap
import pytz

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
    return df


with st.sidebar:
    periodo = st.radio('Selecione o Período do dado', ['Mês Atual', 'Ultimas 24 Horas'])


if periodo == 'Ultimas 24 Horas':
    
    st.title('Focos de Queimadas nas ultimas 24 horas')
    
    df1 = load_data()
    
    data = df1.groupby(pd.Grouper(freq='1H')).count()['lat'].tail(24).index     #filtra por hora e seleciona as ultimas 24horas 
    df = df1[df1.index.floor('H').isin(data)]                                   #floor('H') acha o valor no index mais proximo da data filtrada, isin filtra o index atras dos valores do filtro anterior
    
    on = st.sidebar.toggle("Selecionar o satelite")
    if on:      
        sat = df.satelite.unique().tolist() 
        selec = st.sidebar.selectbox('Satelite',sat)
        dfiltrado = df[df['satelite'] == selec]
    else:
        dfiltrado = df 
    # df1
    
    # Map = leafmap.Map(center=[-15.7801, -47.9292], zoom=4, tiles='cartodbdark_matter')
    # Map.add_points_from_xy(dfiltrado, x="lon", y="lat",value = 'frp', radius= 20)             #NAO FUNCIONA :(
    # Map.to_streamlit(height=700)
    

    Map = leafmap.Map(center=[-15.7801, -47.9292], zoom=4, tiles='cartodbdark_matter')
    Map.add_heatmap(dfiltrado, latitude="lat", longitude="lon",value = 'frp', radius= 10)
    Map.to_streamlit(width=1350, height=700)

else:
    
    st.title('Focos de Queimadas no mês atual')
        
    df1 = load_data()
    
    data = df1.groupby(pd.Grouper(freq='1D')).count()['lat'].index
    
    dataselec = st.sidebar.selectbox('selecione o dia', options= data)

    df = df1[df1.index.floor('D').isin([dataselec])]                 
   
    on = st.sidebar.toggle("Selecionar o satelite")
    if on:      
        sat = df.satelite.unique().tolist() 
        selec = st.sidebar.selectbox('Satelite',sat)
        dfiltrado = df[df['satelite'] == selec]
    else:
        dfiltrado = df  
    
    
    Map = leafmap.Map(center=[-15.7801, -47.9292], zoom=4, tiles='cartodbdark_matter')
    Map.add_heatmap(dfiltrado, latitude="lat", longitude="lon",value = 'frp', radius= 13)
    Map.to_streamlit(width=1350, height=700)    

