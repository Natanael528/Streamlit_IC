import streamlit as st

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

st.title('Focos de Queimadas Brasil')
st.markdown('''Explore informações detalhadas sobre focos de queimadas no Brasil com nossos dashboards interativos. 
            Acompanhe os focos recentes, analise climatologias e visualize séries temporais de dados sobre incêndios 
            florestais em todo o país. Nosso projeto oferece uma visão abrangente e atualizada, 
            facilitando a compreensão e monitoramento dos impactos das queimadas no meio ambiente brasileiro.''')

