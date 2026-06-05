# Importing required libraries for API requests, dates, database connections, and secure variables
import requests
from datetime import datetime, timedelta, timezone
import psycopg2
import os
from dotenv import load_dotenv

# Loading the hidden credentials from our .env file into Python's memory
load_dotenv()

# Setting up the generic function to retrieve various NOAA data products
def fetch_noaa_data(station_id, begin_date, end_date, product, datum="STND"):
    
    # Defining the base CO-OPS API endpoint URL
    base_url = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    
    # Building the payload dictionary dynamically based on the requested product
    params = {
        'station': station_id,
        'begin_date': begin_date,
        'end_date': end_date,
        'product': product,
        'datum': datum, 
        'units': 'english',
        'time_zone': 'gmt',
        'format': 'json',
        'application': 'Coastal_Catch_Predictor'
    }

    # Executing the GET request to the NOAA server
    response = requests.get(base_url, params=params)

    # Checking for a successful HTTP response code
    if response.status_code == 200:
        data = response.json()
        if 'data' in data:
            return data['data']
        elif 'predictions' in data: 
            return data['predictions']
        else:
            return None
    else:
        return None

# Setting up the function to push environmental weather data to PostgreSQL
def save_environmental_data(temp_data, pressure_data):
    
    # Connecting to the PostgreSQL database using our .env variables
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", "5432")
    )
    
    # Opening a cursor to execute SQL commands
    cursor = conn.cursor()

    # Processing and saving temperature records
    if temp_data:
        print("Saving water temperature records to database...")
        for record in temp_data:
            # Executing an UPSERT command to insert or update the row
            cursor.execute("""
                INSERT INTO environmental_conditions (reading_time, water_temperature_f)
                VALUES (%s, %s)
                ON CONFLICT (reading_time) 
                DO UPDATE SET water_temperature_f = EXCLUDED.water_temperature_f;
            """, (record['t'], record['v']))

    # Processing and saving barometric pressure records
    if pressure_data:
        print("Saving barometric pressure records to database...")
        for record in pressure_data:
            # Executing an UPSERT command to merge pressure into the existing timestamp row
            cursor.execute("""
                INSERT INTO environmental_conditions (reading_time, barometric_pressure_mb)
                VALUES (%s, %s)
                ON CONFLICT (reading_time) 
                DO UPDATE SET barometric_pressure_mb = EXCLUDED.barometric_pressure_mb;
            """, (record['t'], record['v']))

    # Committing the changes permanently to the database
    conn.commit()
    
    # Closing the cursor and connection safely
    cursor.close()
    conn.close()

# Setting up the function to push tide prediction data to PostgreSQL
def save_tide_data(tide_data):
    
    # Connecting to the PostgreSQL database
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", "5432")
    )
    cursor = conn.cursor()

    if tide_data:
        print("Saving tide predictions to database...")
        for record in tide_data:
            # Executing an UPSERT for tide levels
            cursor.execute("""
                INSERT INTO tide_predictions (prediction_time, water_level_ft)
                VALUES (%s, %s)
                ON CONFLICT (prediction_time) 
                DO UPDATE SET water_level_ft = EXCLUDED.water_level_ft;
            """, (record['t'], record['v']))

    # Committing and closing
    conn.commit()
    cursor.close()
    conn.close()

# Executing the script logic when run directly
if __name__ == "__main__":
    
    GALVESTON_STATION = "8771341"
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=1)
    
    begin_str = start_time.strftime("%Y%m%d")
    end_str = end_time.strftime("%Y%m%d")

    print(f"Pulling environmental data from {begin_str} to {end_str}...\n")

    # 1. Fetching the raw data from NOAA
    temp_data = fetch_noaa_data(GALVESTON_STATION, begin_str, end_str, "water_temperature")
    pressure_data = fetch_noaa_data(GALVESTON_STATION, begin_str, end_str, "air_pressure")
    tide_data = fetch_noaa_data(GALVESTON_STATION, begin_str, end_str, "predictions", datum="MLLW")

    # 2. Pushing the data into PostgreSQL
    save_environmental_data(temp_data, pressure_data)
    save_tide_data(tide_data)
    
    print("\nData pipeline execution completing successfully!")