import streamlit as st
import pandas as pd
import numpy as np
import xarray as xr
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import geopandas as gpd

#
#Configuração da página
st.set_page_config(layout='wide',
                   page_icon=':fire:',
                   page_title='FireScope',
                   initial_sidebar_state='expanded',
                   )

#Leitura do arquivo CSS
with open('pages/style-climaT.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.logo('Logos/logomaior.png', icon_image='Logos/Logo-icon.png',
        size= 'large',
        link= 'https://meteorologia.unifei.edu.br')

##############################################################definindo funçoes################################################################

# Placeholder para exibir progresso e atualizar elementos dinamicamente
placeholder = st.empty()

# Mensagem inicial
placeholder.markdown("Carregando dados...")



@st.cache_data
def load_data():
    #Lendo os DataFrames comprimidos
    df_lat = pd.read_csv('dados/lat.csv', compression='zip')
    df_lon = pd.read_csv('dados/lon.csv', compression='zip')
    
    #normalizando latitude e longitude
    df_lat['lat'] = df_lat['lat'] / 10000
    df_lon['lon'] = df_lon['lon'] / 10000
    
    #Concatenando os DataFrames
    df = pd.concat([df_lat, df_lon], axis=1)
    df['data'] = pd.to_datetime(df['data'])
    df.set_index('data', inplace=True)
    df = df.sort_values('data')  

    return df

# Progresso inicial (0%)
placeholder.progress(0, "Montando a grade...")

#Função que calcula o índice i e j da localização do foco
def index(longitudes_matriz, latitudes_matriz, lon_foco, lat_foco):
    distancia_lon = (longitudes_matriz - lon_foco)**2
    distancia_lat = (latitudes_matriz - lat_foco)**2

    indice_lon_foco = np.nonzero(distancia_lon == np.min(distancia_lon))
    indice_lat_foco = np.nonzero(distancia_lat == np.min(distancia_lat))

    return indice_lat_foco, indice_lon_foco

df = load_data()
col9, col10, col11 = st.columns([2.5,7,2.5], gap='small')



##############################################################ALGUNS CALCS################################################################
#Leitura do shapefile do Brasil
shapefile_brasil = gpd.read_file('https://github.com/evmpython/shapefile/raw/main/brasil/BRAZIL.shp')

#Limites do Brasil
lonmin, lonmax, latmin, latmax = -75.0, -33.0, -35.0, 7.0
delta = 20/100.0

#Montando a grade
lons = np.arange(lonmin, lonmax, delta)
lats = np.arange(latmax, latmin, -delta)
nlon = len(lons)
nlat = len(lats)
# Progresso de 50%
placeholder.progress(50, "Contanto fogueiras...")

with st.sidebar:
    rad = st.radio('Acomulado',['Total Por Ano','Total Por Mês'])
    if rad == 'Total Por Ano':

        # seleciona a "DATA"
        anos_disponiveis = sorted(df.index.year.unique())
        selec = st.sidebar.selectbox('Ano Desejado', anos_disponiveis, index = 21)##############SELECBOX ANO ###################
        dataselec = selec
        df_selec = df.loc[f'{selec}']
        
          
    else:
        
        #Seleciona o ano desejado
        anos_disponiveis = sorted(df.index.year.unique())
        selecaano = st.sidebar.selectbox('Ano Desejado', anos_disponiveis, index=21)


        meses_nomes = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 
                    'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']

        #Filtra os meses disponíveis apenas para o ano selecionado
        mes_disponiveis = sorted(df[df.index.year == selecaano].index.month.unique())

        selec = st.sidebar.selectbox('Mes Desejado', mes_disponiveis, format_func=lambda x: meses_nomes[x-1])

        dataselec = f'{meses_nomes[selec - 1]}/{selecaano}'
        st.sidebar.divider()

        df_selec = df.loc[f'{selec}-{selecaano}']

# Progresso de 50%
placeholder.progress(50, "Contanto fogueiras...")    
focos_lon, focos_lat = df_selec['lon'].values, df_selec['lat'].values
focos = np.zeros((nlat, nlon))

for lonfoco, latfoco in zip(focos_lon, focos_lat):
    lin, col = index(lons, lats, lonfoco, latfoco)
    focos[lin[0][0], col[0][0]] += 1

#Gera arquivo netcdf
data_vars = {'focos': (('lat', 'lon'), focos, {'units': 'ocorrências/400km²', 'long_name': 'Focos de Calor'})}
coords = {'lat': lats, 'lon': lons, 'time': pd.to_datetime(df_selec.index)}
files = xr.Dataset(data_vars=data_vars, coords=coords)




##############################################################PLOTANDO A FIGURA################################################################
placeholder.progress(75, "Quase lá...") 
#Plota a figura
fig, ax = plt.subplots(figsize=(15, 12), dpi=300, facecolor='#a1a1a121')

#Definir limites do mapa com ajuste
ax.set_xlim(lonmin, lonmax)
ax.set_ylim(latmin, latmax)



#Remover as bordas dos eixos (superior, inferior, direito e esquerdo)
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['right'].set_visible(False)



cores = ['#262626', '#3d3835', '#4d423c', '#674f42', '#937260', '#b38871', '#cf9678', '#e78d5e', '#fdb99d']
cmap = ListedColormap(cores)

#Plota o mapa de focos
map1 = ax.contourf(files['lon'],
                   files['lat'],
                   files['focos'],
                   cmap='afmhot',
                   vmin=0, vmax=160,
                   levels=np.array([0, 5, 10, 15, 20, 30, 40, 50, 60, 70, 100, 130, 160]),
                   extend='max')


#Adiciona a barra de cores
cax = fig.add_axes([0.6, 0.18, 0.2, 0.03])  # Ajuste esses valores para posicionar a colorbar
cbar = plt.colorbar(map1, cax=cax, orientation='horizontal')

cbar.set_label('Fonte: INPE/Pixel: 20km', color='white', fontsize=15)

#onfigurações de cor da barra de cores
cbar.ax.yaxis.set_tick_params(color='white')
cbar.ax.yaxis.label.set_color('white')
cbar.ax.tick_params(colors='white')

placeholder.progress(100, "Tudo pronto! Preparando a vista panorâmica.")

ax.set_facecolor('#323439') #Tirar a barra branca 

#Título da figura
ax.set_title('Acumulado de Focos', fontsize=20, weight='bold', color='white')

#Adiciona subtítulo com o total de focos
total = int(np.sum(files['focos']))
ax.text(lonmin + 0.3, latmax - 1.2, f'Período = {dataselec}', color='white', fontsize=14)
ax.text(lonmin + 0.3, latmax - 2.2, f'Total de focos = {total}', color='white', fontsize=14)


#Plota contorno dos estados e do Brasil
estados_brasil = gpd.read_file('https://github.com/evmpython/shapefile/raw/main/estados_do_brasil/BR_UF_2019.shp')
estados_brasil.plot(edgecolor='gray', facecolor='none', linewidth=0.5, alpha=1, ax=ax)

contorno_brasil = gpd.read_file('https://github.com/evmpython/shapefile/raw/main/brasil/BRAZIL.shp')
contorno_brasil.plot(edgecolor='gray', facecolor='none', linewidth=0.5, alpha=1, ax=ax)

#Remove os rótulos e ticks de lat e lon
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlabel('')
ax.set_ylabel('')



#Ajuste da figura com col10
col10.pyplot(fig, use_container_width=True)

placeholder.empty()

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
