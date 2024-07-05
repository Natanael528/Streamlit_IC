import streamlit as st
import leafmap.foliumap as leafmap

# configuração da página
st.set_page_config(layout='wide')

# load Style css
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

#adiciona logo
st.logo('Logos/cropped-simbolo_RGB.png',
        link= 'https://meteorologia.unifei.edu.br')

with st.expander("teste code"):
    filepath = "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_cities.csv"
    m = leafmap.Map(center=[-15.7801, -47.9292], zoom=4, tiles='cartodbdark_matter')
    m.add_heatmap(
        filepath,
        latitude="latitude",
        longitude="longitude",
        value="pop_max",
        name="Heat map",
        radius=20,
    )
m.to_streamlit(height=700)
