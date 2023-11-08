import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit_authenticator as stauth
from st_aggrid import AgGrid
import pickle
from pathlib import Path

hubs=pd.read_excel("hubs.xlsx")
hubs=hubs[0].tolist()

trucksok=['Any','Flatbed','Reefer','Truck&Trailer','Van']
#info_sidebar=['BrokerRating','BrokerDaysToPay']
columnsoutput=['CityOrigin', 'CountyOrigin', 'PickUp', 'CityDestination',  'CountyDestination', 
               'DropOff', 'Distance','RatePerMile','Broker_Shipper',
               'Broker_Shipper_Email', 'Broker_Shipper_Phone','Weight','Size',   
               'PickUp_Stops', 'DropOff_Stops', 'Specifications', 'Commodity']

df=pd.read_parquet("dfloads.parquet")
#page = st.sidebar.radio("Select page", ["Search", "Brokers"])

#----------- LOADS PAGE ----------------------

def mi_aplicacion():
    
    authenticator.logout("Logout",'main')
    st.title("Loads request")
    st.write(f'Welcome, {name}')
    st.write("To filter the available loads and contact brokers to start the booking process")
    
    column1, column2, column3 = st.columns(3, gap="medium")
    size=0
    weight=0
    
    with column1:
        cityorigin=st.selectbox('Hub Origin:', hubs)
        equip = st.multiselect('Truck type:', trucksok)
        button= st.button("Search")
        equip = ''.join(equip)
    
    with column2:
        citydestination=st.selectbox('Hub Destination:', hubs)
        size=st.slider('Optional/Max truck lenght (ft)',0,53)

    with column3:
        pickup = st.date_input("Pick-up date")
        weight= st.slider('Optional/Max load weight (Pounds)',0,60000,value=0,step=5000)

    if button:
        
        df2=(df.query("HubOrigin==@cityorigin and HubDestination == @citydestination and PickUp>=@pickup")).loc[(df['Equip'].str.contains(equip))].sort_values('RatePerMile',ascending=False)
    
        if weight >0 or size > 0:
            
            if weight>0:
                df3=df2.query("Weight<=@weight or Weight.isna()")
                id_weight=set(df3['ID'])
                if df3.shape[0] == 0:
                    st.write("There's no loads that accomplish the conditions of load weight")
                    
            if size>0:
                df4=df2.query("Size<=@size or Size.isna()")
                id_size=set(df4['ID'])
                if df4.shape[0] == 0:
                    st.write("There's no loads that accomplish the conditions of truck size")
                    
            if size >0 and weight > 0:
                print("Entró acá1")
                ids=id_weight.intersection(id_size)
                df2=df2[df2['ID'].isin(ids)]  
                AgGrid(df2[columnsoutput],width='100%')
                
            if size >0 and weight == 0:
                print("Entró acá2")
                AgGrid(df4[columnsoutput],width='100%')
                
            if size ==0 and weight > 0:
                print("Entró acá3")
                AgGrid(df3[columnsoutput],width='100%')
 
        if weight ==0 and size == 0:
            print("Entró acá4")
            AgGrid(df2[columnsoutput],width='100%')

#-----------------AUTHENTICATION PAGE--------------

names=["Karen Gomez","Dariela Castro"]
usernames=["kren22g","darielamcp"]
password=["karen22","amadelosdatos123"]
hashed_passwords = stauth.Hasher(password).generate()
    
authenticator = stauth.Authenticate(names, usernames, hashed_passwords,"loads_dashboard", "abcdef", cookie_expiry_days=15)

name, authentication_status, username = authenticator.login("Login","main")

if authentication_status== False:
    st.error("Username or password is correct")
    
if authentication_status== None:
    st.warning("Please enter your username or password")
    
if authentication_status== True:
    mi_aplicacion()