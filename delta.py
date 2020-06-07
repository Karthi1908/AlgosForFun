# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 22:24:41 2020
Delta exchange Trades
Back testing of multiple strategies and their combination on Delta Exchange.

@author: karth
"""
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import talib
import hashlib
import hmac
import base64
import requests
import datetime
import json

api_key = 'a1289987f545093504bfa3a6530f27'
api_secret = '43e6e8f3368d4ceb1ad342863c9a1de51e22ecb1130f7ca98ccc104917df'
#url = 'https://api.delta.exchange'

headers = {
         'Accept': 'application/json'
          }


def place_order(side):
    method = 'POST'
    url = "https://api.delta.exchange/orders"
    side=''
    timestamp = get_time_stamp()
    path = '/orders'
    query_string = ''
    
    if side == 'buy' :
        payload ="{\"order_type\":\"limit_order\",\"size\":1000,\"side\":\"buy\",\"limit_price\":\"0.2\",\"product_id\":187}"
    else:
        payload ="{\"order_type\":\"limit_order\",\"size\":1000,\"side\":\"sell\",\"limit_price\":\"0.2\",\"product_id\":187}"
        print(payload)
    pay ={"order_type":"market_order","size":9000,"side":"sell","limit_price":"0.2","product_id":187}
    payload = str(pay)
    print(payload)
    signature_data = method + timestamp + path + query_string + payload
    signature = generate_signature(api_secret, signature_data)

    req_headers = {
            'api-key': api_key,
            'timestamp': timestamp,
            'signature': signature,
            'User-Agent': 'rest-client',
            'Content-Type': 'application/json'
            }

    response = requests.request(
            method, url, data=payload, params={}, timeout=(3, 27), headers=req_headers
            )
    print(response.json())

def generate_signature(secret, message):
    message = bytes(message, 'utf-8')
    secret = bytes(secret, 'utf-8')
    hash = hmac.new(secret, message, hashlib.sha256)
    return hash.hexdigest()

def get_time_stamp():
    d = datetime.datetime.utcnow()
    epoch = datetime.datetime(1970,1,1)
    return str(int((d - epoch).total_seconds()))

def initialize(symbol):
    ins_df = pd.DataFrame()
    end_time = int(time.time())- (0 * 24 * 3600)
    start_time = end_time - (20 * 24 * 60 * 60)

    r = requests.get('https://api.delta.exchange/chart/history',  
                     params={'symbol': symbol,
                             'from' : start_time,
                             'to' : end_time,
                             'resolution': '60'},
                     headers = headers)
    ins_df = pd.DataFrame(r.json(),columns =['t','o','h','l','c','v'])
    #print(ins_df.head())
    print(ins_df.shape)
    return (ins_df.astype(float))

def get_instruments():
    r = requests.get('https://api.delta.exchange/products', params={}, 
                     headers = headers)
    return r.json()


def main():
    #account = get_account()
    #instruments = pd.DataFrame()
    #instruments = json_normalize(get_instruments()) 
    #print(instruments[instruments['symbol'].str.contains('USD',case=True)].symbol)
  

    currency1 =['BTCUSDT','LTCUSDT','ETHUSDT','XRPUSDT','LINKUSDT']
    for cpairs in currency1:
        ins =pd.DataFrame()
        #ins=(get_price_history(cpairs))[['high','low','close']]
       
        ins1 = initialize(cpairs)[['o','h','l','c']]
        ins['open'] = ins1['o']
        ins['high'] = ins1['h']
        ins['low']  = ins1['l']
        ins['close']= ins1['c']     
        ins=ins.apply(pd.to_numeric,errors='coerce')
        ins.fillna(method = 'ffill', inplace = True)
        ins['ADX'] = talib.ADX(ins['high'],ins['low'],ins['close'],timeperiod=13)
        ins['RSI'] = talib.RSI(ins['close'],timeperiod=14)
        ins['DI_POS']= talib.PLUS_DI(ins['high'],ins['low'],ins['close'],timeperiod=13)
        ins['DI_NEG']= talib.MINUS_DI(ins['high'],ins['low'],ins['close'],timeperiod=13)
        ins['SAR']   = talib.SAR(ins['high'],ins['low'])
        ins['trigger'] =0
        #ins['trigger'] = np.where(((ins['DI_POS'] > ins['DI_NEG']) & (ins['RSI'] > 55)), 1, ins['trigger'])
        #ins['trigger'] = np.where(((ins['DI_POS'] < ins['DI_NEG']) & (ins['RSI'] < 45)), -1, ins['trigger'])
        #ins['trigger'] = np.where(((ins['RSI'] > 65) & (ins['DI_POS'] < 32) & (ins['ADX'] <50)),-1,ins['trigger'])
        #ins['trigger'] = np.where(((ins['RSI'] < 35) & (ins['DI_NEG'] < 32) & (ins['ADX'] <50)),1,ins['trigger'])
        ins['trigger'] = np.where(((ins['SAR'] > ins['high'])  ),1,ins['trigger'])
        ins['trigger'] = np.where(((ins['SAR'] < ins['low'])  ),-1,ins['trigger'])
        #ins['trigger'] = np.where(((ins['SAR'] > ins['high']) &(ins['RSI'] > 55)),1,ins['trigger'])
        #ins['trigger'] = np.where(((ins['SAR'] < ins['low'])  &(ins['RSI'] < 45)),-1,ins['trigger'])
        #ins['trigger'] = np.where(((ins['SAR'] > ins['high']) &(ins['DI_POS'] > ins['DI_NEG'])),1,ins['trigger'])
        #ins['trigger'] = np.where(((ins['SAR'] < ins['low'])  &(ins['DI_POS'] < ins['DI_NEG'])),-1,ins['trigger'])

        ins.dropna(inplace=True)
        ins['ret'] = (ins['close'] - ins['close'].shift(1) )/ins['close'].shift(1)
        ins['return'] = ins['ret'] + 1
        ins['strat_ret'] = ins['ret'] * ins['trigger'].shift(1) + 1
       
        print(cpairs,'Return ', np.round(np.prod(ins['return']),6),'Strat Return ',np.round(np.prod(ins['strat_ret']),6))
        ins[['return','strat_ret']].cumprod().plot(title =cpairs)
    #ort_values(ascending = False, inplace = True)
    

        
main()
