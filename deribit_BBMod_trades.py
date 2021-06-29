# -*- coding: utf-8 -*-
"""
Created on Sat Jan 25 12:37:40 2020

@author: Karthikeyan
"""
import pandas as pd
import numpy as np
import datetime 
import asyncio
import websockets
import json
import requests
import time

SMA1 = 19



client_credentials = \
{
  "jsonrpc" : "2.0",
  "id" : 1000,
  "method" : "public/auth",
  "params" : {
    "grant_type" : "client_credentials",
    "client_id" : "QHeB9Ppa",
    "client_secret" : "pXdsxZzMVw2wxFH2-2knyoLJytJv20kgYwIt5fJNF6c"
  }
}



subscribe = \
    {"jsonrpc": "2.0",
     "method": "public/subscribe",
     "id": 42,
     "params": {
        "channels": ["chart.trades.BTC-PERPETUAL.1"]}
    }
buy = \
{
  "jsonrpc" : "2.0",
  "id" : 5275,
  "method" : "private/buy",
  "params" : {
    "instrument_name" : "BTC-PERPETUAL",
    "amount" : 10,
    "type" : "market",
    "label" : "market0000234"
  }
}
  
sell = \
{
  "jsonrpc" : "2.0",
  "id" : 2148,
  "method" : "private/sell",
  "params" : {
    "instrument_name" : "BTC-PERPETUAL",
    "amount" : 10,
    "type" : "market",
    "label" : "market0000234"
  }
}

ticker = \
{
  "jsonrpc" : "2.0",
  "id" : 8106,
  "method" : "public/ticker",
  "params" : {
    "instrument_name" : "BTC-PERPETUAL"
  }
}

async def call_api():
    i =0
    c=0
    tick = pd.DataFrame()
    data = pd.DataFrame()
    position = 0
    trend = ' '
    async with websockets.connect('wss://test.deribit.com/ws/api/v2') as websocket:
       await websocket.send(json.dumps(client_credentials))
       response = await websocket.recv()
       req = json.loads(response)
       index =req.keys()
       #print(index)
       if 'result' in index:
           print('Authentication sucessful')
       else:
           print('Error in Authentication')
       
       
       while websocket.open:
           await websocket.send(json.dumps(ticker))
           response = await websocket.recv()
           i = i + 1
           time.sleep(.99)         
           
           if i > 1 :
               #index_name = json.loads(response)['params']['data']['tick']
               index_name = "BTC-Perpetual"
               price = json.loads(response)['result']['last_price']
               t = datetime.datetime.now()
               #print('==================================================')
               print(index_name , price,t,i,position)
               #print('==================================================')
               t = datetime.datetime.now()
               tick = tick.append(pd.DataFrame({'index_name':index_name, 'Price':price}, index=[t,]))
               data = tick.resample('300s',label = 'right').last().ffill()
               #print(len(data))
               if(len(data) > SMA1+2 ) and len(data) > c :
                   c = len(data)
                   data['SMA1'] = np.round(data['Price'].rolling(window=SMA1).mean(),0)
                   data['STDev'] = np.round(data['Price'].rolling(window=SMA1).std(),0)
                   data['U_BAND'] = np.round(data['SMA1'] + 2.2 * data['STDev'],0)
                   data['L_BAND'] = np.round(data['SMA1'] - 2.2 * data['STDev'],0)
                   print(data.tail(2))
                   

                   if((data['Price'].iloc[-2] > data['SMA1'].iloc[-2]) and \
                   (data['Price'].iloc[-3] < data['SMA1'].iloc[-3])) :
                       trend = 'UP'
                       print("COND1:" , trend)
                   if((data['Price'].iloc[-2] < data['SMA1'].iloc[-2]) and \
                   (data['Price'].iloc[-3] > data['SMA1'].iloc[-3])) :
                       trend = 'DN'
                       print("COND2:" , trend)
                   if((data['Price'].iloc[-2] > data['L_BAND'].iloc[-2]) and \
                   (data['Price'].iloc[-3] < data['L_BAND'].iloc[-3])) :
                       trend = 'UP'
                       print("COND3:" , trend)
                   if((data['Price'].iloc[-2] < data['U_BAND'].iloc[-2]) and \
                   (data['Price'].iloc[-3] > data['U_BAND'].iloc[-3])) :
                       trend = 'DN'
                       print(trend)
                   #print(data.iloc[-1])
                   if position in [0,-1] and trend == 'UP' :
                           print( 40 * '=')
                           #print(data.iloc[-2])
                           print('******* BUY BTC ********')
                           position = 1
                           data['trade'] = 1
                           await websocket.send(json.dumps(buy))
                           buy_resp = await websocket.recv()
                           #print(json.loads(buy_resp)['result']['order']['order_state'])
                           message = "*BB*BUY BTC*** @" + str(data.iloc[-1])
                           telegram='https://api.telegram.org/bot618565857:AAH-3mWGnl2jgMFw4vPML5T1XmY6Ikx9AmU/sendMessage'
                           tparam = { "chat_id":"@ArbInfo","text":message}
                           response = requests.request("GET", telegram, params=tparam)
                              #print(data.iloc[-1])
                   elif position in [1,0] and trend == 'DN':
                           print( 40 * '=')
                           #print(data.iloc[-2])
                           print('******* SELL BTC ********')
                           await websocket.send(json.dumps(sell))
                           sell_resp = await websocket.recv()
                           #print(json.loads(sell_resp)['result']['order']['order_state'])
                           position = -1
                           data['trade'] = -1
                           message = "*BB*SELL BTC*** @" + str(data.iloc[-1])
                           telegram='https://api.telegram.org/bot618565857:AAH-3mWGnl2jgMFw4vPML5T1XmY6Ikx9AmU/sendMessage'
                           tparam = { "chat_id":"@ArbInfo","text":message}
                           response = requests.request("GET", telegram, params=tparam)
                           
                   else:
                       time.sleep(0)
                              
                   if len(data) % 100 == 0:
                       data.to_csv('BB_STD_data.csv')
                       tick.to_csv('BB_tick_data.csv')
                   if len(data) > 5000 :
                       print('******* END OF Fetch ********')
                       deregister(websocket)

def main():
    asyncio.get_event_loop().run_until_complete(call_api())

main()
