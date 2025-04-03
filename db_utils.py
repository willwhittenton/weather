# db_utls.py

import duckdb
import polars as pl
import os
from datetime import datetime

def initialize_db(db_path="weather_data.duckdb"):
    """initialize the DuckDB database with the required schema"""
    conn = duckdb.connect(db_path)

    # Create weather_observations table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS weather_observations (
            observation_time TIMESTAMP,
            temp_f FLOAT,
            temp_c FLOAT,
            relative_humidity FLOAT,
            wind_dir STRING,
            wind_degrees INT,
            wind_mph FLOAT,
            wind_gust_mph FLOAT,
            pressure_mb FLOAT,
            precip_1hr_in FLOAT,
            precip_today_in FLOAT,
            uv FLOAT,
            solar_radiation fLOAT,
            collected_at TIMESTAMP
            )
    """
    )

    return conn

def save_weather_data(data, conn=None):
    """Save weather data to DuckDB using Polars"""
    if conn is None:
        conn = initialize_db()

    # Convert the data to a Polars DF
    df = pl.DataFrame([data])

    # Add collection timestamp
    df = df.with_columns(pl.lit(datetime.now()).alias("collected_at"))

    # Insert data into the table using DuckDB's from_arrow apability
    conn.execute("Insert INTO weather_observations SELECT * from df")
    conn.commit()

    return True

