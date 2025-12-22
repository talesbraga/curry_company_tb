# importar bibliotecas
import pandas as pd
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, date
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores', page_icon='📈', layout='wide')

#--------------------------------------------------
# FUNCOES
#--------------------------------------------------
def top_delivers_rapido(df1):
    df2 = df1.groupby(['City', 'Delivery_person_ID'])['Time_taken(min)'].min().reset_index().sort_values(['City', 'Time_taken(min)'])
    df_aux1 = df2.loc[df2['City'] == 'Metropolitian '].head(10)
    df_aux2 = df2.loc[df2['City'] == 'Urban '].head(10)
    df_aux3 = df2.loc[df2['City'] == 'Semi-Urban '].head(10)            
    df3 = pd.concat([df_aux1,df_aux2,df_aux3]).reset_index(drop=True)

    return df3                

                
def top_delivers( df1):
    df2 = ( df1.groupby(['City', 'Delivery_person_ID'])['Time_taken(min)']
               .max().reset_index()
               .sort_values(['City', 'Time_taken(min)'], ascending=False))
    df_aux1 = df2.loc[df2['City'] == 'Metropolitian '].head(10)
    df_aux2 = df2.loc[df2['City'] == 'Urban '].head(10)
    df_aux3 = df2.loc[df2['City'] == 'Semi-Urban '].head(10)            
    df3 = pd.concat([df_aux1,df_aux2,df_aux3]).reset_index(drop=True)

    return df1

                
def clean_code(df1):
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format= '%d-%m-%Y')
    df1 = df1[df1['Delivery_person_Age'] != 'NaN ']
    df1 = df1[df1['Road_traffic_density'] != 'NaN ']
    df1 = df1[df1['City'] != 'NaN ']
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)    
    # Remove o texto '(min)' e espaços extras
    df1['Time_taken(min)'] = df1['Time_taken(min)'].str.replace('(min)', '', regex=False).str.strip()
    # Converte para inteiro
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    return df1


# importar dataset
df = pd.read_csv('train.csv')
df1 = df.copy()


# limpeza dos dados
df1 = clean_code(df1)


#========================================
# BARRA LATERAL
#========================================

#image_path =  r'C:\Users\Asus\OneDrive\Cursos\Comunidade DS\FTC Analise de dados\Dataset\logo.png'
image = Image.open( 'logo.png' )
st.sidebar.image( image, width=120 )


st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown( """___""")

#=======================
# FILTRO DE DATA
#=======================
st.sidebar.markdown(' ## Selecione uma data limite')
date_slider = st.sidebar.slider(
   "Até qual valor?",     
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6 ),
    value=datetime( 2022, 4, 13 ),
    format="DD-MM-YYYY")

st.sidebar.markdown("""___""")
#==============================
# FILTRO CONDICAO DO TRANSITO
#==============================

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low ','Medium ','High ','Jam '],
    default='Low ')

clima_options = st.sidebar.multiselect(
    'Quais as condições climaticas',
    ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
       'conditions Cloudy', 'conditions Fog', 'conditions Windy'],
    default='conditions Sunny')



st.sidebar.markdown("""___""")
st.sidebar.markdown('### Powered by Comunidade DS')

# filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

# filtro de transito
linhas_selecionadas = df1['Weatherconditions'].isin( clima_options )
df1 = df1.loc[linhas_selecionadas, :]


#========================================
#LAYOUT DO STRIMILIT
#========================================

st.title('Marketplace - Visão Entregadores')


tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'])
#===============
# CONTAINER 01
#===============
with tab1:
    with st.container():
        st.title('Overall Metrics')

        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:  
            maior_idade = df1['Delivery_person_Age'].max()
            col1.metric("Maior idade", maior_idade)
        
        with col2: 
            menor_idade = df1['Delivery_person_Age'].min()
            col2.metric("Menor idade", menor_idade)

        with col3:
            melhor_veiculo = df1['Vehicle_condition'].max()
            col3.metric("Melhor condição de veiculos", melhor_veiculo)

        with col4:
            pior_veiculo = df1['Vehicle_condition'].min()
            col4.metric("Pior condição de veiculos", pior_veiculo)
            
#===============
# CONTAINER 02
#===============
    with st.container():
        st.markdown("""___""")
        st.title('Avaliação')
        

        col1, col2 = st.columns( 2 )
        with col1:
            st.write('Avaliações media por entregador')
            avaliacao_med_emtregador = ( df1.groupby('Delivery_person_ID')['Delivery_person_Ratings']
                                            .mean()
                                            .reset_index()
                                            .round(2))
            st.dataframe(avaliacao_med_emtregador)

        with col2:
            st.write('Avaliação media por transito')
            med_st_por_trafego = ( df1.groupby('Road_traffic_density')['Delivery_person_Ratings']
                                      .agg(['mean','std'])
                                      .round(2))
            med_st_por_trafego.columns = ['media','desvio padrao']
            med_st_por_trafego = med_st_por_trafego.reset_index()
            st.dataframe(med_st_por_trafego)

            st.write('Avaliação media por clima')
            med_st_por_clima = ( df1.groupby('Weatherconditions')['Delivery_person_Ratings']
                                    .agg(['mean','std'])
                                    .round(2))
            med_st_por_clima.columns = ['media','desvio padrao']            
            med_st_por_clima = med_st_por_clima.reset_index()
            st.dataframe(med_st_por_clima)

            
#===============
# CONTAINER 03
#===============
    with st.container():
        st.markdown("""___""")
        st.title('Velocidade de entrega')

        col1,col2 = st.columns(2)

        with col1:
            st.write( 'Top entregadores mais rapidos')
            df3  = top_delivers_rapido(df1)
            st.dataframe(df3)
             

        with col2:
            st.write('Top entregadores mais lentos')
            df3 = top_delivers( df1)
            st.dataframe(df3)


            
            



