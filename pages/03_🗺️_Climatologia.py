import streamlit as st
import pandas as pd
import proplot as pplt

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

st.title('Climatologia')

@st.cache_data
def load_data():
    # Lendo todos os dataframes
    df_lat = pd.read_csv('dados/lat.csv', compression='zip')
    df_lon = pd.read_csv('dados/lon.csv', compression='zip')
    df_municipios = pd.read_csv('dados/municipios.csv', compression='zip')
    df_estados = pd.read_csv('dados/estados.csv', compression='zip')
    df_biomas = pd.read_csv('dados/biomas.csv', compression='zip')
    
    # Normalizando latitude e longitude
    df_lat['lat'] = df_lat['lat'] / 10000
    df_lon['lon'] = df_lon['lon'] / 10000
    
    # Primeiro DataFrame
    df = pd.concat([df_lat, df_lon, df_municipios, df_estados, df_biomas], axis=1)
    df['data'] = pd.to_datetime(df['data'])
    df.set_index('data', inplace=True)
    df = df.sort_values('data')  
    
    return df

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False)

#carrega o dataframe
df = load_data()
data = df.groupby(pd.Grouper(freq='1M')).count()['lat']

# cria moldura da figura
fig, ax = pplt.subplots(figsize=(8, 3), sharey=False, tight=True)

# plota os focos de caloe
ax.plot(data.index,
        data.values,
        color='bright red',
        marker='*',
        label='Total')

# formatação dos eixos
ax.format(title='Total por Hora: MG - 2011 à 2020',
          xlabel='Hora Local',
          ylabel='Focos de Calor',
          xticks=2,
          xtickminor=False,
          ytickminor=False,
          xlim=(-1,24))

# legendas
ax.legend(frameon=False, prop={'size': 15})

# exibe a figura na tela
pplt.to_streamlit(width=1350, height=700)