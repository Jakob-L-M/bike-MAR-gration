import mysql.connector
from dotenv import load_dotenv
import os
from glob import glob
import json
from tqdm import tqdm

load_dotenv('../.env')

db = mysql.connector.connect(
  host=os.getenv('MYSQL_HOST'),
  user=os.getenv('MYSQL_USER'),
  password=os.getenv('MYSQL_PASSWORD'),
  database=os.getenv('MYSQL_DATABASE')
)

cursor = db.cursor()

cursor.execute("SELECT DISTINCT(id) FROM bikes")

bike_ids = [i[0] for i in cursor.fetchall()]

def get_trips_for_bike(bike_id):
    cursor.execute(f"SELECT * FROM bikes WHERE id = {bike_id} ORDER BY timeId")
    
    trips = []
    # list of trips where each trip is:
    # bikeId, tripNum, start_time, end_time, station, lat, lon, nextStation

    next_known = 0
    c = 1
    
    for record in list(cursor.fetchall()):
        if record[1] >= next_known: # record[1]: timeId -> check if we don't know how this trip ends
            
            # find the end of the trip aka next station
            stationId = record[2] if record[2] is not None else 'NULL'
            lat = record[3] if record[3] is not None else 'NULL'
            lon = record[4] if record[4] is not None else 'NULL'

            cursor.execute(f"SELECT * FROM bikes WHERE id = {bike_id} AND timeId > {record[1]} AND NOT (stationId <=> {stationId} AND latitude <=> {lat} AND longitude <=> {lon}) ORDER BY timeId LIMIT 1")
            
            next_station = cursor.fetchall()
            if len(next_station) == 0: # no more trips happen
                break
            
            upper_time = next_station[0][1]
            
            # get all timeIds for that trip
            cursor.execute(f"SELECT id, stationId, latitude, longitude, MIN(timeId) AS start, MAX(timeId) AS end FROM bikes WHERE id = {bike_id} AND timeId BETWEEN {record[1]} AND {upper_time - 1} GROUP BY id, stationId, latitude, longitude")
            
            trip = cursor.fetchall()

            if len(trip) > 1:
                print('WARNING TRIP CALCULATION INCORRECT')
                print(record, next_station, trip, sep='\n')
                raise LookupError()
            trip = trip[0]

            trips.append([bike_id, c, trip[4],
                          trip[5], trip[1],
                          trip[2] if trip[2] == None else float(trip[2]),
                          trip[3] if trip[3] == None else float(trip[3]),
                          next_station[0][2]])

            c += 1 # increase trip counter
            next_known = upper_time

    return trips

trips = get_trips_for_bike(bike_ids[345])
for i, t in enumerate(trips):
    print(i,': ', t, sep='')
