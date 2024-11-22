import streamlit as st
import pandas as pd
import numpy as np
import xarray as xr
import salem
import geopandas as gpd
import leafmap.foliumap as leafmap
import tempfile
import json

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

# Placeholder para exibir progresso e atualizar elementos dinamicamente
placeholder = st.empty()

# Mensagem inicial
placeholder.markdown("Carregando dados...")


#Leitura do shapefile do Brasil
shapefile_brasil = gpd.read_file('https://github.com/evmpython/shapefile/raw/main/brasil/BRAZIL.shp')

#Limites do Brasil
lonmin, lonmax, latmin, latmax = -75.0, -34.0, -35.0, 7.0
delta = 20/100.0

# Progresso inicial (0%)
placeholder.progress(0, "Montando a grade...")

#Montando a grade
lons = np.arange(lonmin, lonmax, delta)
lats = np.arange(latmax, latmin, -delta)
nlon = len(lons)
nlat = len(lats)
with st.sidebar:
    rad = st.radio('Climatologia',['Total Por Ano','Total Por Mês'])
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

# Gerando matriz de focos
focos_lon, focos_lat = df_selec['lon'].values, df_selec['lat'].values
focos = np.zeros((nlat, nlon))

for lonfoco, latfoco in zip(focos_lon, focos_lat):
    lin, col = index(lons, lats, lonfoco, latfoco)
    focos[lin[0][0], col[0][0]] += 1


# leitura do shapefile do Brasil
shapefile = salem.read_shapefile('https://github.com/evmpython/shapefile/raw/main/brasil/BRAZIL.shp')

# NetCDF com dimensão 'time'
data_vars = {'focos': (('time', 'lat', 'lon'), focos[np.newaxis, :, :], {'units': 'ocorrências/400km²', 'long_name': 'Focos de Calor'})}
coords = {'lat': lats, 'lon': lons, 'time': [pd.to_datetime(df_selec.index[0])]}
focos_nc = xr.Dataset(data_vars=data_vars, coords=coords).salem.roi(shape=shapefile)


# Criando arquivo temporário para salvar o NetCDF
with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp:
    focos_nc.to_netcdf(tmp.name)
    netcdf_path = tmp.name
    

##############################################################PLOTANDO A FIGURA################################################################


placeholder.progress(75, "Quase lá...")

estados_brasil = gpd.read_file('https://github.com/evmpython/shapefile/raw/main/estados_do_brasil/BR_UF_2019.shp')
#Convertendo para JSON
estados_geojson = json.loads(estados_brasil.to_json())


m = leafmap.Map(tiles='cartodbdark_matter')

m.add_geojson(estados_geojson, layer_name="Contorno Estados", style={"color": "gray", "weight": 0.5})

params = {
    "width": 4.8,
    "height": 0.3,
    "vmin": 0,
    "vmax": 160,
    "cmap": "afmhot",
    "label": "Focos de Calor/20km2",
    "orientation": "horizontal",
    "transparent": False,
}

m.add_netcdf(
    netcdf_path,
    variables=['focos'],
    palette='afmhot',
    layer_name="Focos de Calor",
)

m.add_colormap(position=(71, 2), **params)

placeholder.progress(100, "Tudo pronto! Preparando a vista panorâmica.")


st.subheader("Mapa de Focos de Calor com Contorno dos Estados e do Brasil")
m.to_streamlit(width=1400, height=700)

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
