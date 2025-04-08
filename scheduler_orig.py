# scheduler.py

import schedule
import time
import argparse
from datetime import datetime, timedelta
import os
from weather_api import get_current_conditions, get_current_conditions_multiple
from db_utils import initialize_db, save_weather_data
from config import COLLECTION_INTERVAL, COLLECTION_TIME

def collect_weather_data():
    """Collect weather data and save to database"""
    print(f"Collecting weather data at {datetime.now()}")

    # Initialize db connection
    conn = initialize_db()

    # Get current weather
    weather_data = get_current_conditions()

    if weather_data:
        print("Connection successful! Current temperature:", weather_data["temp_f"], "°F")
        print("Saving...")
        # save to db
        save_weather_data(weather_data)
        print("Weather data saved successfully!")
    else:
        print("Failed to collect weather data")


### multiple stations save
def collect_weather_data_multiple():
    """
    Save weather data to DuckDB using Polars
    Collects data from multiple lists, defined in weather_api & referencing the config file
    """
    
    print(f"Collecting weather data at {datetime.now()}")

    # Initialize db connection
    conn = initialize_db()

    # Get current weather
    weather_data = get_current_conditions_multiple()

    if weather_data:
        print("Connection successful!")# Current temperature:", weather_data["temp_f"], "°F")
        print("Saving...")
        # save to db
        save_weather_data(weather_data)
        print("Weather data saved successfully!")
    else:
        print("Failed to collect weather data")



### collecting history

def collect_historical_data(start_date, end_date):
    """Collect historical weather data for a date range.
    
    Args:
        start_date (datetime): Start date
        end_date (datetime): End date
    """
    print(f"Collecting historical data from {start_date} to {end_date}")
    
    # Initialize database connection
    conn = initialize_db()
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y%m%d")
        print(f"Collecting data for {date_str}")
        
        # Get historical data
        historical_data = get_historical_data(date_str)
        
        if historical_data:
            # Save data to database
            save_historical_data(historical_data, conn)
            print(f"Historical data for {date_str} saved successfully!")
        else:
            print(f"Failed to collect historical data for {date_str}")
        
        # Move to next day
        current_date = current_date + timedelta(days=1)
        
        # Add a delay to avoid API rate limits
        time.sleep(2)

def main():
    """Main function to set up and run the scheduler"""
    print("Starting weather Data Collection Service")

   
    parser = argparse.ArgumentParser(description='Weather Data Collection Service')
    parser.add_argument('--historical', action='store_true', help='Collect historical data')
    parser.add_argument('--days', type=int, default=7, help='Number of past days to collect')
    parser.add_argument("--start", action="store_true", help="Start the scheduler")
    args = parser.parse_args()

    if args.historical:
        # Collect historical data
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=args.days)
        collect_historical_data(start_date, end_date)
        return

    # Run 1x at startup
    collect_weather_data_multiple()
    print("First run complete. Schedule starting.")

    # schedule to run
    schedule.every(COLLECTION_INTERVAL).minutes.do(collect_weather_data_multiple)

    # continue running
    n = 0
    while True:
        schedule.run_pending()
        time.sleep(600) # checking every 5 minutes
        n = n + 5
        print(f"Collecting every {COLLECTION_INTERVAL} {COLLECTION_TIME}. Elapsed minutes: {n}")

if __name__ == "__main__":
    main()