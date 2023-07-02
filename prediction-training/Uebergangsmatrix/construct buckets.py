import configparser
import pickle

import mysql.connector
import numpy as np
from datetime import datetime as dt
from tqdm.auto import tqdm

# config
min_trips_per_bucket = 100
start_grain = 10
DATA_DIR = "C:\\Users\\belas\\OneDrive\\Documents\\UNI\\Semester 4\\Datenintegration\\bike-Mar-gration\\data\\"

# metadata
minTemp = None
maxTemp = None
minCloud = None
maxCloud = None
minWind = None
maxWind = None
minGust = None
maxGust = None
minHour = 0
maxHour = 23
minDescription = 0
maxDescription = 1


# weekday


# Bucketing:
# 1. Optionally for holiday/non-holiday:
# 2. construct equidistant buckets (start_grain buckets per attribute, start_gain_time buckets for hour)
#          (hashmap from bucketidentifiers to bucket (=trip_matrix + list of bucketIDs of merged buckets)
# 3. while bucket size < min_trips_per_bucket:
#    4. Select smallest bucket >0 (all buckets with 0 defalut to 0 matrix)
#    5. find best adjacent bucket to merge with (similar nr of trips)
#    6. merge buckets (update hashmap matrix, nr of merged buckets) and set both hashmap values to merged bucket


def get_DB():
    # create sql connection
    config = configparser.ConfigParser()
    config.read(r"C:\Users\belas\OneDrive\Documents\UNI\Semester 4\Datenintegration\bike-Mar-gration\.env")
    mydbConfig = config["mysql"]
    mydb = mysql.connector.connect(
        host=mydbConfig["MYSQL_HOST"],
        user=mydbConfig["MYSQL_USER"],
        password=mydbConfig["MYSQL_PASSWORD"],
        database=mydbConfig["MYSQL_DATABASE"]
    )
    return mydb

def get_trips():
    mydb = get_DB()
    mydb_cursor = mydb.cursor()
    # get trips
    querry = """SELECT t.startTime ,t.stationId ,t.nextStationId, w.temp, w.description, w.cloud, w.wind , w.gust 
                FROM trips t 
                JOIN weather w 
                ON w.timeId = t.startTime 
                WHERE t.stationId IS NOT NULL 
                AND t.nextStationId IS NOT NULL;"""
    mydb_cursor.execute(querry)
    trips = mydb_cursor.fetchall()

    return trips


def set_metadata():
    mydb = get_DB()
    mydb_cursor = mydb.cursor()

    # get metadata
    querry = """SELECT MIN(w.temp), MAX(w.temp), MIN(w.cloud), MAX(w.cloud), MIN(w.wind), MAX(w.wind), MIN(w.gust), MAX(w.gust)
                FROM weather w;"""
    mydb_cursor.execute(querry)
    metadata = mydb_cursor.fetchall()
    global minTemp, maxTemp, minCloud, maxCloud, minWind, maxWind, minGust, maxGust
    minTemp = metadata[0][0]
    maxTemp = metadata[0][1]
    minCloud = metadata[0][2]
    maxCloud = metadata[0][3]
    minWind = metadata[0][4]
    maxWind = metadata[0][5]
    minGust = metadata[0][6]
    maxGust = metadata[0][7]


def get_Bucket_identifier(trip):
    temp = round(((trip[3] - minTemp) / (maxTemp - minTemp)) * start_grain)
    cloud = round(((trip[5] - minCloud) / (maxCloud - minCloud)) * start_grain)
    wind = round(((trip[6] - minWind) / (maxWind - minWind)) * start_grain)
    gust = round(((trip[7] - minGust) / (maxGust - minGust)) * start_grain)
    description = round(
        ((decription_to_numeric(trip[4]) - minDescription) / (maxDescription - minDescription)) * start_grain)
    date = dt.fromtimestamp(trip[0] * 180)
    time = date.time()
    timefloat = (time.hour / 24 + time.minute / 1440)
    time_bucket = round(timefloat * start_grain)

    identifier = []
    identifier.append(temp)
    identifier.append(cloud)
    identifier.append(wind)
    identifier.append(gust)
    identifier.append(description)
    identifier.append(time_bucket)
    return identifier

def get_bucket_from_identifier_str(identifier:str):
    split_str = identifier.split("_")[:-1]
    return get_bucket_from_identifier([int(x) for x in split_str])

def get_bucket_from_identifier(identifier:list):
    if (maxTemp is None):
        set_metadata()
    bucket_borders = {}
    #temp min/max touple
    bucket_borders["temp"] = (float(minTemp) + float((maxTemp - minTemp) / start_grain) * (identifier[0]-0.5),
                        float(minTemp) +float((maxTemp - minTemp) / start_grain) * (identifier[0] + 0.5))
    #cloud min/max touple
    bucket_borders["cloud"] = (float(minCloud) +float((maxCloud - minCloud) / start_grain) * (identifier[1]-0.5),
                        float(minCloud) +float((maxCloud - minCloud) / start_grain) * (identifier[1] + 0.5))
    #wind min/max touple
    bucket_borders["wind"] = (float(minWind) +float((maxWind - minWind) / start_grain) * (identifier[2]-0.5),
                        float(minWind) +float((maxWind - minWind) / start_grain) * (identifier[2] + 0.5))
    #gust min/max touple
    bucket_borders["gust"] = (float(minGust) +float((maxGust - minGust) / start_grain) * (identifier[3]-0.5),
                        float(minGust) +float((maxGust - minGust) / start_grain) * (identifier[3] + 0.5))
    #description min/max touple
    description_borders = (float(minDescription) +float((maxDescription - minDescription) / start_grain) * (identifier[4]-0.5),
                        float(minDescription) +float((maxDescription - minDescription) / start_grain) * (identifier[4] + 0.5))
    possibilities = [  # rain descriptions from data, sort by intensity
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
    description_list = []
    for i in range(round(description_borders[0]*len(possibilities)), min(len(possibilities),round(description_borders[1]*len(possibilities))+1)):
        description_list.append(possibilities[i])
    bucket_borders["description"] = description_list

    #time min/max touple
    bucket_borders["time"] = (0 + (24 - 0) / start_grain * (identifier[5]-0.5),
                        0 + (24 - 0) / start_grain * (identifier[5] + 0.5))
    return bucket_borders



def get_all_stations():
    mydb = get_DB()
    mydb_cursor = mydb.cursor()

    # get stations
    querry = """SELECT DISTINCT s.id 
                FROM stations s 
                ORDER BY s.id ASC;"""
    mydb_cursor.execute(querry)
    stations = mydb_cursor.fetchall()
    return list([station[0] for station in stations])


def init_transition_matrix(list_of_all_stations):
    transition_matrix = np.zeros((len(list_of_all_stations), len(list_of_all_stations)))
    return transition_matrix


def bucket_id_to_string(bucket_identifier):
    bucket_id_string = ""
    for attribute in bucket_identifier:
        bucket_id_string += str(attribute)
        bucket_id_string += "_"
    return bucket_id_string


def contains_null(trip):
    for attribute in trip:
        if attribute is None:
            return True
    return False


def construct_buckets():
    print("Getting stations...")
    list_of_all_stations = get_all_stations()
    print("Getting trips...")
    trips = get_trips()
    buckets = {}
    set_metadata()
    print("Constructing buckets...")
    for trip in tqdm(trips):
        if contains_null(trip):
            continue
        bucket_identifier = get_Bucket_identifier(trip)
        bucket_id_string = bucket_id_to_string(bucket_identifier)
        if bucket_id_string in buckets:
            # update transition matrix
            from_station = list_of_all_stations.index(trip[1])
            to_station = list_of_all_stations.index(trip[2])
            buckets[bucket_id_string][0][from_station][to_station] += 1
        else:
            from_station = list_of_all_stations.index(trip[1])
            to_station = list_of_all_stations.index(trip[2])
            # init transition matrix
            matrix = init_transition_matrix(list_of_all_stations)
            buckets[bucket_id_string] = (matrix, [bucket_id_string])
            # update transition matrix
            buckets[bucket_id_string][0][from_station][to_station] += 1
    return buckets


def find_closest_bucket(bucket, buckets):
    closest_bucket = None
    closest_distance = None
    for bucket_in_cluster in buckets[bucket][1]:
        string_arr_id = bucket_in_cluster.split("_")
        numeric_id = []
        for string in string_arr_id[:-1]:
            numeric_id.append(int(string))

        # find closest adjacent bucket
        for attr_bucket in range(len(numeric_id)):
            if (numeric_id[attr_bucket] > 0):
                numeric_id[attr_bucket] -= 1
                bucket_id_string = bucket_id_to_string(numeric_id)
                # check if already merged
                if (bucket_id_string in buckets[bucket][1]):
                    numeric_id[attr_bucket] += 1

                else:
                    if bucket_id_string in buckets:
                        distance = abs(sum(sum(buckets[bucket][0])) / len(buckets[bucket][1]) - sum(
                            sum(buckets[bucket_id_string][0])) / len(buckets[bucket][1]))
                        if (closest_distance is None or distance < closest_distance):
                            closest_bucket = bucket_id_string
                            closest_distance = distance
                    numeric_id[attr_bucket] += 1
            if (numeric_id[attr_bucket] < start_grain):
                numeric_id[attr_bucket] += 1
                bucket_id_string = bucket_id_to_string(numeric_id)
                if (bucket_id_string in buckets[bucket][1]):
                    numeric_id[attr_bucket] -= 1
                else:
                    if bucket_id_string in buckets:
                        distance = abs(sum(sum(buckets[bucket][0])) / len(buckets[bucket][1]) - sum(
                            sum(buckets[bucket_id_string][0])) / len(buckets[bucket][1]))
                        if (closest_distance is None or distance < closest_distance):
                            closest_bucket = bucket_id_string
                            closest_distance = distance
                    numeric_id[attr_bucket] -= 1
    return closest_bucket


def run_merge():
    buckets = construct_buckets()
    merge_occured = True
    print("Merging buckets...")
    while merge_occured:
        merge_occured = False
        iterated_buckets = 0
        for bucket in buckets:
            iterated_buckets += 1
            if (0 < sum(sum(buckets[bucket][0])) < min_trips_per_bucket):
                # merge
                bucket_to_merge = find_closest_bucket(bucket, buckets)
                if (bucket_to_merge is None):
                    continue
                new_matrix = buckets[bucket][0] + buckets[bucket_to_merge][0]
                buckets[bucket_to_merge][1].extend(buckets[bucket][1])
                buckets[bucket_to_merge] = (new_matrix, buckets[bucket_to_merge][1])
                for update_bucket in buckets[bucket][1]:
                    buckets[update_bucket] = buckets[bucket_to_merge]
                merge_occured = True
                #print("merged bucket:" + str(bucket) + " into bucket:" + str(bucket_to_merge))
                print("iterated "+str(iterated_buckets)+" buckets of "+str(len(buckets)))
                break

    print("Merging complete")
    return buckets


def decription_to_numeric(description):
    possibilities = [  # rain descriptions from data, sort by intensity
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
        return possibilities.index(description) / len(possibilities)
    else:
        # raise error, so that new descriptions can be added
        return 0.5




print("Starting merge algo...")
#calculated_buckets = run_merge()
print("Merge algo finished")
print("Saving buckets...")
#with open(DATA_DIR+'buckets.pickle', 'wb') as handle:
#    pickle.dump(calculated_buckets, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load_buckets():
    with open(r'C:\Users\belas\OneDrive\Documents\UNI\Semester 4\Datenintegration\bike-Mar-gration\data\buckets.pickle', 'rb') as handle:
        buckets = pickle.load(handle)
    return buckets

def load_normalized_buckets():
    with open(DATA_DIR+'normalized_buckets.pickle', 'rb') as handle:
        buckets = pickle.load(handle)
    return buckets

def get_weather_bucket_count(bucket: str):
    mydb = get_DB()
    mydb_cursor = mydb.cursor()
    bucket_borders = get_bucket_from_identifier_str(bucket)

    description_concat_str = ""
    for description in bucket_borders["description"][:-1]:
        description_concat_str += "'"+description + "', "
    description_concat_str +="'"+ bucket_borders["description"][-1]+"'"

    querry= "SELECT COUNT(*) FROM weather WHERE " + \
        "temp BETWEEN " + str(bucket_borders["temp"][0]) + " AND " + str(bucket_borders["temp"][1]) + " AND " + \
        "cloud BETWEEN " + str(bucket_borders["cloud"][0]) + " AND " + str(bucket_borders["cloud"][1]) + " AND " + \
        "wind BETWEEN " + str(bucket_borders["wind"][0]) + " AND " + str(bucket_borders["wind"][1]) + " AND " + \
        "gust BETWEEN " + str(bucket_borders["gust"][0]) + " AND " + str(bucket_borders["gust"][1]) + " AND " + \
        "description IN (" +description_concat_str + ") AND " + \
        "hour(FROM_UNIXTIME(weather.timeId*180))+minute(FROM_UNIXTIME(weather.timeId*180))/60 BETWEEN "+ str(bucket_borders["time"][0])+" AND "+str(bucket_borders["time"][1])
    mydb_cursor.execute(querry)
    result = mydb_cursor.fetchall()
    return result[0][0]

def normalize_weather_buckets():
    normalized_buckets = {}
    buckets = load_buckets()
    for key, value in tqdm(buckets.items()):
        #check if already computed for another bucket in this group
        if (key in normalized_buckets):
            continue
        #compute sum of all bucket occurences in this group
        weather_count_sum = 0
        for weather_bucket in value[1]:
            weather_count_sum += get_weather_bucket_count(weather_bucket)
        if (weather_count_sum == 0):
            continue
        normalized_matrix = value[0] / weather_count_sum
        #set normalized matrix for all buckets
        for weather_bucket in value[1]:
            normalized_buckets[weather_bucket] = normalized_matrix

    with open(DATA_DIR+'normalized_buckets.pickle', 'wb') as handle:
        pickle.dump(normalized_buckets, handle, protocol=pickle.HIGHEST_PROTOCOL)


def adjust_by_stationlifetime():
    normalized_buckets = load_normalized_buckets()
    mydb = get_DB()
    mydb_cursor = mydb.cursor()
    querry = "SELECT MIN(startTime), MAX(endTime ) FROM trips"
    mydb_cursor.execute(querry)
    result = mydb_cursor.fetchall()
    min_start_time = result[0][0]
    max_end_time = result[0][1]

    querry = "SELECT id, firstseen, lastseen FROM stations ORDER BY id ASC"
    mydb_cursor.execute(querry)
    result = mydb_cursor.fetchall()
    relative_station_lifetime = []
    for station_first_last in result:
        relative_station_lifetime.append((station_first_last[2]-station_first_last[1])/(max_end_time-min_start_time))
    adjusted_buckets = {}
    for key, value in tqdm(normalized_buckets.items()):
        for i in range(value.shape[0]):
            for j in range(value.shape[1]):
                value[i][j] = value[i][j] * 1/relative_station_lifetime[i] * 1/relative_station_lifetime[j]
        adjusted_buckets[key] = value
    with open(DATA_DIR+'adjusted_buckets.pickle', 'wb') as handle:
        pickle.dump(adjusted_buckets, handle, protocol=pickle.HIGHEST_PROTOCOL)


#normalize_weather_buckets()

adjust_by_stationlifetime()