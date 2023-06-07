import time
from datetime import datetime, timedelta
import requests

#static variables
with open(r"C:/Users/belas/OneDrive/Documents/UNI/Semester 4/Datenintegration/bike-MAR-gration/0_datasets/apikey.txt", "r") as f:
    API_KEY = f.read()
FILE_PATH = r"C:/bike-mar-gration-weatherdata/"
successful_dates = open(r"C:/Users/belas/OneDrive/Documents/UNI/Semester 4/Datenintegration/bike-MAR-gration/0_datasets/successful_dates.txt", "w")
failed_dates = open(r"C:/Users/belas/OneDrive/Documents/UNI/Semester 4/Datenintegration/bike-MAR-gration/0_datasets/failed_dates.txt", "w")

#get weather data for a specific date
def getWeatherData(date):
    querry = f"http://api.weatherapi.com/v1/history.json?key={API_KEY}&q=Marburg&dt={date.year}-{date.month}-{date.day}"
    response = requests.get(querry)
    if response.status_code != 200:
        print(f"Request for {date.year}-{date.month}-{date.day} failed")
        failed_dates.write(f"{date.year}-{date.month}-{date.day}\n")
        return
    else:
        print(f"Request for {date.year}-{date.month}-{date.day} successful")
        successful_dates.write(f"{date.year}-{date.month}-{date.day}\n")
        with open(f"{FILE_PATH}/{date.year}-{date.month}-{date.day}.json", "w") as f:
            f.write(response.text)



firstDate = datetime(2023, 5, 6)
lastDate = datetime(2023, 5, 9)
#loop through all days from 2023-01-01 to now
while firstDate <= lastDate:
    getWeatherData(firstDate)
    firstDate += timedelta(days=1)
    #sleep for 1 second to not overload the api
    time.sleep(0.5)
