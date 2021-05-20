# -*- coding: utf-8 -*-
from datetime import datetime
from time import time 
from datetime import timedelta
import numpy as np 
import pandas as pd
import time as tm
import streamlit as st
import plotly.graph_objects as go






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
  serie_variation = ((close)/open_)
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
  dataframe['timestamp'] =pd.DatetimeIndex(pd.to_datetime(temps)).tz_localize('UTC').tz_convert('UTC')
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
def down_all_coin(name_crypto ,star_time, end_time, delta_hour,exchange):
  all_coin=[]  
  for time in range(star_time, end_time, int(28857600000)):
    all_coin.append(exchange.fetch_ohlcv(name_crypto, limit = 1000 ,since= time, timeframe = delta_hour))
    con_all_coin = np.concatenate(all_coin)  
  df_all_coin = pd.DataFrame(con_all_coin, columns=['timestamp', name_crypto[:3].lower()+'_open', 'high','low', name_crypto[:3].lower()+'_close', 'volume'])  
  df_all_coin = convert_time(df_all_coin).drop_duplicates() 
  return df_all_coin


def fonction_cumul(dataframe, name_crypto ):
  dataframe['cumul_'+name_crypto[:3]]=((dataframe['coef_multi_'+name_crypto[:3]])*100)-100
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
   fig.add_trace(go.Scatter(x= dataframe.index, y= dataframe[cumul],mode='lines',name='test affichage'))
   return fig
    
def to_timestamp(date):
    element = datetime.strptime(date,"%Y-%m-%d")
    timestamp = int(datetime.timestamp(element))*1000
    return timestamp


def fonction_tableau_var (dictionnaire_crypto):
    liste_var =[]
    liste_crypto=[]
    index=[]
    for nom_crypto in dictionnaire_crypto :
      liste_var.append(dictionnaire_crypto[nom_crypto][nom_crypto[:3]+'_var'])
      
      liste_crypto.append(nom_crypto[:3]+'_var') 
      
          
    index = dictionnaire_crypto[nom_crypto].index
    #print(np.transpose(liste_var))
    
    df_liste_var = pd.DataFrame(np.transpose(liste_var),columns=liste_crypto).set_index(index)     
    return df_liste_var


# algorithme  qui cherche la meilleur valeur d'une crypto à  un instant t 
# ENtrée dataframe 
#sortie dataframe 2 colinnes 
def meilleur_varaition(dataframe):       
    max_var = dataframe.max(axis=1) 
    name_max_var = dataframe.idxmax(axis=1)   
    concat_meilleur_var = pd.concat([max_var, name_max_var],axis=1)       
    concat_meilleur_var = pd.concat([dataframe, concat_meilleur_var],axis=1)    
    concat_meilleur_var.rename(columns={0:'var_max',1:'meilleur_var'}, inplace=True)    
    return concat_meilleur_var
 
def concat_meilleur_var(concat_meilleur_var):
    concat_meilleur_var['variation_bx1'] = (concat_meilleur_var[0]*100)-100    
    concat_meilleur_var['cumul_bx1']=concat_meilleur_var['variation_bx1'].cumsum()    
    return concat_meilleur_var
    

#entré dataaframe des varaibles 
def  algo(concat_meilleur_var):
    tempo=[]
    list_valeur_algo=[]
    nbr_colon = len(concat_meilleur_var.columns)-2    
    df_utile = concat_meilleur_var.iloc[:,:nbr_colon]
    serie_var_max = concat_meilleur_var['var_max']
    df_utile['index'] = range(len(serie_var_max))
    df_utile.set_index('index',inplace=True)        
    nom_init = df_utile[df_utile.index==0].idxmax(axis=1).values[0]   
    tempo.append(df_utile[df_utile.index==0][nom_init ].values)
    for i in range(0, len(df_utile)-1):
        name_i_max = df_utile[df_utile.index==i].idxmax(axis=1).values[0]               
        tempo.append(df_utile[df_utile.index==i+1][name_i_max].values)   
    for elm in  tempo:
        list_valeur_algo.append(elm[0])    
    return list_valeur_algo


#entré dataframe  le tableau de variation
# sortie le nom de la crypto
def nom_crypto_achat_vente(tableau_var ):
    #print(tableau_var.iloc[:,:5])
    if tableau_var['meilleur_var'].iloc[0]==tableau_var['meilleur_var'].iloc[1]:
        return False
    else :
        name_cryptos = tableau_var['meilleur_var'].iloc[0][:3].upper()+'/USDT'
        if name_cryptos == 'DOG/USDT':
            name_cryptos ='DOGE/USDT'
        elif name_cryptos == 'LIN/USDT':
             name_cryptos = 'LINK/USDT'
        else :
            pass        
        return name_cryptos
    
    
 # Achat
   

    
# entrée nom crypto un string ex :  'DOGE/USDT'        
def  algo_achat_vente(exchange , nom_crypto_vente, nom_crypto_achat):
    
    balence= exchange.fetchBalance ()
    print('montant portefeuille en EUSDT',balence['total']['USDT'])
    print('montant portefeuille en BTC ',balence['total']['BTC'])
    print('montant portefeuille en ETH ',balence['total']['ETH']) 
    
    
    if (nom_crypto_achat == False) or (nom_crypto_achat == nom_crypto_vente):
         
         print( 'on reste sur la même crypto' )
         pass
    else :         
        #Vendre 
        sell = vente (exchange,  nom_crypto_vente , balence['total'])
        
        
        tm.sleep(5)   
        
        def acheter(exchange ,var2, balence_total, pourcentage):
            montant_USDT = float(exchange.fetch_balance().get('USDT').get('free'))
            
            dic = exchange.fetchTicker(var2)
            dic['last']
            
            buy = exchange.create_market_buy_order (var2 ,(montant_USDT*pourcentage)/ dic['last'])
            return  buy   
        
        #achat        
        while True :
            try :
                acheter = acheter(exchange ,nom_crypto_achat, balence['total'],1)
                print('crypto achetée ' )
                break
            except :
                print('EXECUTION AVEC EXEPTION')
                acheter = acheter(exchange ,nom_crypto_achat, balence['total'],0.065)                
                break
        
    


   

    
    
def vente (exchange, var1, balence_total) :
     sell = exchange.create_market_sell_order (var1,balence_total[var1[:-5]])     
     return sell 
 


    
def sleep_time(sec):
    for elm in range(sec):
        print(elm)
        tm.sleep(sec)  
        
        
def crypto_a_vendre(exchange, minutes, market ):
    
    x = (datetime.now()- timedelta(days = minutes)).timestamp()*1000
    df_hystoric_order={}
    liste_df =[]
    liste_name_crypto=[]
    for name_crypto in market :  
        name_crypto_low = name_crypto.lower()            
        df_hystoric_order[name_crypto_low]= pd.DataFrame.from_dict(exchange.fetchMyTrades(name_crypto, since = int(x)))
       
        index_dernier_ordre = df_hystoric_order[name_crypto_low].index.max() 
       
        liste_df.append(df_hystoric_order[name_crypto_low].loc[index_dernier_ordre])     
      
    
    df_log = pd.DataFrame(liste_df).set_index('symbol')
    st.write(df_log)
    
    crypto_a_vendre = df_log[df_log['side']=='buy'].index[0]
    return crypto_a_vendre
  
  
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
  #bx1 = cols3[1].checkbox('BX1/USDT')    
  liste_boolean = np.array([btc, eth, ada, doge, bnb, uni,
                     ltc, bch, link, vet, xml, fil, trx, neo, eos, dot])    
  return liste_crypto[liste_boolean]



def pipeline_crypto(market, exchange, delta_hour):
     
     crypto ={}
     for elm in market :
            x =elm.lower()
            ohlcv = exchange.fetch_ohlcv(elm , limit = 1000, timeframe = delta_hour)
            crypto[x] = pd.DataFrame(ohlcv,columns=['timestamp', x[:3]+'_open', 'high','low', x[:3]+'_close', 'volume'])
            crypto[x] = convert_time(crypto[x])
            crypto[x] = crypto[x][['timestamp',x[:3]+'_open',x[:3]+'_close']] 
            crypto[x] = crypto[x].set_index('timestamp')
            crypto[x] = crypto[x].merge(variation(crypto[x]),on ='timestamp',how='left')
            crypto[x]['coef_multi_'+x[:3]]=coef_multi(crypto[x])
            crypto[x]  = fonction_cumul(crypto[x],x)
     return crypto
 
def plot_courbes(crypto, tableau_var):
    fig=go.Figure()
    for elm in crypto: 
        
        fig.add_trace(go.Scatter(x= crypto[elm].index, 
                                 y= crypto[elm]['cumul_'+elm[:3]],
                                 mode='lines',
                                 name=elm[:3],
                                 ))  
    fig.add_trace(go.Scatter(x= tableau_var.index, 
                                 y= tableau_var['coef_multi'],
                                 mode='lines',
                                 name='BX1',
                                 )) 
    fig.update_layout(
    title="Variation cumulées ",
    xaxis_title="date",
    yaxis_title="cumul ",
    legend_title="cryptos",
    )
        
    return st.plotly_chart(fig)
 