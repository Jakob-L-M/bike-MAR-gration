import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv('../.env')

db = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST'),
    user=os.getenv('MYSQL_USER'),
    password=os.getenv('MYSQL_PASSWORD'),
    database=os.getenv('MYSQL_DATABASE')
)

cursor = db.cursor()

# Only consider bikes that are currently at some station
# If bike is rented, the trip entry can not change anyway
cursor.execute(f"SELECT id, startTime FROM (SELECT DISTINCT id FROM bikes WHERE timeId >= (SELECT MAX(timeId) FROM bikes)) b LEFT JOIN ( SELECT bikeId, MAX(startTime) as startTime FROM trips GROUP BY bikeId) t ON b.id = t.bikeId;")

# bikeId, max known startTime
bikes = cursor.fetchall()


def get_trips_for_bike(bike_tuple):
    bike_id = bike_tuple[0]
    start = bike_tuple[1] if bike_tuple[1] != None else 0

    cursor.execute(
        f"SELECT * FROM bikes WHERE id = {bike_id} AND timeId >= {start} ORDER BY timeId")

    trips = []
    # list of trips where each trip is:
    # bikeId, start_time, end_time, station, lat, lon, nextStationId, nextStationStart

    next_known = 0

    for record in list(cursor.fetchall()):
        if record[1] >= next_known:  # record[1]: timeId -> check if we don't know how this trip ends

            # find the end of the trip aka next station
            stationId = record[2] if record[2] is not None else 'NULL'
            lat = record[3] if record[3] is not None else 'NULL'
            lon = record[4] if record[4] is not None else 'NULL'

            cursor.execute(
                f"SELECT * FROM bikes WHERE id = {bike_id} AND timeId > {record[1]} AND NOT (stationId <=> {stationId} AND latitude <=> {lat} AND longitude <=> {lon}) ORDER BY timeId LIMIT 1")

            next_station = cursor.fetchall()
            if len(next_station) == 0:  # no more trips happen
                # ongoing trip
                cursor.execute(
                    f"SELECT id, stationId, latitude, longitude, MIN(timeId) AS start, MAX(timeId) AS end FROM bikes WHERE id = {bike_id} AND timeId >= {record[1]} GROUP BY id, stationId, latitude, longitude")

            else:
                # there is a next station
                upper_time = next_station[0][1]

                # get all timeIds for that trip
                cursor.execute(
                    f"SELECT id, stationId, latitude, longitude, MIN(timeId) AS start, MAX(timeId) AS end FROM bikes WHERE id = {bike_id} AND timeId BETWEEN {record[1]} AND {upper_time - 1} GROUP BY id, stationId, latitude, longitude")

            trip = cursor.fetchall()

            if len(trip) > 1:
                print('WARNING TRIP CALCULATION INCORRECT')
                print(record, next_station, trip, sep='\n')
                raise LookupError()
            trip = trip[0]

            trips.append([bike_id,
                          trip[4],
                          trip[5],
                          trip[1],
                          trip[2] if trip[2] == None else float(trip[2]),
                          trip[3] if trip[3] == None else float(trip[3]),
                          # check if trip is ongoing
                          None if len(next_station) == 0 else next_station[0][2],
                          None if len(next_station) == 0 else next_station[0][1]])

            next_known = trip[5]+1

    return trips

def update_bike(bike_tuple):
    trips = get_trips_for_bike(bike_tuple)
    sql = "REPLACE INTO `trips` VALUES \n"
    for t in trips:
        # Override on duplicate key
        values = str(t).replace("'", '').replace('None', 'NULL')[1:-1]
        sql += f"({values}),\n"
    sql = sql[:-2] + ';' # exclude last , and \n
    cursor.execute(sql)
    db.commit()
    print(f"Added {len(trips)} for bike {bike_tuple[0]}")
    return len(trips) - 1

s = 0
for i, b in enumerate(bikes):           
    print(i+1, '/', len(bikes), sep='', end=' ')
    s += update_bike(b)
print('Added', s, 'new trips in total')