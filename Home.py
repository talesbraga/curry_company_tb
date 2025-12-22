import streamlit as st
from PIL import Image

st.set_page_config(
        page_title="Home",
        page_icon="🎲"
)

#image_path = "C:/Users/Asus/OneDrive/Cursos/Comunidade DS/FTC Analise de dados/Dataset/"
image = Image.open( 'logo.png')
st.sidebar.image( image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown( """___""")

st.write(" Curry Company Growth Dashboard")


st.markdown(
    """
    Growth Dashboard foi construido para acompanhar as metricas de crescimento dos entregadores e restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visao Empresa:
        - Visão Gerencial: Metricas gerais de comportamento.
        - Visao tática: indicadores semanais de crescimento.
        - Visao Geografica: Insights de geolocalizaçao.
    - Visao Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visao Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Time de Data Science no Discord
        - @TB
""")