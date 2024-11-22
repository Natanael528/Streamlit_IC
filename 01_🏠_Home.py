import streamlit as st

st.set_page_config(layout='wide',
                   page_icon=':fire:',
                   page_title='FireScope',
                   initial_sidebar_state='expanded',
                   )


with open('pages/style-home.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)
st.logo('Logos/cropped-simbolo_RGB.png',
        link= 'https://meteorologia.unifei.edu.br')



col1, col2 = st.columns([1.5, 9])
with col1:
    st.image('Logos/logo.png', use_container_width=True)
with col2:
    st.markdown(
        """
        <div style="display: left; justify-content: center; align-items: center; flex-direction: column; text-align: center; width: max-content;margin: auto">
            <h2 style="color: #FF902A; text-align: left">Sobre a Plataforma</h2>
            <p style="text-align: justify; font-size: 16px; line-height: 1.6;">
                Bem-vindo à plataforma <strong>FireScope</strong>, seu portal de informações detalhadas sobre 
                focos de queimadas no Brasil. Aqui você encontrará <em>dashboards interativos</em> que permitem:
            </p>
            <ul style="font-size: 16px; line-height: 1.8; text-align: left;">
                <li>Explorar os focos recentes de queimadas por região;</li>
                <li>Analisar séries temporais e climatologias de dados;</li>
                <li>Entender os impactos ambientais causados por incêndios florestais.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )



st.markdown(
    """
    <h2 style="text-align: center; color: #FF902A;">Destaques da Plataforma</h2>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns([3, 3, 3])

with col1:
    st.markdown(
        """
        <div style="text-align: center; padding: 20px;">
            <img src="https://igce.rc.unesp.br/Home/Departamentos47/demac/cbdo19/logo_inpe.png" width="150" alt="Logo INPE">
            <h3 style="color: #FF902A; margin-top: 15px;">Fonte dos Dados</h3>
            <p style="text-align: justify; font-size: 16px; line-height: 1.6;">
                As informações exibidas nesta plataforma são obtidas do <strong>Banco de Dados de Queimadas</strong>, 
                mantido pelo Instituto Nacional de Pesquisas Espaciais (INPE), uma referência no monitoramento ambiental no Brasil.
            </p>
            <p style="text-align: justify; font-size: 16px; line-height: 1.6;">
                Acesse o banco completo e faça o download diretamente no site oficial:
            </p>
            <a href="https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/" 
            target="_blank" style="color: #007BFF; text-decoration: none; font-weight: bold;">
                Banco de Dados de Queimadas - INPE
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div style="text-align: center; padding: 20px;">
            <img src="https://cdn-icons-png.flaticon.com/512/3381/3381063.png" width="120" alt="Ícone de Resolução">
            <h3 style="color: #FF902A; margin-top: 15px;">Resolução dos Dados</h3>
            <p style="text-align: justify; font-size: 16px; line-height: 1.6;">
                Os dados possuem uma resolução espacial de <strong>1 km</strong>, garantindo análises detalhadas e precisas dos focos de queimadas em território nacional.
            </p>
            <p style="text-align: justify; font-size: 16px; line-height: 1.6;">
                Este nível de detalhamento é ideal para monitoramento ambiental, estudos científicos e planejamento de políticas públicas.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div style="text-align: center; padding: 20px;">
            <img src="https://cdn-icons-png.flaticon.com/512/6821/6821891.png" width="120" alt="Ícone de Satélites">
            <h3 style="color: #FF902A; margin-top: 15px;">Satélites de Monitoramento</h3>
            <p style="text-align: justify; font-size: 16px; line-height: 1.6;">
                A plataforma utiliza dados de diversos satélites, com destaque para o <strong>AQUA</strong> e seu sensor <strong>MODIS</strong>, amplamente reconhecido como referência no monitoramento ambiental.
            </p>
            <p style="text-align: justify; font-size: 16px; line-height: 1.6;">
                Outros satélites importantes incluem <strong>TERRA</strong>, <strong>GOES-16</strong>, <strong>NOAA-15</strong>, <strong>NOAA-20</strong>, <strong>MSG-03</strong>, entre outros.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.image(
    'Logos/000_1JQ6G8.jpg',
    use_container_width=True,
)



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
