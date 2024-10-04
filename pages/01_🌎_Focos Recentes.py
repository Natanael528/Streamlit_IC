import streamlit as st
import pandas as pd
from datetime import datetime,timedelta
import leafmap.foliumap as leafmap
import folium


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
    df = pd.read_csv(f'https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/mensal/Brasil/focos_mensal_br_{data}.csv', usecols=(['data_hora_gmt','lat','lon','satelite','bioma','municipio','frp']))
    df = df.rename(columns={'data_hora_gmt':'Data','lat':'Lat','lon':'Lon','satelite':'Satelite','bioma':'Bioma','municipio':'Municipio','frp':'FRP'}) 
    df['Data'] = pd.to_datetime(df['Data'])
    df.set_index('Data', inplace=True)
     
    return df

def load_data2():
    dfs = []
    for i in range(0, 50, 10):
        data_anterior = datetime.now() - timedelta(hours=0,minutes=i)
        
        # Arredondar o tempo para o múltiplo de 10 minutos
        data = data_anterior.replace(minute=(data_anterior.minute // 10) * 10, second=0, microsecond=0).strftime("%Y%m%d_%H%M") 
        
        try: # Tentar carregar o CSV
            
            df = pd.read_csv(f'https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/10min/focos_10min_{data}.csv', usecols=(['data','lat', 'lon', 'satelite']))
            df = df.rename(columns={'data':'Data','lat':'Lat','lon':'Lon','satelite':'Satelite'})
            df['Data'] = pd.to_datetime(df['Data'])
            df['Data'] = df['Data'] - pd.to_timedelta(2.5, unit='h')
            df['Hora'] = df['Data'].dt.time
            df.set_index('Data', inplace=True)

            dfs.append(df)
            
        except Exception as e:
            empty_df = pd.DataFrame(columns=['Data', 'Lat', 'Lon', 'Satelite', 'Hora'])
            dfs.append(empty_df)
        df = pd.concat(dfs)
        print (data)
    return dfs

def convert_df(dfd): #converter arquivos para donwload
    return dfd.to_csv().encode("utf-8")
##############################################################################################################################################################

with st.sidebar:
    periodo = st.radio('Selecione o Período do dado', ['Recentes','Diário'])


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
     
    col1, col2 = st.columns([9, 1.4], vertical_alignment="top") #divide a pagina em duas colunas com tamanhos diferentes

    df2 = load_data2()
    
    selected_dfs = []
    
    colors = ["red", "orange", "green", "blue", "purple"]  # Cores para diferenciar os DataFrames
    
    with col2:  # Coloca os checkboxes na coluna da direita
        st.divider()
        st.markdown("**Focos de incêndio**")

        min1 = st.checkbox(":red[***Últimos 10 Minutos***]", value=True)
        if min1:
            df2[0]['color'] = colors[0]  # Adiciona cor ao DataFrame
            selected_dfs.append(df2[0])
        min2 = st.checkbox(":orange[***Últimos 20 Minutos***]")
        if min2:
            df2[1]['color'] = colors[1]  # Adiciona cor ao DataFrame
            selected_dfs.append(df2[1])

        min3 = st.checkbox(":green[***Últimos 30 Minutos***]")
        if min3:
            df2[2]['color'] = colors[2]  # Adiciona cor ao DataFrame
            selected_dfs.append(df2[2])

        min4 = st.checkbox(":blue[***Últimos 40 Minutos***]")
        if min4:
            df2[3]['color'] = colors[3]  # Adiciona cor ao DataFrame
            selected_dfs.append(df2[3])

        min5 = st.checkbox(":violet[***Últimos 50 Minutos***]")
        if min5:
            df2[4]['color'] = colors[4]  # Adiciona cor ao DataFrame
            selected_dfs.append(df2[4])
            

        ultimaatt = []
        if selected_dfs:  # Verifica se há DataFrames selecionados
            for df in selected_dfs:
                if not df.empty:  # Verifica se o DataFrame não está vazio
                    primeira_linha = df.index[0]  # Pega a primeira linha do DataFrame
                    ultimaatt.append(primeira_linha)

        # Verifica se a lista 'ultimaatt' não está vazia
        if ultimaatt:
            st.markdown("**Última atualização:**")  
            st.markdown(ultimaatt[0])  # Plota a mensagem com o primeiro elemento da lista
        
        st.divider()
    
    if selected_dfs:# Concatenar todos os DataFrames
        concatenated_df = pd.concat(selected_dfs, ignore_index=True)

        sat = concatenated_df['Satelite'].unique().tolist()
        sat.insert(0, 'Todos Satélites')
        selec = st.sidebar.selectbox('Selecione um Satélite', sat)

        if selec == 'Todos Satélites':
            dfiltrado = concatenated_df  # Sem filtragem
        else:
            dfiltrado = concatenated_df[concatenated_df['Satelite'] == selec]


        # Map = leafmap.Map(center=[-25, -55], zoom=4, tiles='cartodbdark_matter')
        # Map.add_points_from_xy(dfiltrado, x="Lon", y="Lat", layer_name="Marcadores")
        # with col1:
        #     Map.to_streamlit(width=1500, height=775)

            
        Map = leafmap.Map(center=[-15, -55], zoom=4, tiles='cartodbdark_matter') #legal ta

        # Adiciona pontos ao mapa com cores diferenciadas e informações no popup
        for _, row in dfiltrado.iterrows():
            popup_text = f"Hora: {row['Hora']}<br>Lat:{row['Lat']}<br>Lon:{row['Lon']}<br>Satelite:{row['Satelite']}"
            folium.Marker(
                location=[row['Lat'], row['Lon']],
                popup=popup_text,
                icon =folium.Icon(color=row['color'],icon="fire")
            ).add_to(Map)

        # Exibindo o mapa
        with col1:
            Map.to_streamlit(width=1500, height=775)