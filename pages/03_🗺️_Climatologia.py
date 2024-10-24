import streamlit as st
import pandas as pd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import geopandas as gpd


# Configuração da página
st.set_page_config(layout='wide',
                   page_icon=':fire:',
                   page_title='Unifei Queimadas',
                   initial_sidebar_state='expanded',
                   )

# Leitura do arquivo CSS
with open('style.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.logo('Logos/cropped-simbolo_RGB.png',
        link= 'https://meteorologia.unifei.edu.br')

@st.cache_data
def load_data():
    # Lendo os DataFrames comprimidos
    df_lat = pd.read_csv('dados/lat.csv', compression='zip')
    df_lon = pd.read_csv('dados/lon.csv', compression='zip')
    df_municipios = pd.read_csv('dados/municipios.csv', compression='zip')
    df_estados = pd.read_csv('dados/estados.csv', compression='zip')
    df_biomas = pd.read_csv('dados/biomas.csv', compression='zip')
    
    # Normalizando latitude e longitude
    df_lat['lat'] = df_lat['lat'] / 10000
    df_lon['lon'] = df_lon['lon'] / 10000
    
    # Concatenando os DataFrames
    df = pd.concat([df_lat, df_lon, df_municipios, df_estados, df_biomas], axis=1)
    df['data'] = pd.to_datetime(df['data'])
    df.set_index('data', inplace=True)
    df = df.sort_values('data')  

    return df

# Função que calcula o índice i e j da localização do foco
def index(longitudes_matriz, latitudes_matriz, lon_foco, lat_foco):
    distancia_lon = (longitudes_matriz - lon_foco)**2
    distancia_lat = (latitudes_matriz - lat_foco)**2

    indice_lon_foco = np.nonzero(distancia_lon == np.min(distancia_lon))
    indice_lat_foco = np.nonzero(distancia_lat == np.min(distancia_lat))

    return indice_lat_foco, indice_lon_foco

df = load_data()
col9, col10, col11 = st.columns([2,8,2])



##############################################################ALGUNS CALCS################################################################
# Leitura do shapefile do Brasil
shapefile_brasil = gpd.read_file('https://github.com/evmpython/shapefile/raw/main/brasil/BRAZIL.shp')

# Limites do Brasil
lonmin, lonmax, latmin, latmax = -75.0, -33.0, -35.0, 7.0
delta = 20/100.0

# Montando a grade
lons = np.arange(lonmin, lonmax, delta)
lats = np.arange(latmax, latmin, -delta)
nlon = len(lons)
nlat = len(lats)


with st.sidebar:
    rad = st.radio('Climatologia',['Por Ano','Por Mês'])
    if rad == 'Por Ano':

        # seleciona a "DATA"
        anos_disponiveis = sorted(df.index.year.unique())
        selec = st.sidebar.selectbox('Ano Desejado', anos_disponiveis, index = 21)##############SELECBOX ANO ###################
        dataselec = selec
        df_selec = df.loc[f'{selec}']

    else:
        # Mapeamento dos números dos meses para os nomes dos meses
        meses_nomes = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 
                    'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
        # Seleciona os meses disponíveis no DataFrame
        mes_disponiveis = sorted(df.index.month.unique())
        
        # Exibe o selectbox com os nomes dos meses, mas retorna o número do mês
        selec = st.sidebar.selectbox('Mes Desejado', mes_disponiveis, format_func=lambda x: meses_nomes[x-1])
        dataselec = meses_nomes[selec - 1]
        st.sidebar.divider()
        df_selec = df[df.index.month == selec]
        
   
        
focos_lon, focos_lat = df_selec['lon'].values, df_selec['lat'].values
focos = np.zeros((nlat, nlon))

for lonfoco, latfoco in zip(focos_lon, focos_lat):
    lin, col = index(lons, lats, lonfoco, latfoco)
    focos[lin[0][0], col[0][0]] += 1

# Gera arquivo netcdf
data_vars = {'focos': (('lat', 'lon'), focos, {'units': 'ocorrências/400km²', 'long_name': 'Focos de Calor'})}
coords = {'lat': lats, 'lon': lons, 'time': pd.to_datetime(df_selec.index)}
files = xr.Dataset(data_vars=data_vars, coords=coords)






# Plota a figura
fig, ax = plt.subplots(figsize=(14, 12), facecolor='#a1a1a121')

# Definir limites do mapa com ajuste
ax.set_xlim(lonmin, lonmax)
ax.set_ylim(latmin, latmax)

# Remover as bordas dos eixos (superior, inferior, direito e esquerdo)
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['right'].set_visible(False)

cores = ['#262626', '#3d3835', '#4d423c', '#674f42', '#937260', '#b38871', '#cf9678', '#e78d5e', '#fdb99d']
cmap = ListedColormap(cores)

# Plota o mapa de focos
map1 = ax.contourf(files['lon'],
                   files['lat'],
                   files['focos'],
                   cmap='hot',
                   vmin=0, vmax=160,
                   levels=np.array([0, 5, 10, 15, 20, 30, 40, 50, 60, 70, 100, 130, 160]),
                   extend='both')

# Adiciona a barra de cores
cbar = plt.colorbar(map1, ax=ax)
cbar.set_label('Fonte: INPE/Pixel: 20km', color='white', fontsize=15)

# Remover o contorno da barra de cores
cbar.outline.set_visible(False)

# Configurações de cor da barra de cores
cbar.ax.yaxis.set_tick_params(color='white')
cbar.ax.yaxis.label.set_color('white')
cbar.ax.tick_params(colors='white')

# Título da figura
ax.set_title('Acumulado de Focos', fontsize=20, weight='bold', color='white')

# Adiciona subtítulo com o total de focos
total = int(np.sum(files['focos']))
ax.text(lonmin + 0.3, latmax - 1.2, f'Período = {dataselec}', color='white', fontsize=14)
ax.text(lonmin + 0.3, latmax - 2.2, f'Total de focos = {total}', color='white', fontsize=14)


# Plota contorno dos estados e do Brasil
estados_brasil = gpd.read_file('https://github.com/evmpython/shapefile/raw/main/estados_do_brasil/BR_UF_2019.shp')
estados_brasil.plot(edgecolor='gray', facecolor='none', linewidth=0.5, alpha=1, ax=ax)

contorno_brasil = gpd.read_file('https://github.com/evmpython/shapefile/raw/main/brasil/BRAZIL.shp')
contorno_brasil.plot(edgecolor='gray', facecolor='none', linewidth=0.5, alpha=1, ax=ax)

# Remove os rótulos e ticks de lat e lon
ax.set_xticks([])
ax.set_yticks([])
ax.set_xlabel('')
ax.set_ylabel('')

# Ajuste da figura com col10
col10.pyplot(fig)