import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import leafmap.foliumap as leafmap
import tempfile
import json
import xarray as xr

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

# Função para carregar dados
@st.cache_data
def load_data():
    # Lendo os DataFrames comprimidos
    df_lat = pd.read_csv('dados/lat.csv', compression='zip')
    df_lon = pd.read_csv('dados/lon.csv', compression='zip')
    
    # Normalizando latitude e longitude
    df_lat['lat'] = df_lat['lat'] / 10000
    df_lon['lon'] = df_lon['lon'] / 10000
    
    # Concatenando os DataFrames
    df = pd.concat([df_lat, df_lon], axis=1)
    df['data'] = pd.to_datetime(df['data'])
    df.set_index('data', inplace=True)
    return df.sort_values('data')

# Função para calcular índice i e j da localização do foco
def find_indices(longitudes, latitudes, lon_foco, lat_foco):
    distancia_lon = (longitudes - lon_foco) ** 2
    distancia_lat = (latitudes - lat_foco) ** 2
    indice_lon = np.argmin(distancia_lon)
    indice_lat = np.argmin(distancia_lat)
    return indice_lat, indice_lon



# Carregar os dados
df = load_data()

# Placeholder para exibir progresso
placeholder = st.empty()
placeholder.markdown("Carregando dados...")

# Leitura do shapefile do Brasil
shapefile_brasil = gpd.read_file('https://github.com/evmpython/shapefile/raw/main/brasil/BRAZIL.shp')

# Configuração da grade de latitude e longitude
lonmin, lonmax, latmin, latmax = -75.0, -34.0, -35.0, 7.0
delta = 0.2
lons = np.arange(lonmin, lonmax, delta)
lats = np.arange(latmax, latmin, -delta)
nlon, nlat = len(lons), len(lats)

# Sidebar para seleção de ano/mês
with st.sidebar:
    rad = st.radio('Climatologia', ['Total Por Ano', 'Total Por Mês'])
    anos_disponiveis = sorted(df.index.year.unique())
    
    if rad == 'Total Por Ano':
        selec = st.selectbox('Ano Desejado', anos_disponiveis, index=len(anos_disponiveis) - 1)
        df_selec = df[df.index.year == selec]
    else:
        selecaano = st.selectbox('Ano Desejado', anos_disponiveis, index=len(anos_disponiveis) - 1)
        meses_nomes = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 
                       'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
        meses_disponiveis = sorted(df[df.index.year == selecaano].index.month.unique())
        mes_selec = st.selectbox('Mês Desejado', meses_disponiveis, format_func=lambda x: meses_nomes[x - 1])
        df_selec = df[(df.index.year == selecaano) & (df.index.month == mes_selec)]
        


# Progresso de carregamento
placeholder.progress(50, "Contando focos de calor...")

# Gerar matriz de focos
focos = np.zeros((nlat, nlon))
for lonfoco, latfoco in zip(df_selec['lon'], df_selec['lat']):
    lin, col = find_indices(lons, lats, lonfoco, latfoco)
    focos[lin, col] += 1

# Criar NetCDF com dimensões lat/lon
data_vars = {
    'focos': (('time', 'lat', 'lon'), focos[np.newaxis, :, :], {'units': 'ocorrências/400km²', 'long_name': 'Focos de Calor'})
}
coords = {'lat': lats, 'lon': lons, 'time': [pd.to_datetime(df_selec.index[0])]}
focos_nc = xr.Dataset(data_vars=data_vars, coords=coords).salem.roi(shape=shapefile_brasil)


# Salvar NetCDF temporariamente
with tempfile.NamedTemporaryFile(suffix=".nc", delete=False) as tmp:
    focos_nc.to_netcdf(tmp.name)
    netcdf_path = tmp.name

# Progresso de carregamento
placeholder.progress(75, "Preparando mapa...")

# Ler contorno dos estados do Brasil
estados_brasil = gpd.read_file('https://github.com/evmpython/shapefile/raw/main/estados_do_brasil/BR_UF_2019.shp')
estados_geojson = json.loads(estados_brasil.to_json())


##############################################################PLOTAR MAPA################################################################


# Configurar mapa
m = leafmap.Map(tiles='cartodbdark_matter')
m.add_geojson(estados_geojson, layer_name="Contorno Estados", style={"color": "gray", "weight": 0.5})

# Adicionar NetCDF ao mapa
params = {
    "width": 4.8,
    "height": 0.3,
    "vmin": 0,
    "vmax": np.max(focos),
    "cmap": "afmhot",
    "label": "Focos de Calor/20km²",
    "orientation": "horizontal",
}
m.add_netcdf(netcdf_path, variables=['focos'], palette='afmhot', layer_name="Focos de Calor")
m.add_colormap(position=(71, 2), **params)

# Exibir mapa
st.subheader("Mapa de Focos de Calor com Contorno dos Estados e do Brasil")
m.to_streamlit(width=1400, height=700)

# Limpar placeholder
placeholder.empty()

# Rodapé
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