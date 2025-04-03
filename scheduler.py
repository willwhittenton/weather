# scheduler.py

import schedule
import time
from datetime import datetime
import os
from weather_api import get_current_conditions
from db_utils import initialize_db, save_weather_data

def collect_weather_data():
    """Collect weather data and save to database"""
    print(f"Collecting weather data at {datetime.now()}")

    # Initialize db connection
    conn = initialize_db()

    # Get current weather
    weather_data = get_current_conditions()

    if weather_data:
        # save to db
        save_weather_data(weather_data, conn)
        print("Weather data saved successfully!")
    else:
        print("Failed to collect weather data")

def main():
    """Main function to set up and run the scheduler"""
    print("Starting weather Data Collection Service")

    # Run 1x at startup
    collect_weather_data()

    # schedule to run hourly
    schedule.every().hour.do(collect_weather_data)

    # continue running
    while True:
        schedule.run_pending()
        time.sleep(60) # checking every minute

if __name__ == "__main__":
    main()