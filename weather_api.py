# weather_api.py

import requests
import os
import time
from dotenv import load_dotenv
from datetime import datetime

# load env variables
load_dotenv()

API_KEY = os.getenv("WUNDERGROUND_API_KEY")



# for single station: 
STATION_ID = os.getenv("STATION_ID")

# multiple stations:
STATIONS = [
    {"id": os.getenv("STATION_ID_1", ""), "name": "Northbay"},
    {"id": os.getenv("STATION_ID_2", ""), "name": "Hunter's Creek"},
    #{"id": os.getenv("STATION_ID_3", ""), "name": "Tertiary Station"}
]

# for single station remove station_id in parenthesis below
# currently built to handle multiple stations, or ID as entered when UDF called
def get_current_conditions(station_id):
    """Fetch current weather from PWS through weather underground API"""
    base_url = f"https://api.weather.com/v2/pws/observations/current"
    
    # for single station replace "stationId": STATION_ID
    params = {
        "stationId": station_id,
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
            "observation_time": datetime.fromisoformat(observation.get("obsTimeLocal")),
            "station_id": observation.get("stationID"),
            "longitude": observation.get("lon"),
            "latitude": observation.get("lat"),
            "neighborhood": observation.get("neighborhood"),
            "temp_f": observation.get("imperial", {}).get("temp"),
            "heat_index": observation.get("imperial", {}).get("heatIndex"),
            "wind_chill": observation.get("imperial", {}).get("windChill"),
            "dew_point": observation.get("imperial", {}).get("dewpt"),
            "humidity": observation.get("humidity"),
            "wind_degrees": observation.get("winddir"),
            "wind_mph": observation.get("imperial", {}).get("windSpeed"),
            "wind_gust_mph": observation.get("imperial", {}).get("windGust"),
            "pressure_hg": observation.get("imperial", {}).get("pressure"),
            "precip_today_in": observation.get("imperial", {}).get("precipTotal"),
            "precip_rate_in": observation.get("imperial", {}).get("precipRate"),
            "collection_time": datetime.now().isoformat()
        }

        return weather_data
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None


### update to utilize multiple stations

def get_current_conditions_multiple():
    """Fetch current conditions for all configured stations"""
    weather_data = []
    
    for station in STATIONS:
        if not station["id"]:
            print(f"Skipping station '{station['name']}' - no ID configured")
            continue
            
        print(f"Fetching data for station {station['id']} ({station['name']})...")
        data = get_current_conditions(station["id"])
        
        if data:
            weather_data.append(data)
            print(f"  Success: {data['temp_f']}°F at {data['neighborhood']}")
        else:
            print(f"  Failed to retrieve data for station {station['id']}")
        
        # Add a short delay to avoid rate limiting
        time.sleep(1)
    
    return weather_data

# testing to ensure it works
if __name__ == "__main__":
    print("Testing Weather Underground API connection...")
    weather_data = get_current_conditions()
    if weather_data:
        print("Connection successful! Current temperature:", weather_data["temp_f"], "°F")
        print(weather_data)
    else:
        print("Failed to retrieve data. Check your API key and station ID.")