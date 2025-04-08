# scheduler.py

import scheduler
import time
from datetime import datetime
from weather_collector import collect_and_store_weather
from db_utils import initialize_db
from config import COLLECTION_INTERVAL

def main():
    """Initialize db and schedule data collection"""
    print(f"Initializing weather data collection service at {datetime.now()}")

    initialize_db()

    # collect immediately on startup
    print("Collecting initial weather data...")
    collect_and_store_weather()

    # schedule regular collection
    schedule.every(COLLECTION_INTERVAL).minutes.do(collect_and_store_weather())

    print(f"Scheduled to collect data every {COLLECTION_INTERVAL} minutes")

    # keep 'er going
    while True:
        schedule.run_pending()
        time.sleep(1) #seconds

if __name__ == "__main__":
    main()