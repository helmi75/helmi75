# -*- coding: utf-8 -*-

import ccxt
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


exchange = ccxt.binance({
       
    'enableRateLimit': True
    })


# generation de dataframe test
def generation_test(k,name_crypto,timestamp):
  import random
  numeros = range(0,100000)
  liste1 = random.choices(numeros,k=k)
  liste2 = random.choices(numeros,k=k)
  index=timestamp[:k]
  df =pd.DataFrame(liste1,liste2).reset_index().set_index(index)
  df= df.rename(columns={"index": name_crypto[:3]+"_open",0 : name_crypto[:3]+"_close"})
  crypto[name_crypto]=df
  return  crypto


# Calcul  de la variation 
# ENtRE => dataframe   exemple crypto['eth/usdt'] 
# SORTIE =>  pandas.core.series.Series
def variation (dataframe) :
  
  open_ = dataframe[dataframe.columns[0]]
  close = dataframe[dataframe.columns[1]]  
  serie_variation = (close/open_)
  df_serie_variation = pd.DataFrame(serie_variation, dataframe.index, columns=[dataframe.columns[0][:3]+'_var'])
  return df_serie_variation







# Calcul du coef_multiplicateur 
# entre =>  Dataframe  exemple crypto['eth/usdt']
# sortie => pandas.Series du coeffitient multiplicateur
def coef_multi(dataframe): 
  liste_finale = []
  for i in  range (len(dataframe.index)):
    if dataframe[dataframe.columns[2]][i]==0:
      liste_finale.append(0)
    else:
      break  
  var_zeros = dataframe[dataframe.columns[2]][:i]
  var_sans_zero = dataframe.iloc[i:][dataframe.columns[2]]
  var_sans_z_cumprod = var_sans_zero.cumprod()
  coef_multi = pd.concat([var_zeros,var_sans_z_cumprod])
  return coef_multi


#
#converti timestamp en datatime 
# entrée dataframe
# Sortie dataframe
def convert_time(dataframe): 
  temps=[]
  for elm in  dataframe['timestamp']:
    temps.append(datetime.fromtimestamp(elm/1000))     
  dataframe['timestamp'] =pd.DatetimeIndex(pd.to_datetime(temps)).tz_localize('UTC').tz_convert('US/Eastern')
  return dataframe


# foction pour détecter les mauvai shape
# entrée dictionnaire
# Sortie array
def detection_mauvais_shape(dictionaire_crypto):
  liste_shape =[]
  liste_crypto=[]
  boulean =[]
  for elm in dictionaire_crypto :
    liste_shape.append(dictionaire_crypto[elm].shape[0])
    liste_crypto.append(elm)
  for elm in liste_shape :
    if elm < np.max(liste_shape):
      boulean.append(True)
    else :
      boulean.append(False)
  boulean,liste_crypto = np.array(boulean),np.array(liste_crypto)
  return  liste_crypto[boulean]




# corrections des shape en ajoutant une colonne de zero et une colonnes de ones 
# entrée dictionnaire  et array 
# Sortie dictionnaire 

def correction_shape(dictionaire_crypto, array ):
    max_shape=[]
    shape_a_manque =[]    
    liste_final=[]
    nom_shape_a_manque=[]

    #onc cherche le shape maximun dans tous le array 
    for elm in dictionaire_crypto:      
      max_shape.append(dictionaire_crypto[elm].shape[0])
    max_shape = np.max(max_shape)  

    # on calcul le shape manquant dans le array 
    for elm1 in array :
       shape_a_manque.append(max_shape - dictionaire_crypto[elm1].shape[0])    
       nom_shape_a_manque.append(elm1) 

    for shape, nom  in zip(shape_a_manque,nom_shape_a_manque) :           
        liste_final = [ np.ones(shape),np.zeros(shape) ]
        df_liste_final = pd.DataFrame(np.transpose(liste_final), columns=[nom[:3]+'_open',nom[:3]+'_close'])
        dictionaire_crypto[nom] = pd.concat((df_liste_final,dictionaire_crypto[nom]), axis=0)
    return dictionaire_crypto



# génération de datatime en fontion du pas 
#entre  dataframe  + timedelta
# sortie liste datatime

def generation_date (dataframe, delta_pas):  
  test_list=[]
  pas = timedelta(hours = delta_pas)
  date_ini = dataframe.index[::-1][0]
  
  inverse_time =dataframe.index[::-1]  
  for i in range (len(inverse_time)):
    test_list.append(date_ini-pas*i)  
  test_list = test_list[::-1]
  return test_list

# entrée  name_crypto ,star_time, end_time
# Sorite Dataframe
def down_all_coin(name_crypto ,star_time, end_time, delta_hour):
  all_coin=[]  
  for time in range(star_time, end_time, int(28857600000/2)):
    all_coin.append(exchange.fetch_ohlcv(name_crypto, limit = 1000 ,since= time, timeframe = delta_hour))
    con_all_coin = np.concatenate(all_coin)  
  df_all_coin = pd.DataFrame(con_all_coin, columns=['timestamp', name_crypto[:3].lower()+'_open', 'high','low', name_crypto[:3].lower()+'_close', 'volume'])  
  df_all_coin = convert_time(df_all_coin).drop_duplicates() 
  return df_all_coin


def fonction_cumul(dataframe, name_crypto ):
  dataframe['cumul%']=((dataframe['coef_multi_'+name_crypto[:3]])*100)-100
  return dataframe

def coef_multi2(dataframe,fontion_variation ):   
  variation  = fontion_variation.values
  ini_varia = fontion_variation[0]
  coef_multi = [ini_varia]
  for elm , i in zip(variation,variation.index) :    
    coef_multi[i] = elm*coef_multi[i-1]
    coef_multi.append(coef_multi[i])
  return coef_multi[:-1]


def plotly(dataframe,cumul):
   fig=go.Figure() 
   fig = fig.add_trace(go.Scatter(x= dataframe.index, y= dataframe[cumul],mode='lines',name='test affichage'))
   return fig
    
def to_timestamp(date):
    element = datetime.strptime(date,"%Y-%m-%d")
    timestamp = int(datetime.timestamp(element))*1000
    return timestamp




def main():
    
    st.title('Test Crypto')
    debut_time = to_timestamp(str(st.sidebar.date_input('date de début')))    
    delta_hour = st.sidebar.selectbox('selectionner une plage auraire',
                 ['4h','6h','8h','12h'])
    liste_crypto = np.array(['BTC/USDT', 'ETH/USDT', 'ADA/USDT','DOGE/USDT', 'BNB/USDT', 'UNI/USDT',
                    'LTC/USDT', 'BCH/USDT', 'LINK/USDT', 'VET/USDT', 'XLM/USDT', 'FIL/USDT','TRX/USDT', 
                    'NEO/USDT','EOS/USDT','DOT/USDT'])

    
    exchange.load_markets()    
    delat_test = 499 #limite 499
    #market=['ETH/USDT','ADA/USDT','BNB/USDT','DOGE/USDT']
    
    
    
    
    crypto = {}
    star_time=  debut_time #1502928000000
    end_time= int(datetime.now().timestamp()*1000)
    

    mar1 =1502928000000
    mar2 = 1597874400000

    print( 'depart',  debut_time )
    print('arriver',datetime.fromtimestamp (1619647200000/1000))
    market= liste_crypto #["BTC/USDT",'ETH/USDT','ADA/USDT','BNB/USDT','DOGE/USDT' ]
    
    for elm in market :
        x =elm.lower()   
        crypto[x] = down_all_coin(elm ,star_time, end_time,delta_hour) #
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
        
    
    
   
    
    
    
    select_crypto = st.selectbox('selectionner une crypto',liste_crypto )
    
    st.dataframe(crypto[select_crypto.lower()])    
    st.plotly_chart(plotly(crypto[select_crypto.lower()], select_crypto.lower()[:3]+'_close'))
    
    download=st.button('Telecharger '+select_crypto.lower()+'.csv')
    
    st.title("Selectionnez les cryptos à télécharger !")
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
                     ltc, bch, link, vet, xml, fil, trx, neo, eos,dot])
    
    download_all=st.button('Telecharger les cryptos selectionnées en .csv') 
   
    if download:
        'Download Started!'        
        df_download= crypto[select_crypto.lower()].reset_index()
        csv = df_download.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings
        linko= f'<a href="data:file/csv;base64,{b64}" download='+select_crypto.lower()+'.csv>Download csv file</a>'
        st.markdown(linko, unsafe_allow_html=True)
        
    st.write(liste_crypto[liste_boolean]) 
    if download_all :      
        st.write('Liens de téléchargement des cryptos sélectionnées ')
        for elm in liste_crypto[liste_boolean] :
            df_download= crypto[elm.lower()].reset_index()
            csv = df_download.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()  # some strings
            linko= f'<a href="data:file/csv;base64,{b64}" download='+elm.lower()+'.csv>Download '+elm.lower()[:3]+ ' csv file</a>'
            st.markdown(linko, unsafe_allow_html=True)
            
        
   
        
    
    
    
    
    
    
if __name__ == '__main__':
    main()
