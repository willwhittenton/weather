import os
from dotenv import load_dotenv

load_dotenv()


# API
API_KEY = os.getenv("WUNDERGOUND_API_KEY")
STATION_ID = os.getenv("STATION_ID")
BASE_URL = "https://api.weather.com/v2/pws/observations/all/1day"


# Data storage
DB_PATH = "data/weather_data.duckdb"
TABLE_NAME = "weather_observations"


# schedule (days)
COLLECTION_INTERVAL = 15
COLLECTION_TIME = "minutes"