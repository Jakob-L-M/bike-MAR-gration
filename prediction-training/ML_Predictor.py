import configparser

import mysql.connector
import pickle
import pandas as pd
import tensorflow as tf
from tqdm.auto import tqdm
import os


#Model architecture: 15*15*24
#input Layer: 15 nodes:
# 1 : latitude (normalised)
# 2 : longitude (normalised)
# 3 : number of bikes at station t = 0
# 4 : number of bikes at station t = -6
# 5 : number of bikes at station t = -15
# 6 : number of bikes at station t = -30
# 7 : number of bikes at station t = -120
# 9 : weather temp
# 10 : weather feelsLikeTemp
# 11 : weather description (parsed & normalised)
# 12 : weather cloud
# 13 : weather wind
# 14 : weather gust
# 15, 16, 17 : weekday as 3-bit binary
# 18 : isHoliday
# 19, 20 : timeX, timeY , coordinates on 24h clock


#build model using tensorflow
def build_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(15, activation='relu', input_shape=[15]),
        tf.keras.layers.Dense(15, activation='relu'),
        tf.keras.layers.Dense(24)
    ])

    optimizer = tf.keras.optimizers.RMSprop(0.001)

    model.compile(loss='mse',
                optimizer=optimizer,
                metrics=['mae', 'mse'])
    return model

#load data from sql to file
def load_data():
    DATA_DIR = "C:\\Users\\belas\\OneDrive\\Documents\\UNI\\Semester 4\\Datenintegration\\bike-Mar-gration\\data\\bikes_at_station\\"

    #create sql connection
    config = configparser.ConfigParser()
    config.read(r"C:\Users\belas\OneDrive\Documents\UNI\Semester 4\Datenintegration\bike-Mar-gration\.env")
    mydbConfig = config["mysql"]
    mydb = mysql.connector.connect(
        host=mydbConfig["MYSQL_HOST"],
        user=mydbConfig["MYSQL_USER"],
        password=mydbConfig["MYSQL_PASSWORD"],
        database=mydbConfig["MYSQL_DATABASE"]
    )
    mydb_cursor = mydb.cursor()

    #get stations
    querry = """SELECT s.id 
                FROM stations s """
    mydb_cursor.execute(querry)
    stations = mydb_cursor.fetchall()


    #load data

    for (stationId) in tqdm(stations):
        if os.path.exists(DATA_DIR + f"{stationId}.pickle"):
            continue
        querry = f"""
SELECT s.latitude, s.longitude, bd.stationId, bd.timeID, bd.nrBikes, w.temp, w.feelsLikeTemp, w.description, w.cloud, w.wind, w.gust, e.`group` 
FROM (
	SELECT b.stationId  AS stationId, b.timeId AS timeId, count(b.id) AS nrBikes
	FROM bikes b
	WHERE b.stationId = {stationId[0]} 
	GROUP BY b.timeId) AS bd
JOIN stations s ON s.id = bd.stationId
JOIN cities c ON c.id = s.cityId 
LEFT OUTER JOIN events e ON TO_DAYS(e.`date`) = TO_DAYS(FROM_UNIXTIME(bd.timeId*180))  
JOIN weather w ON w.cityId = s.cityId AND bd.timeId = w.timeId
"""
        mydb_cursor.execute(querry)
        data = mydb_cursor.fetchall()
        #make dataframe
        df = pd.DataFrame(data, columns=["latitude", "longitude", "stationId", "timeID", "nrBikes", "temp", "feelsLikeTemp", "description", "cloud", "wind", "gust", "event type"])
        #save as pickle
        with open(DATA_DIR+f"{stationId[0]}.pickle", "wb") as file:
            pickle.dump(df, file)



load_data()
