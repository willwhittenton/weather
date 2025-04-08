# weather_collector.py

import requests
import datetime
import polars as pl
from config import API_KEY, STATION_ID, BASE_URL
from db_utils import save_weather_data


### getting the weather
def fetch_weather_data():
    """ get yesterday's data from weather underground API"""
    params = {
        "stationId": STATION_ID,
        "format": "json",
        "units": "e",
        "apiKey": API_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status() # exception if occurs

        data = response.json()

        observation = data.get("observations", [{}])[0]

        # extract data, format for DB
        weather_data = {
                "observation_time":     observation.get("obsTimeLocal"),
                "station_id":           observation.get("stationID"),
                "longitude":            observation.get("lon"),
                "latitude":             observation.get("lat"),
                "temp_f":               observation.get("imperial", {}).get("tempAvg"),
                "heat_index":           observation.get("imperial", {}).get("heatindexAvg"),
                "wind_chill":           observation.get("imperial", {}).get("windchillAvg"),
                "dew_point":            observation.get("imperial", {}).get("dewptAvg"),
                "humidity":             observation.get("humidityAvg"),
                "wind_degrees":         observation.get("winddirAvg"),
                "wind_mph":             observation.get("imperial", {}).get("windspeedAvg"),
                "wind_gust_mph":        observation.get("imperial", {}).get("windgustAvg"),
                "pressure_hg":          observation.get("imperial", {}).get("pressureMax"),
                "precip_total":         observation.get("imperial", {}).get("precipTotal"),
                "precip_rate":          observation.get("imperial", {}).get("precipRate"),
                "collection_time":      datetime.datetime.now().isoformat()
        }

        return weather_data
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None
    
def collect_and_store_weather():
    """Collect weather data and store it in the db"""
    weather_data = fetch_weather_data()

    if weather_data:
        save_weather_data(weather_data)
        print(weather_data)
    else:
        print("No data collected due to an error.")