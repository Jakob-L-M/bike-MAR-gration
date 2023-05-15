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

for timestamp in tqdm(glob('../../0_datasets/nextbike/*.json')):
    c += 1
    time_id = int(timestamp.split('\\')[-1][:-5])//180
    
    with open(timestamp, 'r', encoding='utf-8') as f:
        stations = json.load(f)['countries'][0]['cities'][0]['places']
        
        try:
            for station in stations:
                if not station['bike']:
                    sql = '''INSERT INTO stations (id, name, latitude, longitude, firstSeen, lastSeen, cityId)
                    VALUES (%s, %s, %s, %s, %s, %s, 1)
                    ON DUPLICATE KEY UPDATE
                    firstSeen = CASE WHEN firstSeen < VALUES(firstSeen) THEN firstSeen ELSE VALUES(firstSeen) END,
                    lastSeen = CASE WHEN lastSeen > VALUES(lastSeen) THEN lastSeen ELSE VALUES(lastSeen) END;'''
                    values = [station['uid'], station['name'], station['lat'], station['lng'], time_id, time_id]

                    cursor.execute(sql, values)

                    for bike in station['bike_numbers']:
                        sql = 'INSERT INTO bikes (id, timeId, stationId, latitude, longitude) VALUES (%s, %s, %s, NULL, NULL)'
                        values = [bike, time_id, station['uid']]
                        cursor.execute(sql, values)

                else:
                    sql = 'INSERT INTO bikes (id, timeId, stationId, latitude, longitude) VALUES (%s, %s, NULL, %s, %s)'
                    values = [station['bike_numbers'][0], time_id, station['lat'], station['lng']]

                    cursor.execute(sql, values)

            if c % 15 == 0:
                db.commit()
        except:
            pass