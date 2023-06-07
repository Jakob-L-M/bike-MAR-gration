import mysql.connector
from dotenv import load_dotenv
import os
import urllib.request
import json
from time import sleep

load_dotenv('../.env')

db = mysql.connector.connect(
  host=os.getenv('MYSQL_HOST'),
  user=os.getenv('MYSQL_USER'),
  password=os.getenv('MYSQL_PASSWORD'),
  database=os.getenv('MYSQL_DATABASE')
)

cursor = db.cursor()

for year in range(2022, 2030):
    with urllib.request.urlopen(f"https://feiertage-api.de/api/?jahr={year}&nur_land=HE") as url:
        data = json.load(url)

        for event in data:
            sql = f"INSERT INTO events (`date`, name, `value`, description, `group`) VALUES ('{data[event]['datum']}', '{event}', NULL, NULL, 1);"
            cursor.execute(sql)
            db.commit()

    sleep(2) # lets be polite :)

