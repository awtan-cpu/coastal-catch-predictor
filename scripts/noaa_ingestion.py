# Importing necessary libraries for HTTP requests and timezone-aware dates
import requests
from datetime import datetime, timedelta, timezone

# Setting up a generic function to retrieve various NOAA data products
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
        
        # Parsing the JSON payload from the response
        data = response.json()

        # Verifying the presence of the data or predictions array in the payload
        if 'data' in data:
            return data['data']
        elif 'predictions' in data: # Tides return as 'predictions' instead of 'data'
            return data['predictions']
        else:
            # Printing an error message if the API returns an unexpected structure
            print(f"Encountering an API error for {product}: {data.get('error', 'Unknown error')}")
            return None
    else:
        # Printing a connection error for failed HTTP requests
        print(f"Failing to connect for {product}, status code: {response.status_code}")
        return None

# Executing the script logic when run directly
if __name__ == "__main__":
    
    # Defining the target Galveston Pleasure Pier station ID
    GALVESTON_STATION = "8771341"

    # Calculating the date range using the modern, timezone-aware method (fixes deprecation warning)
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=1)
    
    # Formatting dates to YYYYMMDD strings as required by the NOAA API
    begin_str = start_time.strftime("%Y%m%d")
    end_str = end_time.strftime("%Y%m%d")

    print(f"Pulling environmental data from {begin_str} to {end_str}...\n")

    # 1. Fetching Water Temperature
    print("--- Fetching Water Temperature ---")
    temp_data = fetch_noaa_data(GALVESTON_STATION, begin_str, end_str, "water_temperature")
    if temp_data:
        print(f"Success! First record: Time {temp_data[0]['t']} | Temp {temp_data[0]['v']} °F")

    # 2. Fetching Barometric Pressure
    print("\n--- Fetching Barometric Pressure ---")
    pressure_data = fetch_noaa_data(GALVESTON_STATION, begin_str, end_str, "air_pressure")
    if pressure_data:
        print(f"Success! First record: Time {pressure_data[0]['t']} | Pressure {pressure_data[0]['v']} mb")

    # 3. Fetching Tide Predictions (requires MLLW datum)
    print("\n--- Fetching Tide Predictions ---")
    tide_data = fetch_noaa_data(GALVESTON_STATION, begin_str, end_str, "predictions", datum="MLLW")
    if tide_data:
        print(f"Success! First record: Time {tide_data[0]['t']} | Level {tide_data[0]['v']} ft")