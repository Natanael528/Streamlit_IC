import streamlit as st

# configuração da página
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# load Style css
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

#adiciona logo
st.logo('Logos/cropped-simbolo_RGB.png',
        link= 'https://meteorologia.unifei.edu.br')

st.title('PAGINA PARA MONOXIDO DE CARBONO')