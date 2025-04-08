# adhoc.py

import duckdb
from datetime import datetime, timedelta
import polars as pl
from config import DB_PATH

conn = duckdb.connect(DB_PATH)

query = """
    SELECT *
    FROM weather_observations
    ORDER BY station_id, observation_time DESC
"""

result = conn.execute(query).pl()

result = pl.DataFrame(result)

print(result)