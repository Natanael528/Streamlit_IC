import streamlit as st
import pandas as pd
import datetime 
from datetime import datetime,timedelta
import leafmap.foliumap as leafmap


st.set_page_config(layout='wide',
                   page_icon=':fire:',
                   page_title='Unifei Queimadas',
                   initial_sidebar_state='expanded',
                   )

with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

st.logo('Logos/cropped-simbolo_RGB.png',
        link= 'https://meteorologia.unifei.edu.br')

####################################################################### Download dados #######################################################################
@st.cache_data 
def load_data(): #dados principais mensais 
    
    data = datetime.now().strftime("%Y%m")
    df = pd.read_csv(f'https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/mensal/Brasil/focos_mensal_br_{data}.csv', usecols=(['data_hora_gmt','lat','lon','satelite','bioma']))
    df = df.rename(columns={'data_hora_gmt':'Data','lat':'Lat','lon':'Lon','satelite':'Satelite','bioma':'Bioma'}) 
    df['Data'] = pd.to_datetime(df['Data'])
    df.set_index('Data', inplace=True)
     
    return df

def load_data2():
    dfs = []
    for i in range(0, 250, 10):
        data_anterior = datetime.now() - timedelta(minutes=i)
        
        # Arredondar o tempo para o múltiplo de 10 minutos
        data = data_anterior.replace(minute=(data_anterior.minute // 10) * 10, second=0, microsecond=0).strftime("%Y%m%d_%H%M")
        
        try: # Tentar carregar o CSV
            
            df = pd.read_csv(f'https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/10min/focos_10min_{data}.csv', usecols=(['data','lat', 'lon', 'satelite']))
            df = df.rename(columns={'data':'Data','lat':'Lat','lon':'Lon','satelite':'Satelite'})
            df['Data'] = pd.to_datetime(df['Data'])
            df.set_index('Data', inplace=True)

            dfs.append(df)
            
        except Exception as e:
            continue
        
        df = pd.concat(dfs)
    
    return dfs
##############################################################################################################################################################

with st.sidebar:
    periodo = st.radio('Selecione o Período do dado', ['Horário','Diário'])


if periodo == ('Diário'):
    
    st.title('Focos de queimadas diário')
        
    df1 = load_data()
    data = df1.groupby(pd.Grouper(freq='1D')).count()['Lat'].index

    data_formatada = data.strftime('%Y/%m/%d')[::-1]

    st.sidebar.divider()
    dataselec = st.sidebar.selectbox('Selecione o dia', options=data_formatada)
    st.subheader(f'Data: {dataselec}')
    df = df1[df1.index.floor('D').isin([dataselec])]                
   

    sat = df['Satelite'].unique().tolist()
    if 'AQUA_M-T' in sat:
        indice = sat.index('AQUA_M-T')
    elif 'AQUA_M-M' in sat:
        indice = sat.index('AQUA_M-M')
    else:
        indice = 0
    selec = st.sidebar.selectbox('Selecione um Satelite', sat, index= indice)
    dfiltrado = df[df['Satelite'] == selec]

    Map = leafmap.Map(center=[-15.7801, -47.9292], zoom=4, tiles='cartodbdark_matter')
    Map.add_points_from_xy(dfiltrado, x="Lon", y="Lat", layer_name="Marcadores")             
    Map.to_streamlit(width=1350, height=700)


elif periodo == ('Horário'):
    
    st.title('Focos de queimadas Horário')
    
# Supondo que load_data2() retorna uma lista de DataFrames
df2 = load_data2()

# Criar as abas
tab1, tab2, tab3, tab4, tab5 = st.tabs(["10 Min", "10 - 60 Min", "60 - 120 Min", "120 - 180 Min", "180 - 240 Min"])

with tab1:
    Map = leafmap.Map(center=[-15.7801, -47.9292], zoom=3, tiles='cartodbdark_matter')
    Map.add_points_from_xy(df2[0], x="Lon", y="Lat", layer_name="Marcadores") 
    Map.to_streamlit(width=1350, height=700)

with tab2:
    df_interval = pd.concat(df2[0:6], ignore_index=True)  # Concatena os DataFrames no intervalo
    Map = leafmap.Map(center=[-15.7801, -47.9292], zoom=3, tiles='cartodbdark_matter')
    Map.add_points_from_xy(df_interval, x="Lon", y="Lat", layer_name="Marcadores") 
    Map.to_streamlit(width=1350, height=700)

with tab3:
    df_interval = pd.concat(df2[0:12], ignore_index=True)
    Map = leafmap.Map(center=[-15.7801, -47.9292], zoom=3, tiles='cartodbdark_matter')
    Map.add_points_from_xy(df_interval, x="Lon", y="Lat", layer_name="Marcadores") 
    Map.to_streamlit(width=1350, height=700)

with tab4:
    df_interval = pd.concat(df2[0:18], ignore_index=True)
    Map = leafmap.Map(center=[-15.7801, -47.9292], zoom=3, tiles='cartodbdark_matter')
    Map.add_points_from_xy(df_interval, x="Lon", y="Lat", layer_name="Marcadores") 
    Map.to_streamlit(width=1350, height=700)

with tab5:
    df_interval = pd.concat(df2[0:24], ignore_index=True)
    Map = leafmap.Map(center=[-15.7801, -47.9292], zoom=3, tiles='cartodbdark_matter')
    Map.add_points_from_xy(df_interval, x="Lon", y="Lat", layer_name="Marcadores") 
    Map.to_streamlit(width=1350, height=700)