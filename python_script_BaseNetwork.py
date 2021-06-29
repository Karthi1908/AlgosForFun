import pandas as pd
from collections import deque
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM, BatchNormalization
from sklearn.preprocessing import StandardScaler
import keras.backend as K
from statistics import mean 
import matplotlib.pyplot as plt

def classify_return(future):
    if float(future) > 0:  
        return 1.0
    else:
        return 0.0

def threshold_longshort(predict):
    if float(predict)>0.5: 
        return 1.0
    else:  
        return -1.0
   
def recall(y_true, y_pred): #Sensitivity
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    all_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (all_positives + K.epsilon())
    return recall

def precision(y_true, y_pred): #ppv
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision
   
def f1score(y_true,y_pred):
    return 2*recall(y_true, y_pred)*precision(y_true, y_pred)/(precision(y_true, y_pred)+recall(y_true, y_pred))


historical_period = 90 
future_period = 3 
input_tickers = ["SPY","TLT"] 
             
train_df = pd.DataFrame() 

for ticker in input_tickers:  

    ticker = ticker.split('.csv')[0] 
    dataset = f'{ticker}.csv'  
    df = pd.read_csv(dataset)    
    
    df.rename(columns={"Adj Close": f"{ticker}_close", "Volume": f"{ticker}_volume"}, inplace=True)

    df.set_index("Date", inplace=True)  
    df = df[[f"{ticker}_close", f"{ticker}_volume"]]  

    if len(train_df)==0:
        train_df = df
    else:  
        train_df = train_df.join(df)                                
   
train_df['future'] = train_df['SPY_close'].pct_change()

for k in range(future_period):
    if k==0:
        temp_series = train_df['future'].shift(-1)
    else:
        temp_series+=train_df['future'].shift(-k-1)         
train_df['future']=temp_series/future_period                                          

train_df['target'] = list(map(classify_return, train_df['future']))

train_df = train_df.drop("future", 1)  
train_df['SPY_true_return'] = train_df['SPY_close'].pct_change().shift(-1)

#Select last 10% for validation
last_valdata = sorted(train_df.index.values)[-int(0.10*len(train_df.index.values))]

validation_df = train_df[(train_df.index >= last_valdata)]
train_df = train_df[(train_df.index < last_valdata)]                             

for ticker in input_tickers:  # begin iteration
    train_df[f"{ticker}_close"]=train_df[f"{ticker}_close"].pct_change()
    validation_df[f"{ticker}_close"]=validation_df[f"{ticker}_close"].pct_change()
    train_df[f"{ticker}_volume"]=train_df[f"{ticker}_volume"].pct_change()
    validation_df[f"{ticker}_volume"]=validation_df[f"{ticker}_volume"].pct_change()                                              

train_df.dropna(inplace=True)
validation_df.dropna(inplace=True)

col_names=[]
for ticker in input_tickers:  
    col_names.append(f"{ticker}_close")
    col_names.append(f"{ticker}_volume")

scaler = StandardScaler()
train_df[col_names]=scaler.fit_transform(train_df[col_names]) 
validation_df[col_names]=scaler.transform(validation_df[col_names])                            

train_x = []
train_y = []
validation_x = []
validation_y = []
val_y_true=[]
                              
#Create Training Data
data = [] 
hist_days = deque(maxlen=historical_period)  

for i in train_df.values:  
    hist_days.append([n for n in i[:-2]])  
    if len(hist_days) == historical_period:  
        data.append([np.array(hist_days), i[-2]]) 

for inputs, target in data: 
    train_x.append(inputs)  
    train_y.append(target)
    
train_x=np.array(train_x)

#Create validation Data
data = [] 
hist_days = deque(maxlen=historical_period)  

for i in validation_df.values:  
    hist_days.append([n for n in i[:-2]])  
    if len(hist_days) == historical_period:  
        data.append([np.array(hist_days), i[-2], i[-1]])  

for inputs, target,var_to_predict in data: 
    validation_x.append(inputs)  
    validation_y.append(target)
    val_y_true.append(var_to_predict)        
    
validation_x=np.array(validation_x)

#Build base model
model = Sequential()
model.add(LSTM(32, input_shape=(train_x.shape[1:]), return_sequences=True))
model.add(Dropout(0.2))
model.add(BatchNormalization())                                                    

model.add(LSTM(32))
model.add(Dropout(0.2))
model.add(BatchNormalization())                                                                                 

model.add(Dense(32, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(1, activation='sigmoid'))        

model.compile(loss='binary_crossentropy', optimizer=tf.keras.optimizers.Adam(decay=1e-6), metrics=[precision, recall,f1score]) 
 
# Train model
model.fit(train_x, train_y,batch_size=128,epochs=50,validation_data=(validation_x, validation_y))

y_pred_val=list(map(threshold_longshort, model.predict(validation_x)))    
returns=[]

for i in range(len(val_y_true)):
    if i==0:
        returns.append(0)
    else:
        returns.append(val_y_true[i]*y_pred_val[i-1])

equity_bm=10000*np.cumprod(1+np.array(val_y_true))
equity_stgy=10000*np.cumprod(1+np.array(returns))                                            
   
ann_return_stgy = 252*np.array(returns).mean()
ann_return_bm = 252*np.array(val_y_true).mean()

sharpe_ratio_stgy=np.sqrt(252)*np.array(returns).mean()/np.array(returns).std()
sharpe_ratio_bm=np.sqrt(252)*np.array(val_y_true).mean()/np.array(val_y_true).std()

win_ratio_bm=len((np.where(np.array(val_y_true)>0))[0]) / len(val_y_true)
win_ratio_stgy=len((np.where(np.array(returns)>0))[0]) / len(returns)

pl_ratio_bm=-mean([i for i in val_y_true if i >= 0]) / mean([i for i in val_y_true if i < 0])
pl_ratio_stgy=-mean([i for i in returns if i >= 0]) / mean([i for i in returns if i < 0])

Roll_Max = pd.Series(equity_bm).rolling(window=2*252, min_periods=1).max()
DD_bm = (pd.Series(equity_bm)/Roll_Max-1).min()

Roll_Max = pd.Series(equity_stgy).rolling(window=2*252, min_periods=1).max()
DD_stgy = (pd.Series(equity_stgy)/Roll_Max-1).min()                                       

#print ('Equity($) Benchmark vs Strategy')
#print (equity_bm, equity_stgy)

fig, ax = plt.subplots()
ax.plot(equity_bm,label='Benchmark')
ax.plot(equity_stgy,label='Strategy')
ax.legend(loc='upper left', shadow=True, fontsize='x-large')
plt.xlabel('#Days')
plt.ylabel('Equity($)')                                         
plt.show()
                                        
print ('Annual Return% Benchmark vs Strategy')
print (100*ann_return_bm, 100*ann_return_stgy)

print ('\n')
print ('Sharpe Ratio Benchmark vs Strategy')
print ([sharpe_ratio_bm, sharpe_ratio_stgy])

print ('\n')
print ('%Winners Benchmark vs Strategy')
print ([100*win_ratio_bm, 100*win_ratio_stgy])

print ('\n')
print ('Win/Loss Ratio Benchmark vs Strategy')
print ([pl_ratio_bm, pl_ratio_stgy])

print ('\n')
print ('Max Drawdown(%) Benchmark vs Strategy')
print ([100*DD_bm, 100*DD_stgy])