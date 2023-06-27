import math
import os
import random
from datetime import datetime as dt

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

import pandas as pd
import tensorflow as tf

from load_data_locally import get_data

DATA_DIR = '../data/bikes_at_station/'
MODEL_DIR = './models/'

def description_to_numeric(description):
    possibilities = [#rain descriptions from data, sort by intensity
        "Sunny",
        "Clear",
        "Partly cloudy",
        "Mist",
        "Cloudy",
        "Overcast",
        "Fog",
        "Patchy light drizzle",
        "Patchy rain possible",
        "Patchy light rain",
        "Light rain shower",
        "Light drizzle",
        "Light rain",
        "Freezing fog",
        "Moderate rain at times",
        "Patchy snow possible",
        "Patchy light snow",
        "Patchy sleet possible",
        "Light snow showers",
        "Light sleet showers",
        "Light snow",
        "Light freezing rain",
        "Light sleet",
        "Moderate rain",
        "Patchy light rain with thunder",
        "Patchy moderate snow",
        "Moderate snow",
        "Patchy heavy snow",
        "Thundery outbreaks possible",
        "Thunder outbreaks possible",
        "Moderate or heavy rain shower",
        "Moderate or heavy snow showers",
        "Heavy rain at times",
        "Moderate or heavy sleet",
        "Heavy snow",
        "Moderate or heavy rain with thunder",
        "Blizzard"
    ]
    check_set = set(possibilities)
    if description in check_set:
        return possibilities.index(description)/len(possibilities)
    else:
        #raise error, so that new descriptions can be added
        print(description, description in check_set, possibilities.index(description))
        raise ValueError('unknown weather')
        return 0.5


def getWeekday(timeID):
    unix = timeID * 180
    date = dt.fromtimestamp(unix)
    wd = date.weekday()
    #get weekday as 3-bit binary tuple
    return [(wd & 4)>>2, (wd & 2)>>1, wd & 1]


def eventType_to_numeric(eventType):
    if eventType is None:
        return 0
    else:
        return 1


def getXY(timeID):
    date = dt.fromtimestamp(timeID * 180)
    time = date.time()
    time_float = (time.hour/24 + time.minute/1440) * 2 * math.pi
    x = math.sin(time_float)
    y = math.cos(time_float)
    return (x, y)

#Model architecture: 15*15*24
#input Layer: 15 nodes:
# 1 : latitude (normalised)
# 2 : longitude (normalised)
# 3 : number of bikes at station t = 0
# 4 : number of bikes at station t = -6
# 5 : number of bikes at station t = -15
# 6 : number of bikes at station t = -30
# 7 : number of bikes at station t = -120
# 8 : weather temp
# 9 : weather feelsLikeTemp
# 10 : weather description (parsed & normalised)
# 11 : weather cloud
# 12 : weather wind
# 13 : weather gust
# 14, 15, 16 : weekday as 3-bit binary
# 17 : isHoliday
# 18, 19 : timeX, timeY , coordinates on 24h clock
def transform_input(df: pd.DataFrame):

    print('Transforming input data...', end='', sep='', flush=True)

    # latitude
    # df['lat'] = min_max_norm(df['latitude'].values)
    df['lat'] = df['latitude'].apply(lambda x: float(x) + 0.001*random.random() - 0.001)

    # longitude
    # df['long'] = min_max_norm(df['longitude'].values)
    df['long'] = df['longitude'].apply(lambda x: float(x) + 0.001*random.random() - 0.001)

    
    # weather description (parsed & normalised)
    df['desc_numeric'] = df['description'].apply(lambda x: description_to_numeric(x))
    
    # 3 bit weekday array
    df['weekday_0'], df['weekday_1'], df['weekday_2'] = np.array(list(df['timeId'].apply(lambda x: getWeekday(x)).values)).T

    #isHoliday
    df['event_type'] = df['event_type'].apply(lambda x: eventType_to_numeric(x))
    
    #timeX, timeY , coordinates on 24h clock
    df['timeX'], df['timeY'] = np.array(list(df['timeId'].apply(lambda x: getXY(x)).values)).T

    print('\b\b\b ✔ ', flush=True)

    return df[[ # X
        'weekday_0', 'weekday_1', 'weekday_2', 'timeX',
       'timeY', 'lat', 'long', 'temp',
       'feelsLikeTemp', 'desc_numeric', 'cloud', 'wind',
       'gust', 'event_type', 'nBikes', 't-6', 
       't-15', 't-30', 't-60', 't-120'
       ]], df[[ # y
        't+15','t+30', 't+45', 't+60'
       ]], df[['timeId', 'stationId', 'description']]

#build model using TensorFlow
def build_model(name = '', load=True):

    print('Loading model...', end='', sep='', flush=True)

    # if model exists -> load it
    if load and os.path.exists(MODEL_DIR + name):
        model = tf.keras.models.load_model(MODEL_DIR + name)

    else:
        model = tf.keras.Sequential([
            tf.keras.layers.Dense(20, activation='relu', input_shape=[20]),
            tf.keras.layers.Dense(20, activation='relu'),
            tf.keras.layers.Dense(20, activation='relu'),
            tf.keras.layers.Dense(4) #output: t+15,t+30,t+45,t+60
        ])

        model.compile(loss='mean_squared_logarithmic_error',
                    optimizer=tf.keras.optimizers.Adam(), # using legacy due to M2 Mac
                    metrics=['mse', 'mae'])
    
    print('\b\b\b ✔ ', flush=True)
    return model

def build_train_test_data(test_size=0.1, seed=2023):
    df = get_data()
    X, y, meta = transform_input(df)

    X = np.asarray(X, dtype=np.float32)
    y = np.asarray(y, dtype=np.float32)

    print('Building train and test sets...', end='', sep='', flush=True)

    X_train, X_test, y_train, y_test, meta_train, meta_test = train_test_split(X, y, meta,  test_size=test_size, random_state=seed)

    print('\b\b\b ✔ ', flush=True)

    print('\tData Info:',
          'Size: ' + str(len(df)),
          'Start: ' + str(min(df['timeId'])),
          'End: ' + str(max(df['timeId'])),
          'Seed: ' + str(seed),
          'Test Percent: ' + str(test_size), sep='\n\t')
    
    return X_train, X_test, y_train, y_test, meta_train, meta_test

def load_model_and_train():
    
    name = 'log_loss'
    model = build_model(name, False)
    
    X_train, X_test, y_train, y_test, _, _ = build_train_test_data()
    
    #train model
    print("Training model...")
    model.fit(X_train, y_train, epochs=10, batch_size=512)
    #test model
    print("Testing model...")
    test_loss, test_mse, test_mae = model.evaluate(X_test, y_test, verbose=2)
    print("Test loss: " + str(test_loss))
    print("Test MAE: " + str(test_mae))
    print("Test MSE: " + str(test_mse))
    #save model
    print("Saving model...")
    model.save(MODEL_DIR + name)

if __name__ == '__main__':
    # print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
    load_model_and_train()
