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
c = 0

STATION_SQL_HEADER = '''
INSERT INTO stations (id, name, latitude, longitude, firstSeen, lastSeen, cityId) VALUES
'''
STATION_SQL_FOOTER = '''
ON DUPLICATE KEY UPDATE
firstSeen = CASE WHEN firstSeen < VALUES(firstSeen) THEN firstSeen ELSE VALUES(firstSeen) END,
lastSeen = CASE WHEN lastSeen > VALUES(lastSeen) THEN lastSeen ELSE VALUES(lastSeen) END;
'''
current_station_sql = STATION_SQL_HEADER
css_count = 0

BIKE_SQL_HEADER = '''
INSERT INTO bikes (id, timeId, stationId, latitude, longitude) VALUES
'''
current_bike_sql = BIKE_SQL_HEADER
cbs_count =0

for timestamp in tqdm(glob('../../0_datasets/nextbike/*.json')):
    time_id = int(timestamp.split('\\')[-1][:-5])//180
    
    with open(timestamp, 'r', encoding='utf-8') as f:
        stations = json.load(f)['countries'][0]['cities'][0]['places']
        

        for station in stations:
            if not station['bike']:
                sql = f"({station['uid']}, {station['name']}, {station['lat']}, {station['lng']}, {time_id}, {time_id}, 1),\n"
                
                current_station_sql += sql
                css_count += 1

                for bike in station['bike_numbers']:
                    sql = f"({bike}, {time_id}, {station['uid']}, NULL, NULL),"
                    current_bike_sql += sql
                    cbs_count += 1

            else:
                sql = f"({station['bike_numbers'][0]}, {time_id}, NULL, {station['lat']}, {station['lng']}),"
                current_bike_sql += sql
                cbs_count += 1

    if css_count > 700:
        cursor.execute(current_station_sql[:-1] + STATION_SQL_FOOTER)
        db.commit()
        current_station_sql = STATION_SQL_HEADER
        css_count = 0

    if cbs_count > 500: # Marburg has ~400 bike, making sure not to overload the buffer
        cursor.execute(current_bike_sql[:-1])
        db.commit()
        current_station_sql = BIKE_SQL_HEADER
        cbs_count = 0
