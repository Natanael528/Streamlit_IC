import streamlit as st
import leafmap.foliumap as leafmap
import folium
from folium.plugins import MarkerCluster

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

st.title('Anomalia')




import leafmap.foliumap as leafmap
import folium
import pandas as pd

# Exemplo de DataFrame filtrado (dfiltrado)
data = {
    'lat': [-15.7801, -22.9068, -3.1190],
    'lon': [-47.9292, -43.1729, -60.0217],
    'name': ['Brasília', 'Rio de Janeiro', 'Manaus']
}
dfiltrado = pd.DataFrame(data)

# Crie o mapa
Map = leafmap.Map(center=[-15.7801, -47.9292], zoom=4, tiles='cartodbdark_matter')

# Caminho para o ícone de fogo SVG local
icon_path = r'Logos\fireicon.png'

# Adicione pontos ao mapa com ícones personalizados
for idx, row in dfiltrado.iterrows():
    icon = folium.CustomIcon(icon_image=icon_path, icon_size=(30, 30))
    folium.Marker(
        location=[row['lat'], row['lon']],
        icon=icon,
        popup=row['name']
    ).add_to(Map)

# Exiba o mapa no Streamlit
Map.to_streamlit(width=1350, height=700)
