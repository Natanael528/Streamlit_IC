import streamlit as st
import pandas as pd
from datetime import datetime,timedelta
import leafmap.foliumap as leafmap


st.set_page_config(layout='wide',
                   page_icon=':fire:',
                   page_title='Unifei Queimadas',
                   initial_sidebar_state='collapsed',
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
    for i in range(0, 50, 10):
        data_anterior = datetime.now() - timedelta(hours=-3,minutes=i)
        
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

def convert_df(dfd): #converter arquivos para donwload
    return dfd.to_csv().encode("utf-8")
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

    Map = leafmap.Map(center=[-19, -60], zoom=4, tiles='cartodbdark_matter')
    Map.add_points_from_xy(dfiltrado, x="Lon", y="Lat", layer_name="Marcadores")             
    Map.to_streamlit(width=1500, height=700)
    
    csv = convert_df(dfiltrado)
    st.sidebar.download_button(label="Download CSV", data = csv, file_name= f'{selec}_{dataselec}.csv') #botao de donwload dos dados selecionados

else:
    st.title('Focos de queimadas Horário')  
     
    col1, col2 = st.columns([8, 1.4], vertical_alignment="bottom") #divide a pagina em duas colunas com tamanhos diferentes

    df2 = load_data2()
    
    selected_dfs = []
    with col2: #deixa no canto direito as selectboxs 
        st.divider()
        st.text('Selecione o Período')

        min1 = st.checkbox("10 Min", value=True)
        if min1:
            selected_dfs.append(df2[0])

        min2 = st.checkbox("20 Min")
        if min2:
            selected_dfs.append(df2[1])

        min3 = st.checkbox("30 Min")
        if min3:
            selected_dfs.append(df2[2])

        min4 = st.checkbox("40 Min")
        if min4:
            selected_dfs.append(df2[3])

        min5 = st.checkbox("50 Min")
        if min5:
            selected_dfs.append(df2[4])

        st.divider()

    # Concatenar todos os DataFrames
    if selected_dfs:
        concatenated_df = pd.concat(selected_dfs, ignore_index=True)

        # acessar a coluna 'Satelite'
        sat = concatenated_df['Satelite'].unique().tolist()
        selec = st.sidebar.selectbox('Selecione um Satelite', sat)
        dfiltrado = concatenated_df[concatenated_df['Satelite'] == selec]

        Map = leafmap.Map(center=[-19, -60], zoom=4, tiles='cartodbdark_matter')

        Map.add_points_from_xy(dfiltrado, x="Lon", y="Lat", layer_name="Marcadores")

        with col1:
            Map.to_streamlit(width=1450, height=775)