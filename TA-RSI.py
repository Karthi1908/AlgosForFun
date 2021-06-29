# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 11:10:49 2020

@author: karth
"""

import numpy as np
import pandas as pd
import pandas_datareader.data as web
from datetime import date, timedelta
import quandl 
#quandl.ApiConfig.api_key = 'HTNov29YHShyqrm1R7sZ'

end=date.today()
start=end - timedelta(days= 5*365)

#close = web.DataReader('GDAX/BTC_USD','quandl',start,end,access_key ='HTNov29YHShyqrm1R7sZ')
BTC = quandl.get('GDAX/BTC_USD',start_date = start, end_date = end)
print(BTC.head(10)) 
BTC['Close'] = BTC['Open'].shift(-1)
print(BTC.head(10)) 

BTC['MA'] = np.round(BTC['Close'].rolling(window=20,center=False).mean(),2)
BTC['Std_dev'] = np.round(BTC['Close'].rolling(window=20,center=False).std(),4)
print(BTC.tail(10))

BTC['UP_Band'] = BTC['MA'] + 3 * BTC['Std_dev']
BTC['LOW_Band'] = BTC['MA'] - 3 * BTC['Std_dev']

_= BTC[['Close','MA','UP_Band','LOW_Band']].plot(grid=True,figsize=(20,16))