# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 21:40:27 2020
Arbitrage on Prices Difference between Crypto-Exchanges.
CUrrently in testing phase so no actual/sandbox trades placed.
@author: karth
"""

import requests
import time
import logging

name ='status' + str(int(time.time()))+ '.log'
path = 'C:/Users/karth/Desktop/crypto-research/arb_exchanges/log/' + name 

#print(path)

fh = logging.FileHandler(path)
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger = logging.getLogger('Logger')
logger.setLevel(logging.INFO)
logger.addHandler(fh)

server_url = 'https://sg-api.upbit.com'
i=0


while i < 3:
    exchange = []
    bid = []
    ask = []
    
    #Bittrex
    resp = requests.get('https://api.bittrex.com/api/v1.1/public/getorderbook?market=BTC-LTC&type=both')
    exchange.append('Bittrex')
    bid.append(resp.json()['result']['buy'][0]['Rate'])
    ask.append(resp.json()['result']['sell'][0]['Rate'])
    #print(exchange[0],bid[0],ask[0])
  
    #Binance 
    resp1 = requests.get('https://api.binance.com/api/v3/depth?symbol=LTCBTC&limit=5')
    exchange.append('Binance')
    bid.append(float(resp1.json()['bids'][0][0]))
    ask.append(float(resp1.json()['asks'][0][0]))
    #print(exchange[1],bid[1],ask[1])
    
    #HitBTC 
    resp3 = requests.get('https://api.hitbtc.com/api/2/public/orderbook/LTCBTC?limit=100')
    #print(resp3.json())
    #print(resp3.json()['bid'][0]['price'],resp3.json()['ask'][0]['price'])
    exchange.append('HitBtc')
    bid.append(float(resp3.json()['bid'][0]['price']))
    ask.append(float(resp3.json()['ask'][0]['price']))
    
    #crypto
    resp2 = requests.get('https://api.crypto.com/v1/depth?symbol=ltcbtc&type=step0')
    exchange.append('Crypto')
    bid.append(float(resp2.json()['data']['tick']['bids'][0][0]))
    ask.append(float(resp2.json()['data']['tick']['asks'][0][0]))
    #print(exchange[2],bid[2],ask[2])
   
    #Upbit
    url = server_url + "/v1/orderbook"
    querystring = {"markets":"BTC-LTC"}
    response = requests.request("GET", url, params=querystring)
    exchange.append('Upbit')
    bid.append(response.json()[0]['orderbook_units'][0]['bid_price'])
    ask.append(response.json()[0]['orderbook_units'][0]['ask_price'])
    #print(exchange[3],bid[3],ask[3])

    logger.info("----------------------")
    logger.info("%s - Bid:%f Ask:%f" , exchange[0],bid[0],ask[0])
    logger.info("%s - Bid:%f Ask:%f" , exchange[1],bid[1],ask[1])
    logger.info("%s - Bid:%f Ask:%f" , exchange[2],bid[2],ask[2])
    logger.info("%s - Bid:%f Ask:%f" , exchange[3],bid[3],ask[3])
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

    #Consider 45 bps as transaction cost
    if(max_bid > min_ask * 1.0045 ):
        logger.info('Sell in %s and Buy in %s',max_bid_exch,min_ask_exch)
        logger.info("-------------------")
        message = "Sell in " + max_bid_exch + " Buy in " + min_ask_exch
        #print(message)
        telegram='https://api.telegram.org/***APIKEY***k/sendMessage'
        tparam = { "chat_id":"@ArbInfo","text": message}
        response = requests.request("GET", telegram, params=tparam)
        print(response.json()['result']['text'])
        time.sleep(5)
    else:
        logger.info("No Arb opportunity")
        i=i+1
        time.sleep(5)
        logger.info("-------------------")
        if i%100 == 0 :
            telegram='https://api.telegram.org/*****/sendMessage?chat_id=@ArbInfo&text=No%20Arb%20Opportunity'
            response = requests.get(telegram)
            print(response.json()['result']['text'])


