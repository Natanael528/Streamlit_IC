import streamlit as st
import pandas as pd
from datetime import datetime,timedelta
import leafmap.foliumap as leafmap
import folium


st.set_page_config(layout='wide',
                   page_icon=':fire:',
                   page_title='FireScope',
                   initial_sidebar_state='expanded',
                   )

with open('GIT/Streamlit_IC/pages/style-foco.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

st.logo('GIT/Streamlit_IC/Logos/logomaior.png', icon_image='GIT/Streamlit_IC/Logos/logomaior.png',
        size= 'large',
        link= 'https://meteorologia.unifei.edu.br')

####################################################################### Download dados Por Funções ###########################################################
@st.cache_data 

def load_data():
    dfs = {}  # Dicionário para armazenar DataFrames com a data como chave
    for i in range(0, 7, 1):

        data_anterior = datetime.now() - timedelta(days=i)

        data_str_file = data_anterior.strftime("%Y%m%d") #DATA PARA BAIXAR OS DADOS
        data_str_key = data_anterior.strftime("%Y/%m/%d")#DATA PARA SELECIONAR AS CHAVES DO DICIONARIO
        
        df = pd.read_csv(f'https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/diario/Brasil/focos_diario_br_{data_str_file}.csv',
                         usecols=(['data_hora_gmt', 'lat', 'lon', 'satelite','municipio', 'bioma', 'frp']))
        
        df = df.rename(columns={'data_hora_gmt':'Data', 'lat':'Lat', 'lon':'Lon', 'satelite':'Satélite','municipio':'Município','bioma':'Bioma', 'frp':'FRP'})
        
        df['Data'] = pd.to_datetime(df['Data'])
        df.set_index('Data', inplace=True)
        
        
        dfs[data_str_key] = df # Armazena o DataFrame no dicionário
    
    return dfs


def load_data2():
    dfs = []
    last_data = datetime.now() - timedelta(hours=3)
    last_data2 = last_data.replace(minute=(last_data.minute // 10) * 10, second=0, microsecond=0) 
    for i in range(0, 50, 10):
        data_anterior = datetime.now() - timedelta(hours=0,minutes=i)
        
        data = data_anterior.replace(minute=(data_anterior.minute // 10) * 10, second=0, microsecond=0).strftime("%Y%m%d_%H%M")# Arredondar o tempo para o múltiplo de 10 minutos
        print (data)
        try: # Tentar carregar o CSV
            
            df = pd.read_csv(f'https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/10min/focos_10min_{data}.csv', usecols=(['data','lat', 'lon', 'satelite']))
            df = df.rename(columns={'data':'Data','lat':'Lat','lon':'Lon','satelite':'Satélite'})
            df['Data'] = pd.to_datetime(df['Data'])
            df['Data'] = df['Data'] - pd.to_timedelta(3, unit='h')
            df['Hora'] = df['Data'].dt.time
            df.set_index('Data', inplace=True)

            dfs.append(df)
            
        except Exception as e:
            empty_df = pd.DataFrame(columns=['Data', 'Lat', 'Lon', 'Satélite', 'Hora'])
            dfs.append(empty_df)
        df = pd.concat(dfs)

    return dfs , last_data2

def convert_df(dfd): #converter arquivos para donwload
    return dfd.to_csv().encode("utf-8")

##############################################################################################################################################################

with st.sidebar:
    periodo = st.radio('Selecione o Período do dado', ['Recentes (10-50 Min)','Últimos 7 dias'])
######FIGURAS ULTIMOS 7 DIAS######
if periodo == ('Últimos 7 dias'):

    st.title('Focos de queimadas diário nos últimos 7 dias')
        
    df1= load_data()
    datas = list(df1.keys())#no uso de dicionario, para pegar as chaves de cada dataset
    
    st.sidebar.divider()
    index_selec = st.sidebar.selectbox('Selecione o dia', options=datas)

    df = df1.get(index_selec)  #usando a chave selecionada pelo selectbox agora define o dataset exato 
               
######SELECIONA OS DADOS######
    sat = df['Satélite'].unique().tolist()
    if 'AQUA_M-T' in sat:
        indice = sat.index('AQUA_M-T')
    elif 'AQUA_M-M' in sat:
        indice = sat.index('AQUA_M-M')
    else:
        indice = 0
    selec = st.sidebar.selectbox('Selecione o Satélite', sat, index= indice)
    dfiltrado = df[df['Satélite'] == selec]
    
######PLOTA FIGURA######
    Map = leafmap.Map(center=[-19, -60], zoom=4, tiles='cartodbdark_matter')
    Map.add_points_from_xy(dfiltrado, x="Lon", y="Lat", layer_name="Marcadores")             
    Map.to_streamlit(width=1500, height=700)
    
    csv = convert_df(dfiltrado)
    st.sidebar.download_button(label="Download CSV", data = csv, file_name= f'{selec}_{index_selec}.csv') #botao de donwload dos dados selecionados

else:
######FIGURAS POR 10 MINUTOS######
    st.title('Focos de queimadas Horário (10-50 Min)')  
     
    col1, col2 = st.columns([9, 1.4], vertical_alignment="top") #divide a pagina em duas colunas com tamanhos diferentes

    df2 , last_data = load_data2()

    selected_dfs = []
    
    colors = ["red", "orange", "green", "blue", "purple"]  # Cores para diferenciar os DataFrames
    
    with col2:
        st.divider()
        st.markdown("**Focos de incêndio**")

        min1 = st.checkbox(":red[***Últimos 10 Minutos***]", value=True)
        if min1:
            df2[0]['color'] = colors[0]  # Adiciona cor ao DataFrame
            selected_dfs.append(df2[0])
        min2 = st.checkbox(":orange[***Últimos 20 Minutos***]")
        if min2:
            df2[1]['color'] = colors[1]  
            selected_dfs.append(df2[1])

        min3 = st.checkbox(":green[***Últimos 30 Minutos***]")
        if min3:
            df2[2]['color'] = colors[2] 
            selected_dfs.append(df2[2])

        min4 = st.checkbox(":blue[***Últimos 40 Minutos***]")
        if min4:
            df2[3]['color'] = colors[3] 
            selected_dfs.append(df2[3])

        min5 = st.checkbox(":violet[***Últimos 50 Minutos***]")
        if min5:
            df2[4]['color'] = colors[4]
            selected_dfs.append(df2[4])  
        
        st.markdown("**Última atualização:**")  
        st.markdown(last_data)
        st.divider()
        
######SELEÇÃO DOS SATELITES######
    if selected_dfs:# Concatenar todos os DataFrames
        concatenated_df = pd.concat(selected_dfs, ignore_index=True)

        sat = concatenated_df['Satélite'].unique().tolist()
        sat.insert(0, 'Todos Satélites')
        selec = st.sidebar.selectbox('Selecione o Satélite', sat)

        if selec == 'Todos Satélites':
            dfiltrado = concatenated_df  # Sem filtragem
        else:
            dfiltrado = concatenated_df[concatenated_df['Satélite'] == selec]
          
        Map = leafmap.Map(center=[-15, -55], zoom=4, tiles='cartodbdark_matter') #legal ta
        
######PLOTAGEM DAS FIGURAS######
        # Adiciona pontos ao mapa com cores diferenciadas e informações no popup
        for _, row in dfiltrado.iterrows():
            popup_text = f"Hora: {row['Hora']}<br>Lat:{row['Lat']}<br>Lon:{row['Lon']}<br>Satelite:{row['Satélite']}"
            folium.Marker(
                location=[row['Lat'], row['Lon']],
                popup=popup_text,
                icon =folium.Icon(color=row['color'],icon="fire")
            ).add_to(Map)

        # Exibindo o mapa
        with col1:
            Map.to_streamlit(width=1500, height=775)
            
            
st.sidebar.markdown(
    """
    <hr>
    <footer style="text-align: left; font-size: 13px; color: grey;">
    Desenvolvido por <a href="https://www.linkedin.com/in/natanaeis" style="text-decoration: none; color: #FF902A;">
    Natanael Silva Oliveira</a> | © 2024
    </footer>
    """,
    unsafe_allow_html=True,
)
