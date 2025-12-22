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

st.set_page_config(page_title='Visão Empresa', page_icon='🚚', layout='wide')

#--------------------------------------------------
# FUNCOES
#--------------------------------------------------
def country_maps(df1):
    data_plot = (df1.loc[:, ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']]
                    .groupby( ['City', 'Road_traffic_density'])
                    .median()
                    .reset_index())
    data_plot = data_plot[data_plot['City'] != 'NaN']
    data_plot = data_plot[data_plot['Road_traffic_density'] != 'NaN']    
    # Desenhar o mapa
    map_ = folium.Map( zoom_start=11 )
    
    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']] ).add_to( map_ )
    
    
    folium_static(map_, width=1024 , height=600)

    return None


def order_share_by_week(df1):
    df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year').nunique().reset_index()            
    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )            
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']    
    # gráfico
    fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )

    return fig

    
def order_by_week(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')            
    df_aux = df1.loc[:,['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()            
    fig = px.line(df_aux, x='week_of_year', y='ID')

    return fig

    
def traffic_order_city( df1 ):
    df_aux = (df1.loc[:, ['ID', 'City', 'Road_traffic_density']]
                .groupby( ['City', 'Road_traffic_density'] )
                .count().reset_index())
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
    # gráfico
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID', color='City')

    return fig

    
def traffic_order_share(df1):
    df_aux = (df1.loc[:, ['ID', 'Road_traffic_density']]
                .groupby( 'Road_traffic_density' )
                .count().reset_index())
    df_aux['perc_ID'] = 100 * (df_aux['ID'] / df_aux['ID'].sum())                
    # gráfico
    fig = px.pie( df_aux, values='perc_ID', names='Road_traffic_density' )

    return fig

    
def order_metric(df1):    
    df_aux = (df1.loc[:, ['ID', 'Order_Date']]
                .groupby('Order_Date')
                .count().reset_index())
    df_aux.columns = ['Order_Date', 'Qtd_entregas']
    # grafico
    fig = px.bar(df_aux, x='Order_Date', y='Qtd_entregas',)

    return fig

            
def clean_code( df1 ):
    """" Esta funcao tem a responsabilidade de limpar o dataframe

    tipo de limpeza:
    1. Remocao dos dados Nan
    2. Mudanca do tipo da coluna de dados
    3. Remocao dos espacos das variaveis de texto

    input: Dataframe
    ouput: Dataframe   
    
    """
    
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


#-------------------------------- INICIO DA ESTRUTURA LOGICA DO CODIGO --------------------------------

#------------------------
# importar dataset
#------------------------

df = pd.read_csv('train.csv')

df1 = df.copy()

# Limpando os dados
df1 = clean_code ( df1 )

#========================================
# BARRA LATERAL
#========================================

#image_path =  r'C:\Users\Asus\OneDrive\Cursos\Comunidade DS\FTC Analise de dados\Dataset\logo.png'
image = Image.open( 'logo.png' )
st.sidebar.image( image, width=120 )


st.sidebar.markdown('# Curry Company')
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
st.sidebar.markdown("""___""")
st.sidebar.markdown('### Powered by Comunidade DS')

# filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]



#========================================
#LAYOUT DO STRIMILIT
#========================================

st.title('Marketplace - Visão Cliente')

#===============
# CONTAINER 01
#===============
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

#========= Visao gerencial ===============
with tab1:
    with st.container():
        fig = order_metric(df1)
        st.write("Orders by Day")
        st.plotly_chart( fig, use_container_witdth=True )
                
#===== Visao gerencial ============= 
#===================================
# CONTAINER 02
#===================================

    with st.container():
        col1, col2 = st.columns( 2 )
        
        #======== VG - coluna 01 ==========
        with col1:
            st.write('Traffic Order Share')
            fig = traffic_order_share(df1)
            st.plotly_chart( fig, use_container_width=True)            
    
        #======== VG - coluna 02 ==========    
        with col2:
            st.write('Traffic Order City')
            fig = traffic_order_city( df1 )
            st.plotly_chart(fig, use_container_width=True)
                

#=======================================
# VISAO TATICA
#=======================================

#============= CONTAINER 01 ============
with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig = order_by_week( df1 )
        st.plotly_chart(fig, use_container_width=True)
        
        
#============= CONTAINER 02 ============        
    with st.container():
# Quantidade de pedidos por entregador por Semana
# Quantas entregas na semana / Quantos entregadores únicos por semana
        st.markdown('# Order Share by Week')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)


#=======================================
# VISAO GEOGRAFICA
#=======================================

with tab3:
    st.markdown('### Country Maps')
    country_maps(df1)




    