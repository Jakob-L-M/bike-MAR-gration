import mysql.connector
import pandas as pd
from tqdm.auto import tqdm
from dotenv import load_dotenv
import os
from glob import glob

load_dotenv('../.env')
DATA_DIR = "../data/bikes_at_station/"

#load data from sql to file
def update_data():

    #create sql connection
    db = mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST"),
        user=os.environ.get("MYSQL_USER"),
        password=os.environ.get("MYSQL_PASSWORD"),
        database=os.environ.get("MYSQL_DATABASE")
    )
    cursor = db.cursor()

    #get stations
    query = """SELECT s.id, s.firstSeen, s.lastSeen
                FROM stations s """
    cursor.execute(query)
    stations = cursor.fetchall()


    #load data

    for s in (pbar := tqdm(stations)):
        stationId = s[0]
        first_seen = s[1]
        last_seen = s[2]
        last_known = 0
        old_df = None
        
        # fetch current local version and metadata info
        if os.path.exists(DATA_DIR + f"{stationId}.pickle"):
            old_df = pd.read_pickle(DATA_DIR + f"{stationId}.pickle")
            last_known = max(old_df['timeId'])
        
        query = f"""
        WITH base AS (
            SELECT
                s.id,
                b.timeId,
                s.cityId,
                s.latitude,
                s.longitude
            FROM (
                SELECT
                    *
                FROM
                    stations
                WHERE
                    id = {stationId} -- stationId
            ) s
            CROSS JOIN (
                SELECT DISTINCT
                    timeId
                FROM
                    bikes
                WHERE
                    timeId > {last_known - 40} -- last_known timeId, -40 since thats the furthers away join (2h) we perform
                    AND timeId BETWEEN {first_seen} -- firstSeen
                    AND {last_seen} -- lastSeen
            ) b
            -- WHERE b.timeId BETWEEN s.firstSeen AND s.lastSeen
        ),
        main AS (
            SELECT
                base.*,
                w.temp,
                w.feelsLikeTemp,
                w.isDay,
                w.description,
                w.cloud,
                w.wind,
                w.gust,
                e. `group`,
                COALESCE(n,
                    0) AS nBikes
            FROM
                base
                -- join info
            LEFT JOIN (
                SELECT
                    timeId,
                    COUNT(id) AS n
                FROM
                    bikes
                WHERE
                    stationId = {stationId} -- stationId
                GROUP BY
                    timeId) sInfo ON base.timeId = sInfo.timeId
                -- weather info
                JOIN weather w ON w.cityId = base.cityId
                    AND base.timeId = w.timeId
                    -- event info
            LEFT OUTER JOIN events e ON TO_DAYS(e. `date`) = TO_DAYS(FROM_UNIXTIME(base.timeId * 180))
        )
        SELECT
            main.*,
            b2.nBikes  AS 't-6',
            b5.nBikes  AS 't-15',
            b10.nBikes AS 't-30',
            b20.nBikes AS 't-60',
            b40.nBikes AS 't-120',
            a5.nBikes  AS 't+15',
            a10.nBikes AS 't+30',
            a15.nBikes AS 't+45',
            a20.nBikes AS 't+60'
        FROM
            main
            -- bX: before X timeIds
            -- aX: after X timeIds
            -- No outer join to exclude missing data
            JOIN main b2  ON main.timeId = b2.timeId - 2
            JOIN main b5  ON main.timeId = b5.timeId - 5
            JOIN main b10 ON main.timeId = b10.timeId - 10
            JOIN main b20 ON main.timeId = b20.timeId - 20
            JOIN main b40 ON main.timeId = b40.timeId - 40
            JOIN main a5  ON main.timeId = a5.timeId + 5
            JOIN main a10 ON main.timeId = a10.timeId + 10
            JOIN main a15 ON main.timeId = a15.timeId + 15
            JOIN main a20 ON main.timeId = a20.timeId + 20
        """
        cursor.execute(query)
        data = cursor.fetchall()
        
        # update info text
        pbar.set_description('Adding %s instances for station %s' % (len(data), stationId))
        
        # make data frame
        df = pd.DataFrame(data, columns=['stationId', 'timeId', 'cityId', 'latitude', 'longitude', 'temp', 'feelsLikeTemp', 'isDay', 'description', 'cloud', 'wind', 'gust', 'event_type', 'nBikes', 't-6', 't-15', 't-30', 't-60', 't-120', 't+15', 't+30', 't+45', 't+60'])
        
        # append to old frame
        if old_df is not None:
            df = pd.concat([old_df, df])

        #save as pickle
        df.to_pickle(DATA_DIR+f"{stationId}.pickle")

def get_data():
    dfs = []
    print('Getting data ready...', end='', sep='', flush=True)
    # iterate over all station files and append output
    for file in glob(DATA_DIR + '*.pickle') :
        dfs.append(pd.read_pickle(file))
        # break # for testing just load one station
    
    print('\b\b\b ✔ ', flush=True)
    return pd.concat(dfs)


if __name__ == '__main__':
    update_data()
