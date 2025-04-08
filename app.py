# app.py

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import duckdb
import os
from datetime import datetime, timedelta
from config import DB_PATH

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

def get_db_connection():
    """Get a connection to the DuckDB database"""

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Databise file not found: {DB_PATH}")
    
    return duckdb.connect(DB_PATH)

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('static', 'index.html')


@app.route('/api/stations', methods=['GET'])
def get_stations():
    """Get list of all stations in the database"""
    try:
        conn = get_db_connection()
        query = """
        SELECT DISTINCT 
            station_id,
            neighborhood,
            latitude,
            longitude,
            MAX(observation_time) as last_observation
        FROM weather_observations
        GROUP BY station_id, neighborhood, latitude, longitude
        ORDER BY station_id
        """
        
        result = conn.execute(query).fetchall()
        
        # Convert to list of dictionaries
        columns = ["station_id", "neighborhood", "latitude", "longitude", "last_observation"]
        stations = []
        for row in result:
            stations.append(dict(zip(columns, row)))
            
        conn.close()
        return jsonify({
            "stations": stations,
            "count": len(stations),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/api/health', methods = ['GET'])
def health_check():
    """Simple health check endpoint"""
    try:
        conn = get_db_connection()
        result = conn.execute("SELECT 'OK' as status").fetchone()[0]
        conn.close()
        return jsonify({
            "status": result,
            "timestamp": datetime.now().isoformat(),
            "database": DB_PATH
        })
    except Exception as e:
        return jsonify ({
            "status": "ERROR",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500
    
@app.route('/api/recent', methods = ['GET'])
def get_recent_data():
    """Get recent weather observations"""
    try:
        limit = int(request.args.get('limit', 10))
        station_id = request.args.get('station_id')

        conn = get_db_connection()
        query = """
        SELECT
            observation_time,
            station_id,
            neighborhood,
            temp_f,
            humidity,
            wind_mph,
            pressure_hg
            precip_today_in,
            collection_time
        FROM weather_observations
        """

        params = []
        if station_id:
            query += " WHERE station_id = ?"
            params.append(station_id)

        query += """
        ORDER BY observation_time DESC
        LIMIT ?
        """

        params.append(limit)

        result = conn.execute(query, params).fetchall()

        columns = ["observation_time", "station_id", "neighborhood", "temp_f", "humidity", "wind_mph", "pressure_hg", "precip_today_in", "collection_time"]

        data = []
        for row in result:
            data.append(dict(zip(columns, row)))

        conn.close()

        return jsonify({
            "data": data,
            "count": len(data),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500
    

@app.route('/api/summary', methods=['GET'])
def get_summary():
    """Get summary statistics for a time period"""
    try:
        # Get days parameter (default to 7)
        days = int(request.args.get('days', 7))
        
        # Get optional station_id parameter
        station_id = request.args.get('station_id')
        
        conn = get_db_connection()
        
        # Build the WHERE clause
        where_clause = "WHERE observation_time >= ?"
        params = [datetime.now() - timedelta(days=days)]
        
        if station_id:
            where_clause += " AND station_id = ?"
            params.append(station_id)
            
        query = f"""
        SELECT 
            AVG(temp_f) as avg_temp,
            MIN(temp_f) as min_temp,
            MAX(temp_f) as max_temp,
            AVG(humidity) as avg_humidity,
            AVG(wind_mph) as avg_wind,
            MAX(wind_gust_mph) as max_wind_gust,
            MAX(precip_today_in) as max_precip,
            COUNT(DISTINCT CAST(observation_time AS DATE)) as days_covered
        FROM weather_observations
        {where_clause}
        """
        
        result = conn.execute(query, params).fetchone()
        
        # Convert to dictionary
        columns = ["avg_temp", "min_temp", "max_temp", "avg_humidity", 
                  "avg_wind", "max_wind_gust", "max_precip", "days_covered"]
        summary = dict(zip(columns, result))
        
        # Add query parameters to response
        summary["period_days"] = days
        summary["station_id"] = station_id if station_id else "all"
            
        conn.close()
        return jsonify({
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500



@app.route('/api/custom', methods=['POST'])
def custom_query():
    """Run a custom query with parameters (with some safety restrictions)"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data or "query" not in data:
            return jsonify({
                "status": "ERROR",
                "error": "Missing required 'query' field"
            }), 400
            
        query = data["query"]
        params = data.get("params", [])
        
        # Basic security check - only allow SELECT queries
        if not query.strip().upper().startswith("SELECT"):
            return jsonify({
                "status": "ERROR",
                "error": "Only SELECT queries are allowed"
            }), 403
            
        conn = get_db_connection()
        result = conn.execute(query, params).fetchall()
        
        # Get column names
        column_names = [desc[0] for desc in conn.description]
        
        # Convert results to list of dictionaries
        rows = []
        for row in result:
            rows.append(dict(zip(column_names, row)))
            
        conn.close()
        return jsonify({
            "data": rows,
            "count": len(rows),
            "columns": column_names,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500
    


if __name__ == "__main__":
    # check for static folder
    if not os.path.exists('static'):
        os.makedirs('static')

    # Run the Flask app on your local network
    app.run(host = '192.168.68.71', port = 5000, debug=False)