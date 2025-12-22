import os
import pandas as pd
import plotly.express as px
import math
from haversine import haversine
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, date
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Restaurante', page_icon='🍽️', layout='wide')

#--------------------------------------------------
# FUNCOES
#--------------------------------------------------
def avg_std_time_on_traffic(df1):
    df_aux = df1.groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean','std']})
    df_aux.columns= ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
          color='std_time',
          color_continuous_scale='RdBu',
          color_continuous_midpoint=np.average(df_aux['std_time']))

    return fig
def avg_std_time_graph( df1):

    df_aux = df1.loc[: , ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control',x=df_aux['City'],y=df_aux['avg_time'],error_y=dict( type= 'data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')

    return fig

                
def avg_std_time_delivery(df1, festival, op ):   
    """
        Esta funcao calcula o tempo medio e o devio padrao do tempo de entrega.
        Parametro:
            Input:
                - df: Dataframe com os dados necessarios para o calculo
                - op: Tipo de operacao que precisa ser calculada
                    'avg_time': Calcula o tempo medio
                    'std_time': Calcula o desvio padrao do tempo.

            Output:
                - df: Dataframe com 2 coluna e 1 linha.
    
    """
    df_aux = df1.groupby('Festival').agg({'Time_taken(min)': ['mean','std']})
    df_aux.columns= ['avg_time', 'std_time']
    df_aux = df_aux.reset_index().round(2)           
    df_aux = df_aux.loc[df_aux['Festival'] == festival, op]

    return df_aux

                
def distance(df1, fig):
    if fig == False:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df1['distance'] = df1.loc[: , cols].apply( lambda x: 
                                      haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                  (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1)
        avg_distance = df1['distance'].mean().round(2)   
        return avg_distance
        
    else:
        df1['distance'] = df1.loc[: , ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']].apply( lambda x: 
                                          haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                      (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1)
        avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure( data=[go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0,0.1,0])])
        return fig
        

    
def clean_code(df1):
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format= '%d-%m-%Y')
    df1 = df1[df1['Delivery_person_Age'] != 'NaN ']
    df1 = df1[df1['Road_traffic_density'] != 'NaN ']
    df1 = df1[df1['Festival'] != 'NaN ']
    df1 = df1[df1['City'] != 'NaN ']
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    # Remove o texto '(min)' e espaços extras
    df1['Time_taken(min)'] = df1['Time_taken(min)'].str.replace('(min)', '', regex=False).str.strip()
    # Converte para inteiro
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    return df1

# importar dataset
df_raw = pd.read_csv('train.csv')
df1 = df_raw.copy()

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

st.title('Marketplace - Visão Restaurantes')


tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'])

#=================================
# PRIMEIRO CONTAINER COM 6 COLUNAS
#=================================
with tab1:
    with st.container():
        st.title(' overal Metrics')
        st.markdown("""___""")

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            entregador_unico = df1['Delivery_person_ID'].nunique()
            col1.metric('Entregador únicos', entregador_unico)
            
        with col2:
            avg_distance = distance(df1, fig=False)
            col2.metric( 'Distância média', avg_distance)       
        
        with col3:
            df_aux = avg_std_time_delivery(df1, 'Yes ', 'avg_time' )
            col3.metric('Tempo Média c/ Festival', df_aux)        
            
        with col4:
            df_aux = avg_std_time_delivery(df1, 'Yes ', 'std_time' )
            col4.metric('Desvio Padrão c/ Festival', df_aux)
            
        with col5:
            df_aux = avg_std_time_delivery(df1, 'No ', 'avg_time' )       
            col5.metric('Tempo Média s/ Festival', df_aux)
            
        with col6:
            df_aux = avg_std_time_delivery(df1, 'No ', 'std_time' )            
            col6.metric('Desvio Padrão s/ Festival', df_aux)


#=================================
# SEGUNDO CONTAINER COM 2 COLUNAS
#=================================    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.write('Tempo Medio de entrega por cidade')
            fig = avg_std_time_graph( df1)
            st.plotly_chart( fig)
         
        with col2:
            st.write('Distribuiçao da distancia')
            df_aux = df1.groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean','std']})
            df_aux.columns= ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            
            st.dataframe(df_aux)
            
    

#=================================
# TERCEIRO CONTAINER COM 2 COLUNAS
#=================================    
        
    with st.container():
        st.title('Tempo medio de entrega')
        st.markdown("""___""")

        col1, col2 = st.columns(2)
        with col1:
            st.write('Distância média por cidade')
            fig = distance( df1, fig=True)
            st.plotly_chart(fig)
            
        with col2:
            st.write('Tempo médio e o desvio padrão por cidade e tipo de tráfego')
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig)


       


        












