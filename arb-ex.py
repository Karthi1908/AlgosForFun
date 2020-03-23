# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 20:37:00 2020

@author: karth
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 21:40:27 2020

@author: karth
"""

import requests
import time
import logging
import os

name ='status.log'
cwd = os.getcwd()
path = cwd +'/' + name 

print(path)

fh = logging.FileHandler(path)
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger = logging.getLogger('Logger')
logger.setLevel(logging.INFO)
logger.addHandler(fh)


i=0


def main() :
    exchange = []
    bid = []
    ask = []
    logger.info("----------------------")
    
    #Bittrex
    resp = requests.get('https://api.bittrex.com/api/v1.1/public/getorderbook?market=BTC-ETH&type=both')
    if resp.ok:
        exchange.append('Bittrex')
        bid.append(resp.json()['result']['buy'][0]['Rate'])
        ask.append(resp.json()['result']['sell'][0]['Rate'])
        logger.info("%s - Bid:%f Ask:%f" , exchange[-1],bid[-1],ask[-1])
    #print(exchange[0],bid[0],ask[0])
  
    #Binance 
    resp1 = requests.get('https://api.binance.com/api/v3/depth?symbol=ETHBTC&limit=5')
    if(resp1.ok):
        exchange.append('Binance')
        bid.append(float(resp1.json()['bids'][0][0]))
        ask.append(float(resp1.json()['asks'][0][0]))
        logger.info("%s - Bid:%f Ask:%f" , exchange[-1],bid[-1],ask[-1])
    #print(exchange[1],bid[1],ask[1])
    
    #crypto
    resp2 = requests.get('https://api.crypto.com/v1/depth?symbol=ethbtc&type=step0')
    if(resp.ok) :
        exchange.append('Crypto')
        bid.append(float(resp2.json()['data']['tick']['bids'][0][0]))
        ask.append(float(resp2.json()['data']['tick']['asks'][0][0]))
        logger.info("%s - Bid:%f Ask:%f" , exchange[-1],bid[-1],ask[-1])
    #print(exchange[2],bid[2],ask[2])
    
    #HitBTC 
    resp3 = requests.get('https://api.hitbtc.com/api/2/public/orderbook/ETHBTC?limit=100')
    if(resp3.ok) :
    #print(resp3.json()['bid'][0]['price'],resp3.json()['ask'][0]['price'])
        exchange.append('HitBtc')
        bid.append(float(resp3.json()['bid'][0]['price']))
        ask.append(float(resp3.json()['ask'][0]['price']))
        logger.info("%s - Bid:%f Ask:%f" , exchange[-1],bid[-1],ask[-1])
   
    #Upbit
    url = 'https://sg-api.upbit.com/v1/orderbook'
    querystring = {"markets":"BTC-ETH"}
    response = requests.request("GET", url, params=querystring)
    if(response.ok) :
        exchange.append('Upbit')
        bid.append(response.json()[0]['orderbook_units'][0]['bid_price'])
        ask.append(response.json()[0]['orderbook_units'][0]['ask_price'])
        logger.info("%s - Bid:%f Ask:%f" , exchange[-1],bid[-1],ask[-1])
    #print(exchange[3],bid[3],ask[3])

    logger.info("----------------------")
    
    max_bid = max(bid)
    max_bid_exch = exchange[bid.index(max(bid))]
    min_ask =min(ask)
    min_ask_exch = exchange[ask.index(min(ask))]
    #print(max_bid,max_bid_exch)
    #print(min_ask,min_ask_exch)
    #print("%s : %f || %f : %s",max_bid_exch,max_bid,min_ask,min_ask_exch)
    logger.info("%s : %f || %f : %s",max_bid_exch,max_bid,min_ask,min_ask_exch)
    logger.info("----------------------")

    if((max_bid / 1.0025) > (min_ask * 1.0025) ):
        profit_pc = round((max_bid - min_ask) / (max_bid + min_ask) * 100, 6)
        logger.info('Sell in %s and Buy in %s and Profit is %f',max_bid_exch,min_ask_exch,profit_pc)
        logger.info("-------------------")
        profit_pc = (max_bid - min_ask) / (max_bid + min_ask) * 100
        message = "Sell in " + max_bid_exch + " Buy in " + min_ask_exch + 'Profit %' + str(profit_pc)
        #print(message)
        telegram='https://api.telegram.org/bot949842434:AAHkHI4PkzFJ6ZGbAFp9tKmBg-2wyUbsU1k/sendMessage'
        tparam = { "chat_id":"@ArbInfo","text": message}
        response = requests.request("GET", telegram, params=tparam)
        print(response.json()['result']['text'])
        time.sleep(5)
    else:
        logger.info("No Arb opportunity")
        time.sleep(5)
        logger.info("-------------------")
        print(i)
        if i%100 == 0 :
            telegram='https://api.telegram.org/bot949842434:AAHkHI4PkzFJ6ZGbAFp9tKmBg-2wyUbsU1k/sendMessage?chat_id=@ArbInfo&text=No%20Arb%20Opportunity'
            response = requests.get(telegram)
            print(response.json()['result']['text'])

while i < 4000:
    main()
    i=i+1
