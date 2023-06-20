import math
import os
import pickle
import random
from datetime import datetime as dt
from tqdm.auto import tqdm

import numpy as np
from sklearn.model_selection import train_test_split

import pandas as pd
import tensorflow as tf

def findRow(timeID, df, allowedError=0):
    #binary search for timeID
    left = 0
    right = len(df)-1
    while (left < right):
        mid = (left + right) // 2
        if (df["timeID"][mid] == timeID):
            return mid
        elif (df["timeID"][mid] < timeID):
            left = mid + 1
        else:
            right = mid
    if (abs(df["timeID"][left] - timeID) < allowedError):
        return left
    else:
        return -1



#df columns=["latitude", "longitude", "stationId", "timeID", "nrBikes", "temp", "feelsLikeTemp", "description", "cloud", "wind", "gust", "event type"]
def normalise_latitude(lat):
    return (lat - 50.808048)
def normalise_longitude(long):
    return (long - 8.768440)


def decription_to_numeric(description):
    possibilities = [#rain descriptions from data, sort by intensity
        "Sunny",
        "Clear",
        "Partly cloudy",
        "Mist",
        "Cloudy",
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
        "Light snow",
        "Light freezing rain",
        "Light sleet",
        "Moderate rain",
        "Patchy light rain with thunder",
        "Patchy moderate snow",
        "Moderate snow",
        "Patchy heavy snow",
        "Thunder outbreaks possible",
        "Moderate or heavy rain shower",
        "Moderate or heavy snow showers",
        "Heavy rain at times"
        "Moderate or heavy sleet",
        "Heavy snow",
        "Moderate or heavy rain with thunder",
        "Blizzard"
    ]
    if (description in possibilities):
        return possibilities.index(description)/len(possibilities)
    else:
        #raise error, so that new descriptions can be added
        return 0.5


def getWeekday(timeID):
    unix = timeID * 180
    date = dt.fromtimestamp(unix)
    wd = date.weekday()
    #get weekday as 3-bit binary tuple
    return ((wd & 4)>>2, (wd & 2)>>1, wd & 1)


def eventType_to_numeric(eventType):
    if (eventType is None):
        return 0
    else:
        return 1


def getXY(timeID):
    date = dt.fromtimestamp(timeID * 180)
    time = date.time()
    timefloat = (time.hour/24 + time.minute/1440) * 2 * math.pi
    x = math.sin(timefloat)
    y = math.cos(timefloat)
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
def toInputFormat(dataframe, timeID):
    input = []
    row = findRow(timeID, dataframe)

    #latitude
    input.append(normalise_latitude(float(dataframe["latitude"][row])))
    #longitude
    input.append(normalise_longitude(float(dataframe["longitude"][row])))
    #number of bikes at station t = 0
    input.append(dataframe["nrBikes"][row])
    #row for t = -6
    row6 = findRow(timeID - 2, dataframe)
    #row for t = -15
    row15 = findRow(timeID - 5, dataframe)
    #row for t = -30
    row30 = findRow(timeID - 10, dataframe)
    #row for t = -120
    row120 = findRow(timeID - 40, dataframe)
    #check if rows exist
    if (row6 == -1 or row15 == -1 or row30 == -1 or row120 == -1):
        return None
    #number of bikes at station t = -6
    input.append(dataframe["nrBikes"][row6])
    #number of bikes at station t = -15
    input.append(dataframe["nrBikes"][row15])
    #number of bikes at station t = -30
    input.append(dataframe["nrBikes"][row30])
    #number of bikes at station t = -120
    input.append(dataframe["nrBikes"][row120])
    #weather temp
    input.append(dataframe["temp"][row])
    #weather feelsLikeTemp
    input.append(dataframe["feelsLikeTemp"][row])
    #weather description (parsed & normalised)
    input.append(decription_to_numeric(dataframe["description"][row]))
    #weather cloud
    input.append(dataframe["cloud"][row])
    #weather wind
    input.append(dataframe["wind"][row])
    #weather gust
    input.append(dataframe["gust"][row])
    #weekday as 3-bit binary
    weekday = getWeekday(dataframe["timeID"][row])
    input.append(weekday[0])
    input.append(weekday[1])
    input.append(weekday[2])
    #isHoliday
    input.append(eventType_to_numeric(dataframe["event type"][row]))
    #timeX, timeY , coordinates on 24h clock
    timexy = getXY(dataframe["timeID"][row])
    input.append(timexy[0])
    input.append(timexy[1])

    return np.array(input)

def toOutputFormat(dataframe, timeID):
    row15 = findRow(timeID+5, dataframe)
    row30 = findRow(timeID+10, dataframe)
    row45 = findRow(timeID+15, dataframe)
    row60 = findRow(timeID+20, dataframe)
    if (row15 == -1 or row30 == -1 or row45 == -1 or row60 == -1):
        return None
    else:
        return np.array([dataframe["nrBikes"][row15], dataframe["nrBikes"][row30], dataframe["nrBikes"][row45], dataframe["nrBikes"][row60]])


def readData():
    path_to_data = r"C:/Users/belas/OneDrive/Documents/UNI/Semester 4/Datenintegration/bike-Mar-gration/data/bikes_at_station/"
    dataframes = []
    for file in tqdm(os.listdir(path_to_data)):
        if file.endswith(".pickle"):
            df = pd.read_pickle(path_to_data + file)
            dataframes.append(df)
    return dataframes


#build model using tensorflow
def build_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(19, activation='relu', input_shape=[19]),
        tf.keras.layers.Dense(15, activation='relu'),
        tf.keras.layers.Dense(4) #output: t+15,t+30,t+45,t+60
    ])

    optimizer = tf.keras.optimizers.RMSprop(0.001)

    model.compile(loss='mse',
                optimizer=optimizer,
                metrics=['mae', 'mse'])
    return model

def build_train_test_data():
    print("reading data to dataframes...")
    dataframes = readData()
    train_test_data = []
    print("\nconstructing train and test data...")
    for index, df in enumerate(dataframes):
        print("\nstarted Dataframe "+str(index+1)+" of "+str(len(dataframes)))
        for timeID in tqdm(df["timeID"]):
            output = toOutputFormat(df, timeID)
            if (output is None):
                continue
            input = toInputFormat(df, timeID)
            if (input is None):
                continue
            train_test_data.append((input, output))
    print("splitting train and test data...")
    random.shuffle(train_test_data)
    #train test split
    train_data, test_data = train_test_split(train_test_data, test_size=0.2)
    #split into input and output
    train_data_x = []
    train_data_y = []
    for data in train_data:
        train_data_x.append(data[0])
        train_data_y.append(data[1])
    test_data_x = []
    test_data_y = []
    for data in test_data:
        test_data_x.append(data[0])
        test_data_y.append(data[1])

    #save to file with pickle
    path_to_train_test_data = r"C:/Users/belas/OneDrive/Documents/UNI/Semester 4/Datenintegration/bike-Mar-gration/data/train_test_data/"
    print("saving train and test data...")
    with open(path_to_train_test_data+"train_data_x.pickle", "wb") as f:
        pickle.dump(train_data_x, f)
    with open(path_to_train_test_data+"train_data_y.pickle", "wb") as f:
        pickle.dump(train_data_y, f)
    with open(path_to_train_test_data+"test_data_x.pickle", "wb") as f:
        pickle.dump(test_data_x, f)
    with open(path_to_train_test_data+"test_data_y.pickle", "wb") as f:
        pickle.dump(test_data_y, f)
    print("data build & save complete")
    return True


def load_train_test_data():
    path_to_train_test_data = r"C:/Users/belas/OneDrive/Documents/UNI/Semester 4/Datenintegration/bike-Mar-gration/data/train_test_data/"
    with open(path_to_train_test_data+"train_data_x.pickle", "rb") as f:
        train_X = pickle.load(f)
    with open(path_to_train_test_data+"train_data_y.pickle", "rb") as f:
        train_Y = pickle.load(f)
    with open(path_to_train_test_data+"test_data_x.pickle", "rb") as f:
        test_X = pickle.load(f)
    with open(path_to_train_test_data+"test_data_y.pickle", "rb") as f:
        test_Y = pickle.load(f)
    #return train_X, train_Y, test_X, test_Y
    return np.array(train_X, dtype=np.float32), np.array(train_Y, dtype=np.float32), np.array(test_X, dtype=np.float32), np.array(test_Y, dtype=np.float32)

def init_and_save_model():
    model = build_model()
    model.save("models/model01.h5")

def load_model_and_train():
    print("Loading model...")
    model_name = "model01.h5"
    model = tf.keras.models.load_model("models/"+model_name)
    print("loading data...")
    train_data_x, train_data_y, test_data_x, test_data_y = load_train_test_data()
    #train model
    print("Training model...")
    model.fit(train_data_x, train_data_y, epochs=10)
    #test model
    print("Testing model...")
    test_loss, test_mae, test_mse = model.evaluate(test_data_x, test_data_y, verbose=2)
    print("Test loss: " + str(test_loss))
    print("Test MAE: " + str(test_mae))
    print("Test MSE: " + str(test_mse))
    #save model
    print("Saving model...")
    model.save("models/model01.h5")

def calc_baseline():
    print("loading data...")
    train_data_x, train_data_y, test_data_x, test_data_y = load_train_test_data()0,,


    #predict same value as t
    print("Calculating baseline...")
    MSE = 0
    for i in range(len(test_data_x)):
        for j in range(len(test_data_y[0])):
            MSE += (test_data_x[i][2] - test_data_y[i][j])**2

    MSE = MSE / len(test_data_x)

    print("Baseline MSE: " + str(MSE))

calc_baseline()
