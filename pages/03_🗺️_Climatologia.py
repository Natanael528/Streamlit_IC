import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
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
    # Lendo todos os dataframes
    df_lat = pd.read_csv('dados/lat.csv', compression='zip')
    df_lon = pd.read_csv('dados/lon.csv', compression='zip')
    df_municipios = pd.read_csv('dados/municipios.csv', compression='zip')
    
    # Normalizando latitude e longitude
    df_lat['lat'] = df_lat['lat'] / 10000
    df_lon['lon'] = df_lon['lon'] / 10000
    
    # Primeiro DataFrame
    df = pd.concat([df_lat, df_lon, df_municipios], axis=1)
    df['data'] = pd.to_datetime(df['data'])
    df.set_index('data', inplace=True)
    df = df.sort_values('data')
    
    # Agrupando os dados por ano e contando as entradas
    df2 = df.groupby(pd.Grouper(freq='1Y')).count()['lat']

    return df, df2

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False)

# Carrega o dataframe
df, df2 = load_data()

# Seleção do ano
anos_disponiveis = sorted(df2.index.year.unique())
ano_selecionado = st.sidebar.selectbox('Selecione o Ano:', anos_disponiveis)

# Filtrando o DataFrame para o ano selecionado
df_filtrado = df[df.index.year == ano_selecionado]

# Adicionando uma coluna fictícia de valor
df_filtrado['value'] = 1  # Todos os pontos têm a mesma intensidade

# Criando o mapa com heatmap
m = leafmap.Map(center=[-15.7801, -47.9292], zoom=4, tiles='cartodbdark_matter')

# Adicionando o heatmap ao mapa
m.add_heatmap(
    df_filtrado,
    latitude="lat",
    longitude="lon",
    value="value",  # Usando a coluna 'value' com intensidade uniforme
    name="Heat map",
    radius=12,
)

# Exibindo o mapa no Streamlit
m.to_streamlit(width=1750, height=800)







