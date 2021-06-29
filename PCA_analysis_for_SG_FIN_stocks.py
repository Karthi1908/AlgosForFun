# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 22:55:21 2021
Original code available  rodler/quantinsti_statarb
Modified for SG stocks for self learning.
@author: karth
"""


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import datetime
from statsmodels.tsa.stattools import coint
from scipy import stats as stats
from sklearn.linear_model import LinearRegression
from sklearn.decomposition import PCA
import scipy
import statsmodels.api as sm
import pandas_datareader.data as web

end_dt = datetime.date.today()
print(end_dt)


start_dt = end_dt - datetime.timedelta(days = 5 * 365 )
print(start_dt)


DBS = web.DataReader('D05.SI','yahoo',start_dt,end_dt)
print(DBS.tail(10))



UOB = web.DataReader('U11.SI','yahoo',start_dt,end_dt)
print(UOB.tail(10))


OCBC = web.DataReader('O39.SI','yahoo',start_dt,end_dt)
print(OCBC.tail(10))

HLSG = web.DataReader('S41.SI','yahoo',start_dt,end_dt)
print(HLSG.tail(10))

#cointegration = coint(DBS['Close'], UOB['Close'])
#print(cointegration)

#correlation = np.corrcoef(DBS['Close'], UOB['Close'])
#print(correlation)


prices = pd.DataFrame()
prices['DBS']  = DBS['Close']
prices['UOB']  = UOB['Close']
prices['OCBC'] = OCBC['Close']
prices['HLSG'] = HLSG['Close']
print(prices.tail(10))



def backtest(prices,max_pos=1,num_factors=1,initial_cash=1e6,lkbk=500):
    pr = np.asarray(prices.T)
    print(pr.shape)
    entry = {}
    pnls = []
    dates = []
    resids = run_pca(pr,num_factors)
    
    if max_pos > pr.shape[0]/2:
        print('max_pos too large!')
        #return

    for i,pri in enumerate(pr.T):

        if i < 60: continue
 
        resids, factors = run_pca(pr[:,max(0,i-lkbk):i],num_factors,log_prices=True)
        zs = {}
        for inst in range(len(pri)):
            #zs[inst] = Zscore(resids[inst])[i]
            zs[inst] = Zscore(resids[inst])[-1]

        idx_long = (np.argsort([zs[j] for j in zs])[:max_pos])
        idx_short = (np.argsort([zs[j] for j in zs])[-max_pos:])
        
        pnl = 0
        for j,idx in enumerate(entry):
            wgt = np.round((initial_cash/len(pri))/entry[idx])
            #pnl += ((pri[idx]-np.abs(entry[idx]))/np.abs(entry[idx]))*wgt/initial_cash
            pnl += ((pri[idx]-np.abs(entry[idx])))*wgt
            #print pnl
        pnls.append(pnl)
        dates.append(prices.index[i])
            
        entry = {}
        

        print(idx_long, idx_short)
        for idx in idx_long:
            entry[idx] = pri[idx]
        for idx in idx_short:
            entry[idx] = -pri[idx]
        print(i,entry)
        
        #print(i,sum(pnls))
    return pnls,dates


def Zscore(X):
    return np.array((X - np.mean(X)) / np.std(X))

def run_pca(pr,components=1,log_prices=True):
    pca = PCA(n_components=components)
    if log_prices:
        comps = pca.fit(np.log(pr.T)).components_.T
    else:
        comps = pca.fit(pr.T).components_.T
    factors = sm.add_constant(pr.T.dot(comps))
    mm = [sm.OLS(s.T, factors).fit() for s in pr]
    resids = list(map(lambda x: x.resid, mm))
    return resids, factors


pnls,dates = backtest(prices,max_pos=2,num_factors=2,initial_cash=1e6,lkbk=400)

plt.plot(np.cumsum(pnls));
