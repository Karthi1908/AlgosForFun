# -*- coding: utf-8 -*-
"""
Created on Fri May  8 00:23:28 2020
Pair trading of EOS and LTC
@author: karth
"""

import pandas as pd
import pandas_datareader.data as web
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller,coint
import matplotlib.pyplot as plt
from datetime import datetime , timedelta

def main():
    
    INS = pd.DataFrame()
    end_dt = datetime.today()
    start_dt = end_dt - timedelta(days = 1.2 * 365)
    
    INS['LTC'] = web.DataReader('LTC-USD','yahoo',start_dt,end_dt)['Close']
    INS['EOS'] = web.DataReader('EOS-USD','yahoo',start_dt,end_dt)['Close']
    print(INS.head())
    
    HR = get_hedge_ratio(INS)
    print('Hedge_Ratio:',HR)
    
    INS['Spread'] = INS['EOS'] - HR * INS['LTC']
    check_stationarity(INS['Spread'])
    INS = mean_reversion_strategy(INS,10,2)
    trade_stats(INS)
    
def get_hedge_ratio(df):
    
    plt.scatter(df.EOS,df.LTC)
    plt.xlabel('LTC')
    plt.ylabel('EOS')
    plt.show()
    
    IV = df.LTC
    DV = df.EOS
    model = sm.OLS(DV,IV).fit()
    return model.params[0]
    
def check_stationarity(x):
    adf =adfuller(x,maxlag=1)
    print(adf[0])
    print(adf[4])
    #x.plot(figsize=(10,7))
    
def mean_reversion_strategy(df,ma,std):
    
   
    df['MA'] = np.round(df['Spread'].rolling(window = ma, center=False).mean(),2)
    df['Std'] = np.round(df['Spread'].rolling(window =ma, center=False).std(),2)
    
    df['UP_Band'] = df['MA'] + std * df['Std']
    df['LO_Band'] = df['MA'] - std * df['Std']
    
    df['Long_Entry'] = df['Spread'] > df['LO_Band']
    df['Long_Exit']  = df['Spread'] > df['MA']
    
    df['Long Positions'] = np.nan
    df.loc[df['Long_Entry'] ,'Long Positions' ] = 1
    df.loc[df['Long_Exit'], 'Long Positions'] = 0
    df['Long Positions'].fillna(method='ffill', inplace =True)
    
    df['Short_Entry'] = df['Spread'] < df['UP_Band']
    df['Short_Exit']  = df['Spread'] < df['MA']
    
    df['Short Positions'] = np.nan
    df.loc[df['Short_Entry'] ,'Short Positions' ] = -1
    df.loc[df['Short_Exit'], 'Short Positions'] = 0
    df['Short Positions'].fillna(method = 'ffill', inplace = True)
    
    df['positions'] = df['Long Positions'] + df['Short Positions']
    
    return df
    
    
    print(df[['Long_Entry','Long_Exit','Long Positions']].head(20))
    
def trade_stats(df):
    df['Pct_Change'] = (df['Spread'] - df['Spread'].shift(1)) / ( df['LTC'] + df['EOS'])
    df['Strat_ret']  = df['positions'].shift(1) * df['Pct_Change']
    df['cum_ret']    = (df['Strat_ret']+1).cumprod()
    
    df['cum_ret'].plot(figsize=(10,8))
    plt.xlabel('Date')
    plt.ylabel('Cum return')
    plt.show()    
    
main()