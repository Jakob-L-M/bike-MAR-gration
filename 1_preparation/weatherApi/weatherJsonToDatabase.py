from datetime import datetime
import json
import mysql.connector

#generate sql insert string from data
def getSqlinsert(timeId, cityId, temp, feelsLikeTemp, isDay, description, cloud, wind, gust):
    sqlinsert = f"INSERT INTO weather (timeId, cityId, temp, feelsLikeTemp, isDay, description, cloud, wind, gust) VALUES ({timeId}, {cityId}, {temp}, {feelsLikeTemp}, {isDay}, '{description}', {cloud}, {wind}, {gust});\n"
    return sqlinsert

def getTimeId(time_in_milliseconds):
    time_in_milliseconds /= 1000*180
    return int(time_in_milliseconds)

def getFileName(date):
    return f"{date.year}-{date.month}-{date.day}.json"


json_folder = r"C:/bike-mar-gration-weatherdata/"

firstDate = datetime(2022, 7, 18)
lastDate = datetime(2023, 5, 7)


mysql.co

#loop through all days from firstDate to lastDate
while firstDate <= lastDate:
    with open(json_folder + getFileName(firstDate), "r") as f:
        data = json.load(f)
        hourhistory = data["forecast"]["forecastday"][0]["hour"]
        for hourindex in range(len(hourhistory)-1):

