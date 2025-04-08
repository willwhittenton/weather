# db_utils.py

import duckdb
import polars as pl
import os
from config import DB_PATH, TABLE_NAME
from datetime import datetime


### set up DB, table

def initialize_db():
    """initialize the DuckDB database with the required schema"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = duckdb.connect(DB_PATH)

# Create weather_observations table
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                 
                --date and metadata
                observation_time TIMESTAMP,
                station_id STRING,
                longitude FLOAT,
                latitude FLOAT,
                neighborhood STRING,
                            
                -- temp data
                temp_f FLOAT,       -- use avg
                heat_index FLOAT,   -- use avg
                wind_chill FLOAT,   -- use avg
                dew_point FLOAT,    -- use avg
                
                -- air data
                humidity FLOAT,     -- use avg
                wind_degrees INT,   -- use avg
                wind_mph FLOAT,     -- use avg 
                wind_gust_mph FLOAT,-- use avg
                pressure_hg FLOAT,  -- use max

                -- rain data
                precip_today_in FLOAT,
                precip_rate_in FLOAT,
                 
                -- system fields
                collection_time TIMESTAMP
            )
    """
    )

    conn.close()


''' removing to revert to current observation api
    # Create weather_observations table
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                 
                --date and metadata
                observation_time TIMESTAMP,
                station_id VARCHAR,
                longitude FLOAT,
                latitude FLOAT,
                            
                -- temp data
                temp_f FLOAT,       -- use avg
                heat_index FLOAT,   -- use avg
                wind_chill FLOAT,   -- use avg
                dew_point FLOAT,    -- use avg
                
                -- air data
                humidity FLOAT,     -- use avg
                wind_degrees INT,   -- use avg
                wind_mph FLOAT,     -- use avg 
                wind_gust_mph FLOAT,-- use avg
                pressure_hg FLOAT,  -- use max

                -- rain data
                precip_total FLOAT,
                precip_rate FLOAT,
                 
                -- system fields
                collection_time TIMESTAMP
            )
    """
    )

    conn.close()

'''

### save data to table. table defined in-line

def save_weather_data(weather_data):
    """
    Save weather data to DuckDB using Polars
    Collects data from multiple lists, defined in weather_api & referencing the config file
    """
    if not weather_data:
        print("No data to save")
        return
        
    print(f"Saving {len(weather_data)} weather observations to database...")

    # Convert the data to a Polars DF
    df = pl.DataFrame([weather_data])

    # Connect to DB
    conn = duckdb.connect(DB_PATH)

    # Add collection timestamp
    df = df.with_columns(pl.lit(datetime.now()).alias("collection_time"))

    # Insert data into the table using DuckDB's from_arrow apability
    ''' fix bc now using a list instead of df?
        conn.execute(f"""
                 Insert INTO {TABLE_NAME} 
                 SELECT * from df
                 """)
    '''
    for data in weather_data:
         conn.execute("""
         INSERT INTO weather_observations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
         """, [
             data["observation_time"], 
             data["station_id"], 
             data["longitude"], 
             data["latitude"], 
             data["neighborhood"], 
             data["temp_f"], 
             data["heat_index"], 
             data["wind_chill"], 
             data["dew_point"], 
             data["humidity"], 
             data["wind_degrees"], 
             data["wind_mph"], 
             data["wind_gust_mph"], 
             data["pressure_hg"], 
             data["precip_today_in"], 
             data["precip_rate_in"], 
             data["collection_time"]
         ])
    
    conn.close

    print(f"Data stored successfully!")


### most recent records. n editable

def get_latest_records(n=5):
    """Retrieve the latest n records as a Polars DataFrame"""
    conn = duckdb.connect(DB_PATH)
    
    # Execute query and convert to Polars df
    result = conn.execute(f"""
    SELECT * FROM {TABLE_NAME}
    ORDER BY collection_time DESC
    LIMIT {n}
    """)
    
    result_df = pl.from_arrow(result.arrow())
    
    conn.close()
    return result_df



### analysis functions

def analyze_weather_data(days=7):
    """Analyze recent weather data using Polars"""
    conn = duckdb.connect(DB_PATH)
    
    # Query recent data
    query = f"""
    SELECT * FROM weather_observations 
    WHERE observation_time >= CURRENT_DATE - {days}
    """
    
    # Execute query and convert to Polars DataFrame
    result = conn.execute(query).arrow()
    df = pl.from_arrow(result)
    
    # Calculate daily statistics
    daily_stats = (
        df.group_by(pl.col("observation_time").dt.date().alias("date"))
        .agg(
            pl.col("temp_f").mean().alias("avg_temp_f"),
            pl.col("temp_f").max().alias("max_temp_f"),
            pl.col("temp_f").min().alias("min_temp_f"),
            pl.col("humidity").mean().alias("avg_humidity"),
            pl.col("wind_mph").mean().alias("avg_wind_mph"),
            pl.col("precip_total").sum().alias("total_precip_in")
        )
        .sort("date")
    )
    
    return daily_stats



def analyze_weather_data_lazy(days=7):
    conn = duckdb.connect(DB_PATH)
    
    # Execute query and convert to Polars DataFrame
    result = conn.execute(f"""
    SELECT * FROM weather_observations 
    WHERE observation_time >= CURRENT_DATE - {days}
    """).arrow()
    
    # Create lazy DataFrame
    df = pl.from_arrow(result).lazy()
    
    # Define operations
    daily_stats = (
        df.group_by(pl.col("observation_time").dt.date().alias("date"))
        .agg(
            pl.col("temp_f").mean().alias("avg_temp_f"),
            pl.col("temp_f").max().alias("max_temp_f"),
            pl.col("temp_f").min().alias("min_temp_f"),
            pl.col("humidity").mean().alias("avg_humidity"),
            pl.col("wind_mph").mean().alias("avg_wind_mph"),
            pl.col("precip_total").sum().alias("total_precip_in")
        )
        .sort("date")
    )
    
    # Execute when needed
    return daily_stats.collect()