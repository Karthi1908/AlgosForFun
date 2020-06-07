# -*- coding: utf-8 -*-
"""
Created on Sun May 31 08:44:06 2020
Momentum strategies in Forex
Backtesting if the 20 day monentum forex paris provides any indication of future price
@author: karth
"""

import requests
from datetime import datetime, timedelta
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from pandas.io.json import json_normalize
from statsmodels.tsa.stattools import adfuller


API_key = 'Bearer ' + 'ADD YOUR API KEY'
headers = {
         'Accept': 'application/json',
         'Authorization' : 'Bearer ' + 'ADD YOUR API KEY' ,
        # 'Accept-Datetime-Format' : 'RFC3339'
          }

def get_account():
    r = requests.get('https://api-fxpractice.oanda.com/v3/accounts',  
                    headers = headers)
    print(r.json()['accounts'][0]['id'])
    return r.json()['accounts'][0]['id']
    
def get_instruments(account):
   
    link = 'https://api-fxpractice.oanda.com/v3/accounts/' + account + '/instruments'
    r = requests.get(link, headers = headers)
    #print(r.json()['instruments'])
    return r.json()['instruments']

def get_prices(instrument ,n=0 , ind):
    
    if ind == 'T' :
        end_dt = time.time() - (n * 7 * 24 * 3600)
        start_dt = end_dt - (25 * 24 * 3600)
    else:
        end_dt = time.time() - ((n-1) * 7 *24 *3600)
        start_dt = end_dt - (7 * 24 * 3600)        
    #print(end_dt,start_dt)
    
    link = 'https://api-fxpractice.oanda.com/v3/instruments/'+ instrument + '/candles'
    r = requests.get(link, 
                     params = {'price' : 'M', 
                               'granularity': 'H1', 
                          #     'count' : '120',
                               'from' : start_dt,
                               'to': end_dt}, 
                     headers = headers)
    #print(r.json()['instruments'])
    #print(r.json())
    return r.json()['candles']
def main():
    account = get_account()
    #instruments = pd.DataFrame()
    #instruments = json_normalize(get_instruments(account)) 
    #print(instruments[instruments['name'].str.contains('INR',case=True)].name)
  
    currency = ['EUR_USD','USD_JPY','USD_SGD','AUD_USD','AUD_JPY','AUD_NZD','AUD_CAD','EUR_JPY','SGD_JPY','USD_INR','USD_TRY','USD_CAD','GBP_JPY','CAD_JPY','EUR_GBP','GBP_USD']
    #currency1 =['USD_INR','EUR_INR','GBP_INR','JPY_INR']
    ins =pd.DataFrame()
    ins_test = pd.DataFrame()
    result =pd.DataFrame()
    for n in range(1, 50) :
        for cpairs in currency:
            ins[cpairs]=(json_normalize(get_prices(cpairs,n,'T'))['mid.c'])
            ins[cpairs]= pd.to_numeric(ins[cpairs],errors = 'coerce').fillna(method = 'ffill')
            ins_test[cpairs]=(json_normalize(get_prices(cpairs,n,'t'))['mid.c'])
            ins_test[cpairs]= pd.to_numeric(ins_test[cpairs],errors = 'coerce').fillna(method = 'ffill')
            time.sleep(2)
        ins_return = ins.iloc[-1]/ins.iloc[0] -1
        ins_test_return = ins_test.iloc[-1]/ins_test.iloc[0] -1
        train_test = pd.concat([ins_return ,ins_test_return],axis =1, sort = False)
        result = pd.concat([result,train_test],axis =0, sort = False)
    #ort_values(ascending = False, inplace = True)
        print(train_test)
    result.to_csv('Forex_Momentum2.csv')
    print(result)
        
        
main()
    
 
    
    
