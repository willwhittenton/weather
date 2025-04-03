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