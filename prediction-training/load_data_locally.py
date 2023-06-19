import configparser

import mysql.connector
import pickle
import pandas as pd
from tqdm.auto import tqdm
import os



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
        if os.path.exists(DATA_DIR + f"{stationId[0]}.pickle"):
            pass
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
ORDER BY bd.timeId
"""
        mydb_cursor.execute(querry)
        data = mydb_cursor.fetchall()
        #make dataframe
        df = pd.DataFrame(data, columns=["latitude", "longitude", "stationId", "timeID", "nrBikes", "temp", "feelsLikeTemp", "description", "cloud", "wind", "gust", "event type"])
        #save as pickle
        with open(DATA_DIR+f"{stationId[0]}.pickle", "wb") as file:
            pickle.dump(df, file)



load_data()
