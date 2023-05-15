from datetime import datetime, timedelta
import json
import mysql.connector
import configparser


THREE_MIN_IN_S = 60*3

config = configparser.ConfigParser()
config.read(r"C:\Users\belas\OneDrive\Documents\UNI\Semester 4\Datenintegration\bike-MAR-gration\0_datasets\.env")


#generate sql insert string from data
def getSqlinsert(timeId, cityId, temp, feelsLikeTemp, isDay, description, cloud, wind, gust):
    sqlinsert = f"INSERT INTO weather (timeId, cityId, temp, feelsLikeTemp, isDay, description, cloud, wind, gust) VALUES ({timeId}, {cityId}, {temp}, {feelsLikeTemp}, {isDay}, '{description}', {cloud}, {wind}, {gust});\n"
    return sqlinsert

def getTimeId(time_in_seconds):
    time_in_seconds /= 180
    return int(time_in_seconds)

def getFileName(date):
    return f"{date.year}-{date.month}-{date.day}.json"


json_folder = r"C:/bike-mar-gration-weatherdata/"

firstDate = datetime(2022, 7, 18)

#get sql connection
mydbConfig = config["mysql"]
mydb = mysql.connector.connect(
    host=mydbConfig["MYSQL_HOST"],
    user=mydbConfig["MYSQL_USER"],
    password=mydbConfig["MYSQL_PASSWORD"],
    database=mydbConfig["MYSQL_DATABASE"]
)
mydb_cursor = mydb.cursor()


def interpolate_and_persist(time_in_seconds, timestamp1, timestamp2, mydb_cursor):
    weight1 = abs(time_in_seconds - timestamp2["time_epoch"]) / abs(timestamp1["time_epoch"] - timestamp2["time_epoch"])
    weight2 = 1-weight1
    #calc values
    #temp
    key = "temp_c"
    temp = weight1*timestamp1[key]+weight2*timestamp2[key]

    #feelsliketemp
    key = "feelslike_c"
    feelsliketemp = weight1*timestamp1[key]+weight2*timestamp2[key]

    #isDay
    key = "is_day"
    isDay = round(weight1*timestamp1[key]+weight2*timestamp2[key])

    #description
    key = "condition"
    if (weight1>weight2):
        description = timestamp1[key]["text"]
    else:
        description = timestamp2[key]["text"]

    #cloud
    key = "cloud"
    cloud = weight1*timestamp1[key]+weight2*timestamp2[key]

    #wind
    key = "wind_kph"
    wind = weight1*timestamp1[key]+weight2*timestamp2[key]

    #gust
    key = "gust_kph"
    gust = weight1*timestamp1[key]+weight2*timestamp2[key]

    #cityID (=1)
    cityID = 1

    #timeID
    timeID = getTimeId(time_in_seconds)

    #persist
    InsertQuerry = f"INSERT INTO weather(timeId, cityId, temp, feelsLikeTemp, isDay, description, cloud, wind, gust) " \
                   f"VALUES ({timeID}, {cityID}, {temp}, {feelsliketemp}, {isDay}, {description}, {cloud}, {wind}, {gust})"

    #mydb_cursor.execute(InsertQuerry)


#loop through all days from firstDate to lastDate
f =  open(json_folder + getFileName(firstDate), "r")
data = json.load(f)
hourseries = data["forecast"]["forecastday"][0]["hour"]

pointer_hourseries = 0  # index of timestamp2 in hourseries
timestamp1 = hourseries[pointer_hourseries]
timestamp2 = hourseries[pointer_hourseries]
current_pointer_seconds = timestamp1["time_epoch"]
while(True):
    while(current_pointer_seconds < timestamp2["time_epoch"]):
        interpolate_and_persist(current_pointer_seconds, timestamp1, timestamp2, mydb_cursor)
        current_pointer_seconds += THREE_MIN_IN_S
    timestamp1 = hourseries[pointer_hourseries]
    pointer_hourseries +=1
    if (pointer_hourseries>=len(hourseries)):
        pointer_hourseries = 0
        firstDate += timedelta(days=1)
        #load new weather file
        try:
            f = open(json_folder + getFileName(firstDate), "r")
        except FileExistsError:
            print(f"File for date{getFileName(firstDate)} not found")
            mydb.commit()
            mydb_cursor.close()
            mydb.close()
            break
        data = json.load(f)
        hourseries = data["forecast"]["forecastday"][0]["hour"]

    timestamp2 = hourseries[pointer_hourseries]


