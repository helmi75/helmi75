# -*- coding: utf-8 -*-

import pandas as pd
import os
import numpy as np
import pickle
import matplotlib.pyplot as plt 
from datetime import datetime
from time import time 
from datetime import timedelta
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
import base64
import ccxt
from fonctions import *
import time as tm



 
crypto ={}
choix_market()
  
    
apiKey = st.text_input("Enter Apikey", type="password")
secret = st.text_input("Enter a Secretkey", type="password")



dth= st.selectbox('delta_hour',['1m', '5m','15m', '1h','4h','6h','8h','12h','1d'], index = 5)
i_iteration = st.number_input('intervale d\'itération (min) ', 1,value= 5)

delta_hour = dth


exchange = ccxt.binance({
    'apiKey': apiKey,
    'secret': secret,
    'enableRateLimit': True
    })
st.write("wech bien ou quoi ? ")

# initialisation temps 

start_time = datetime.now()
k=0
liste_principale=[]
liste_achat=[]
liste_vente=[]
temps=[]

bouton_run = st.button("run")
if bouton_run:
    while True:

        print("première iteration  : ",start_time)   
        print("horaire now",datetime.now())
        print ("iteration numéto : ", k)

        st.write("première iteration  : ",start_time) 
        st.write("horaire now", datetime.now())
        st.write("iteration numéto : ", k)


        for elm in market :
            x =elm.lower()
            ohlcv = exchange.fetch_ohlcv(elm , limit = 2, timeframe = delta_hour)
            crypto[x] = pd.DataFrame(ohlcv,columns=['timestamp', x[:3]+'_open', 'high','low', x[:3]+'_close', 'volume'])
            crypto[x] = convert_time(crypto[x])
            crypto[x] = crypto[x][['timestamp',x[:3]+'_open',x[:3]+'_close']] 
            crypto[x] = crypto[x].set_index('timestamp')
            crypto[x] = crypto[x].merge(variation(crypto[x]),on ='timestamp',how='left')
            crypto[x]['coef_multi_'+x[:3]]=coef_multi(crypto[x])
            crypto[x]  = fonction_cumul(crypto[x],x)


        df_liste_var =  fonction_tableau_var(crypto)   
        tableau_var = meilleur_varaition(df_liste_var) 
        tableau_var['algo'] = algo(tableau_var)
        tableau_var['coef_multi'] = tableau_var['algo'].cumprod()
        nom_crypto_achat =  nom_crypto_achat_vente(tableau_var)
        nom_crypto_vente= crypto_a_vendre(exchange,2, market ) 
        
        algo_achat_vente(exchange, nom_crypto_vente, nom_crypto_achat)
        
        print('la crypot à vendre est ',nom_crypto_vente)
        print('la crypot à acheter est ',nom_crypto_achat)


        k=k+1
        liste_principale.append([datetime.now(), nom_crypto_achat, nom_crypto_vente])
        st.write(tableau_var)
        st.write(pd.DataFrame(liste_principale, columns=['temps','crypto vente','crypto achat']))
        
        if nom_crypto_achat ==  nom_crypto_vente:
            st.write('On reste sur la même crypto')
        else:
            st.write('crypto à vendre ',nom_crypto_vente)
            st.write('crypto à acheter',nom_crypto_achat)
       


        tm.sleep(60*i_iteration)
