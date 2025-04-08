# analysis.py

import duckdb
import polars as pl
from datetime import datetime, timedelta

# Connect to your existing DuckDB database
conn = duckdb.connect('data/weather_data.duckdb')

# Example 1: Basic query to fetch recent records
def get_recent_observations(limit=10):
    query = """
    SELECT 
        observation_time,
        station_id,
        neighborhood,
        temp_f,
        humidity,
        wind_mph,
        precip_today_in
    FROM weather_observations
    ORDER BY observation_time DESC
    LIMIT ?
    """
    
    # Execute query and convert to Polars DataFrame
    result = conn.execute(query, [limit]).pl()
    return result

# Example 2: Get daily temperature averages for the past week
def get_daily_temperature_averages(days=7):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    query = """
    SELECT 
        CAST(observation_time AS DATE) AS date,
        AVG(temp_f) AS avg_temp,
        MIN(temp_f) AS min_temp,
        MAX(temp_f) AS max_temp,
        AVG(humidity) AS avg_humidity
    FROM weather_observations
    WHERE observation_time BETWEEN ? AND ?
    GROUP BY CAST(observation_time AS DATE)
    ORDER BY date
    """
    
    result = conn.execute(query, [start_date, end_date]).pl()
    return result

# Example 3: Get observations by neighborhood
def get_neighborhood_stats():
    query = """
    SELECT 
        neighborhood,
        COUNT(*) AS observation_count,
        AVG(temp_f) AS avg_temp,
        AVG(humidity) AS avg_humidity,
        AVG(wind_mph) AS avg_wind,
        MAX(precip_today_in) AS max_precip
    FROM weather_observations
    WHERE neighborhood IS NOT NULL
    GROUP BY neighborhood
    ORDER BY neighborhood
    """
    
    result = conn.execute(query).pl()
    return result

# Example 4: Find extreme weather events
def find_extreme_weather():
    query = """
    SELECT 
        observation_time,
        station_id,
        neighborhood,
        temp_f,
        wind_mph,
        wind_gust_mph,
        precip_rate_in,
        humidity
    FROM weather_observations
    WHERE 
        temp_f > 95 OR
        temp_f < 32 OR
        wind_mph > 20 OR
        wind_gust_mph > 30 OR
        precip_rate_in > 0.5
    ORDER BY observation_time DESC
    """
    
    result = conn.execute(query).pl()
    return result

# Example 5: Compare current conditions to historical averages
def compare_to_historical_averages(days_back=30):
    query = """
    WITH current_conditions AS (
        SELECT 
            AVG(temp_f) AS current_avg_temp,
            AVG(humidity) AS current_avg_humidity,
            AVG(wind_mph) AS current_avg_wind
        FROM weather_observations
        WHERE observation_time >= CURRENT_DATE
    ),
    historical AS (
        SELECT 
            AVG(temp_f) AS historical_avg_temp,
            AVG(humidity) AS historical_avg_humidity,
            AVG(wind_mph) AS historical_avg_wind
        FROM weather_observations
        WHERE 
            observation_time < CURRENT_DATE AND
            observation_time >= date_add(-?, CURRENT_DATE)
    )
    SELECT 
        current_avg_temp,
        historical_avg_temp,
        current_avg_temp - historical_avg_temp AS temp_diff,
        current_avg_humidity,
        historical_avg_humidity,
        current_avg_humidity - historical_avg_humidity AS humidity_diff,
        current_avg_wind,
        historical_avg_wind,
        current_avg_wind - historical_avg_wind AS wind_diff
    FROM current_conditions, historical
    """
    
    result = conn.execute(query, [days_back]).pl()
    return result

# Example usage
if __name__ == "__main__":
    print("Recent weather observations:")
    recent = get_recent_observations(5)
    print(recent)
    
    print("\nDaily temperature averages for the past week:")
    daily_avg = get_daily_temperature_averages()
    print(daily_avg)
    
    print("\nWeather statistics by neighborhood:")
    neighborhood_stats = get_neighborhood_stats()
    print(neighborhood_stats)
    
    print("\nExtreme weather events:")
    extreme = find_extreme_weather()
    print(extreme)
    
    print("\nComparison to historical averages:")
    comparison = compare_to_historical_averages()
    print(comparison)
    
    # Close connection when done
    conn.close()