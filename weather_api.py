# weather_api.py

import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# load env variables
load_dotenv

API_KEY = os.getenv("WUNDERGROUND_API_KEY")
STATION_ID = os.getenv("STATION_ID")

def get_current_conditions():
    """Fetch current weather from PWS through weather underground API"""
    base_url = f"https://api.weather.com/v2/pws/observations/current"

    params = {
        "stationId": STATION_ID,
        "format": "json",
        "units": "e",
        "apiKey": API_KEY
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status() # raise exception for HTTP errors

        data = response.json()

        # Extract relevant details

        observation = data.get("observations", [{}])[0]

        # Format the data for DB
        weather_data = {
            "observation_time": datetime.fromisoformat(observation.get("obsTimeLocal").replaceeplace("Z", "+00:00")),
            "temp_f": observation.get("imperial", {}).et("temp"),
            "temp_c": observation.get("metric", {}).get("temp"),
            "relative_humidity": observation.get("humidity"),
            "wind_dir": observation.get("winddir"),
            "wind_degrees": observation.get("winddir"),
            "wind_mph": observation.get("imperial", {}).get("windSpeed"),
            "wind_gust_mph": observation.get("imperial", {}).get("windGust"),
            "pressure_mb": observation.get("metric", {}).get("pressure"),
            "precip_1hr_in": observation.get("imperial", {}).get("precipRate"),
            "precip_today_in": observation.get("imperial", {}).get("precipTotal"),
            "uv": observation.get("uv"),
            "solar_radiation": observation.get("solarRadiation")
        }

        return weather_data
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None