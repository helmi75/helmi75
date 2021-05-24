# -*- coding: utf-8 -*-

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

from config import *
from fonctions import *

def choix_market():
  liste_crypto= np.array(['BTC/USDT', 'ETH/USDT', 'ADA/USDT','DOGE/USDT', 'BNB/USDT', 'UNI/USDT',
                    'LTC/USDT', 'BCH/USDT', 'LINK/USDT', 'VET/USDT', 'XLM/USDT', 'FIL/USDT','TRX/USDT', 
                    'NEO/USDT','EOS/USDT','DOT/USDT'])
  cols3 = st.beta_columns(3)    
  btc = cols3[0].checkbox('BTC/USDT')
  eth = cols3[0].checkbox('ETH/USDT')
  ada = cols3[0].checkbox('ADA/USDT')
  doge = cols3[0].checkbox('DOGE/USDT')
  bnb = cols3[0].checkbox('BNB/USDT')
  uni = cols3[1].checkbox('UNI/USDT')
  bch = cols3[1].checkbox('BCH/USDT')
  link = cols3[1].checkbox('LINK/USDT')
  vet = cols3[1].checkbox('VET/USDT')
  xml = cols3[1].checkbox('XLM/USDT')
  fil = cols3[2].checkbox('FIL/USDT')
  ltc = cols3[2].checkbox('LTC/USDT')
  trx = cols3[2].checkbox('TRX/USDT')
  neo = cols3[2].checkbox('NEO/USDT')
  eos = cols3[2].checkbox('EOS/USDT')
  dot = cols3[2].checkbox('DOT/USDT')
  
      
  liste_boolean = np.array([btc, eth, ada, doge, bnb, uni,
                     ltc, bch, link, vet, xml, fil, trx, neo, eos, dot])    
  return liste_crypto[liste_boolean]

def plot_courbes(crypto, tableau_var, multi_BX1, cumul_BX1):
    fig=go.Figure()
    for elm in crypto: 
        
        fig.add_trace(go.Scatter(x= crypto[elm].index, 
                                 y= crypto[elm]['cumul_'+elm[:3]],
                                 mode='lines',
                                 name=elm[:3],
                                ))
    if multi_BX1:
        fig.add_trace(go.Scatter(x= tableau_var.index, 
                                 y= tableau_var['coef_multi'],
                                 mode='lines',
                                 name='Bot max 1',
                                 )) 
    
    if cumul_BX1 :
        fig.add_trace(go.Scatter(x= tableau_var.index, 
                                 y= tableau_var['coef_cumul'],
                                 mode='lines',
                                 name='coef_cumul_BX1',
                                 ))
    else :
        pass
    
    fig.update_layout(
    title="Variation cumulées ",
    xaxis_title="date",
    yaxis_title="cumul ",
    legend_title="cryptos",
    )
    return st.plotly_chart(fig)


def plot_courbes2(tableau_var):
    fig=go.Figure()
     
    for elm in tableau_var.iloc[:,:-5]:
        tableau_var[elm]       
        fig.add_trace(go.Scatter(x= tableau_var[elm].index, 
                                 y= tableau_var[elm],
                                 mode='lines',
                                 name=elm,
                                 )) 
    return st.plotly_chart(fig)

def main():
    
    star_time = to_timestamp(str(st.date_input('date de début',date_init ))) #1502928000000
    end_time = to_timestamp(str(st.date_input('date de fin')))
    delta_hour = st.selectbox('selectionner une plage auraire',['4h','6h','8h','12h'])
    
   
    
      
    crypto = {}
    boxmax ={}
    market= choix_market()
    
    for elm in market :
        x =elm.lower()   
        crypto[x] = down_all_coin(elm ,star_time, end_time,delta_hour,exchange) #
        crypto[x]=pd.DataFrame(data=crypto[x], columns=['timestamp', x[:3]+'_open', 'high','low', x[:3]+'_close', 'volume']) 
        crypto[x] = crypto[x][['timestamp',x[:3]+'_open',x[:3]+'_close']]     
        #crypto[x] = convert_time(crypto[x])
        crypto[x] = crypto[x].set_index('timestamp')
    
    
    array_mauvais_shape = detection_mauvais_shape(crypto)
    crypto = correction_shape(crypto, array_mauvais_shape)
    for elm in array_mauvais_shape :
        crypto[elm]['timestamp'] = generation_date (crypto[elm], int(delta_hour[:1]))
        crypto[elm] =  crypto[elm].set_index('timestamp') 
    for elm in market : 
        x =elm.lower() 
        crypto[x] = crypto[x].merge(variation(crypto[x]),on ='timestamp',how='left')
        crypto[x]['coef_multi_'+x[:3]]=coef_multi(crypto[x])
        crypto[x]  = fonction_cumul(crypto[x],x) 
        
        
        
        
        
    df_liste_var =  fonction_tableau_var(crypto)   
    tableau_var = meilleur_varaition(df_liste_var) 
    
    tableau_var['algo'] = algo(tableau_var)
    tableau_var['coef_multi'] = tableau_var['algo'].cumprod()
    tableau_var['coef_cumul']= tableau_var['coef_multi'].apply(lambda x : (x*100)-100)
    
    multi_BX1 = st.checkbox('Bot max 1')
    cumul_BX1 = st.checkbox('cumul_BX1')
   
    plot_courbes(crypto, tableau_var,multi_BX1, cumul_BX1)
    st.write(tableau_var)
    
   
    
    
   

    
   
    
    
  
    
    
    
    
    
if __name__ == '__main__':
    main()
