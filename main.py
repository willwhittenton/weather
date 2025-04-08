# main.py

import argparse
from weather_collector import collect_and_store_weather
from db_utils import initialize_db, get_latest_records
from scheduler_orig import main as run_scheduler

### show the records

def display_latest_records(count):
    """Display the latest records from the db"""
    df = get_latest_records(count)
    if not df.is_empty():
        print(f"\nLatest {df.height} weather observations:")

        for row in df.iter_rows():
            obs_time = row[0]
            temp = row[1]
            humidity = row[3]
            wind_speed = row [4]
            print(f"Time: {obs_time}, Temp: {temp}°F, Humidity: {humidity}%, Wind: {wind_speed} mph")

    else:
        print("No records found in the database.")


### here's how to run the thing 

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Weather Station Data Collection")
    parser.add_argument("--collect", action="store_true", help="Collect data once")
    parser.add_argument("--view", type=int, metavar="N", help="View the latest N records")
    parser.add_argument("--start", action="store_true", help="Start the scheduler")
    parser.add_argument("--export", type=str, metavar="FILE", help="Export the latest 100 records to CSV file")

    args = parser.parse_args()

    # initialize db
    initialize_db

    if args.collect:
        print("Collecting weather data once...")
        collect_and_store_weather()

    if args.view:
        display_latest_records(args.view)
    
    if args.export:
        df = get_latest_records(100)
        if not df.is_empty():
            df.write_csv(args.export)
            print(f"Exported {df.height} records to {args.export}")
        else:
            print("No data to export")

    if args.start:
        run_scheduler()

    # if no args, show help
    if not (args.collect or args.view or args.start or args.export):
        parser.print_help()

