# -*- coding: utf-8 -*-

#test push
# -*- coding: utf-8 -*-


import pandas as pd
import os
import numpy as np
import pickle as pk
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
  liste_crypto= np.array(['BTC/USDT', 'ETH/USDT', 'ADA/USDT','DOGE/USDT', 'BNB/USDT', 'UNI/USDT','SOL/USDT','KSM/USDT',
                    'LTC/USDT', 'BCH/USDT', 'LINK/USDT', 'VET/USDT', 'XLM/USDT', 'FIL/USDT','TRX/USDT', 
                    'NEO/USDT','EOS/USDT','DOT/USDT','AAVE/USDT', 'MATIC/USDT', 'LUNA/USDT', 'THETA/USDT', 
                    'AXS/USDT', 'ENJ/USDT','SAND/USDT','WIN/USDT','SLP/USDT'])
  
    
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
  
  aave = cols3[0].checkbox('AAVE/USDT')
  matic = cols3[1].checkbox('MATIC/USDT')
  luna = cols3[0].checkbox('LUNA/USDT')
  theta = cols3[1].checkbox('THETA/USDT')
  sol  = cols3[1].checkbox('SOL/USDT')
  ksm = cols3[0].checkbox('KSM/USDT')
  
  axs = cols3[2].checkbox('AXS/USDT')
  enj = cols3[2].checkbox('ENJ/USDT')
  sand = cols3[0].checkbox('SAND/USDT')
  win = cols3[1].checkbox('WIN/USDT')
  slp = cols3[2].checkbox('SLP/USDT')
  
 
  
  

  
      
  liste_boolean = np.array([btc, eth, ada, doge, bnb, uni ,sol ,ksm ,ltc ,bch ,link ,vet ,xlm ,fil ,trx ,neo ,eos ,dot ,aave ,matic ,luna ,theta ,
                            axs ,enj ,sand ,win ,slp])
                         
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
                                 name='coef_multi_BX1',
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


def plot_courbes2(df_tableau_multi):
    fig=go.Figure()     
    for elm in df_tableau_multi.columns:                     
        fig.add_trace(go.Scatter(x= df_tableau_multi[elm].index, 
                                 y= df_tableau_multi[elm],
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
    liste_tableau_multi=[]
    for elm in market : 
        x =elm.lower() 
        crypto[x] = crypto[x].merge(variation(crypto[x]),on ='timestamp',how='left')
        crypto[x]['coef_multi_'+x[:3]]=coef_multi(crypto[x])
        crypto[x]  = fonction_cumul(crypto[x],x) 
        liste_tableau_multi.append(crypto[x]['coef_multi_'+x[:3]])
    df_tableau_multi = pd.concat(liste_tableau_multi, axis = 1)
    
        
        
        
        
        
    df_liste_var =  fonction_tableau_var(crypto)   
    tableau_var = meilleur_varaition(df_liste_var) 
     
    tableau_var['algo'] = algo(tableau_var)
    tableau_var['coef_multi'] = tableau_var['algo'].cumprod()
    tableau_var['coef_cumul']= tableau_var['coef_multi'].apply(lambda x : (x*100)-100)
    
    
    
   
    
    df_tableau_multi = pd.concat( [df_tableau_multi, tableau_var['coef_multi']] , axis=1)
    df_tableau_multi = df_tableau_multi.rename(columns={"coef_multi" :"botmax1"})
    
    plot_courbes2(df_tableau_multi)
    st.write( df_tableau_multi.tail(1))
    
    
    
    if st.checkbox('Voir tableau coef multi') :      
      st.write(df_tableau_multi)    
    
    if st.checkbox('Voir tableau de variation'):
       st.write(tableau_var)
        
    if st.sidebar.button("Download tableau de variation "):      
            df_download = tableau_var
            csv = df_download.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()  # some strings
            linko= f'<a href="data:file/csv;base64,{b64}" download= tableau_var.csv> Download tableau_var csv file</a>'
            st.markdown(linko, unsafe_allow_html=True)
            
    if st.sidebar.button("Download tableau coef multi "):      
            df_download = df_tableau_multi
            csv = df_download.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()  # some strings
            linko= f'<a href="data:file/csv;base64,{b64}" download= tableau_multi.csv> Download df_tableau_multi csv file</a>'
            st.markdown(linko, unsafe_allow_html=True)
    
    if st.sidebar.button (" Download cryptos"):
      for elm in market :
            df_download= crypto[elm.lower()].reset_index()
            csv = df_download.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()  # some strings
            linko= f'<a href="data:file/csv;base64,{b64}" download='+elm.lower()+'.csv>Download '+elm.lower()[:3]+ ' csv file</a>'
            st.markdown(linko, unsafe_allow_html=True)
    
   

    
   
    
    
  
    
    
    
    
    
if __name__ == '__main__':
    main()
