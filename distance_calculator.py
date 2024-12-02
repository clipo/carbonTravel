import pandas as pd
import googlemaps
from datetime import datetime
import time
import logging
import os
from googlemaps.exceptions import ApiError
from tqdm import tqdm
from geopy.distance import geodesic #Import geodesic function
from geopy.geocoders import Nominatim #Import Nominatim for geocoding


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_gmaps_client(api_key):
    """Initializes the Google Maps client with the provided API key. Includes validation."""
    if not api_key:
        raise ValueError("Google Maps API key is missing.")
    try:
        return googlemaps.Client(key=api_key)
    except Exception as e:
        raise Exception(f"Failed to initialize Google Maps client: {str(e)}")

def calculate_distance(gmaps, origin, destination, mode, max_retries=3, retry_delay=2):
    """Calculates distance between two points using specified mode. Includes retry mechanism."""
    retries = 0
    while retries < max_retries:
        try:
            result = gmaps.distance_matrix(
                origin,
                destination,
                mode=mode,
                departure_time=datetime.now()
            )

            if result['rows'][0]['elements'][0]['status'] == 'OK':
                distance = result['rows'][0]['elements'][0]['distance']['value'] / 1000  # Convert to km
                duration = result['rows'][0]['elements'][0]['duration']['value'] / 3600  # Convert to hours
                return round(distance, 2), round(duration, 2)
            elif result['rows'][0]['elements'][0]['status'] == 'ZERO_RESULTS':
                logging.warning(f"Distance Matrix API returned status ZERO_RESULTS for {origin} to {destination} using {mode}.")
                return None, None #Return None explicitly for ZERO_RESULTS
            else:
                status = result['rows'][0]['elements'][0]['status']
                logging.warning(f"Distance Matrix API returned status {status} for {origin} to {destination} using {mode}. Retrying...")
                time.sleep(retry_delay)
                retries += 1

        except ApiError as e:
            logging.error(f"API Error calculating {mode} distance from {origin} to {destination}: {str(e)}. Retrying...")
            time.sleep(retry_delay)
            retries += 1
        except Exception as e:
            logging.exception(f"Error calculating {mode} distance from {origin} to {destination}: {str(e)}")
            return None, None
    logging.error(f"Max retries exceeded for {origin} to {destination} using {mode}")
    return None, None

def calculate_flight_distance(gmaps, origin, destination, max_retries=3, retry_delay=2):
    """Calculates approximate flight distance using geopy's geodesic function."""
    geolocator = Nominatim(user_agent="flight_distance_calculator")

    retries = 0
    while retries < max_retries:
        try:
            origin_location = geolocator.geocode(origin)
            destination_location = geolocator.geocode(destination)

            if origin_location and destination_location:
                origin_coords = (origin_location.latitude, origin_location.longitude)
                destination_coords = (destination_location.latitude, destination_location.longitude)
                distance = geodesic(origin_coords, destination_coords).km
                return round(distance, 2)
            else:
                logging.warning(f"Geocoding failed for {origin} or {destination} (flight). Retrying...")
                time.sleep(retry_delay)
                retries += 1
        except Exception as e:
            logging.exception(f"Error calculating flight distance from {origin} to {destination}: {str(e)}. Retrying...")
            time.sleep(retry_delay)
            retries += 1
    logging.error(f"Max retries exceeded for flight distance calculation from {origin} to {destination}")
    return 0 # Return 0 as default if calculation fails


def process_excel_file(input_file, api_key):
    """Processes the input Excel file, adding distance data directly to the input file.
       Handles inconsistent travel method formatting, missing state data, country-specific state usage,
       prioritizes 'flight' for multiple modes, and retries with EWR/JFK for ZERO_RESULTS from non-US destinations.
       Uses geopy for flight distance calculation and ensures a distance value for every row."""
    try:
        gmaps = initialize_gmaps_client(api_key)
        df = pd.read_excel(input_file)

        required_cols = ['trip_info_departure_city', 'trip_info_departure_state', 'trip_info_departure_street_address',
                         'trip_info_destination_city', 'trip_info_destination_state', 'trip_info_destination_country',
                         'trip_info_destination_street_address', 'travel_info_methods_methods']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"Input file must contain columns: {required_cols}")

        car_synonyms = ["rental car", "personal car", "car"]
        flight_synonyms = ["plane", "flight", "airplane"]

        distance_column_name = 'Calculated_Distance_km'
        if distance_column_name not in df.columns:
            df[distance_column_name] = None

        for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
            origin_city = str(row['trip_info_departure_city']).strip()
            origin_state = str(row['trip_info_departure_state']).strip()
            destination_city = str(row['trip_info_destination_city']).strip()
            destination_state = str(row['trip_info_destination_state']).strip()
            destination_country = str(row['trip_info_destination_country']).strip()
            travel_methods_raw = str(row['travel_info_methods_methods']).strip()

            origin = origin_city
            if origin_state and origin_state.strip():
                origin = f"{origin_city}, {origin_state}"

            destination = destination_city
            if destination_country.lower() == "united states" and destination_state and destination_state.strip():
                destination = f"{destination_city}, {destination_state}"
            elif destination_country and destination_country.strip():
                destination = f"{destination_city}, {destination_country}"

            if pd.isna(origin) or origin.strip() == "":
                origin = "Binghamton, NY"
            if pd.isna(destination) or destination.strip() == "":
                logging.warning(f"Skipping row {index + 1} due to missing destination.")
                continue

            if pd.isna(travel_methods_raw) or travel_methods_raw.strip() == "":
                logging.warning(f"Skipping row {index + 1} due to missing travel method.")
                continue

            travel_methods = travel_methods_raw.lower()
            travel_modes = [item.strip() for item in travel_methods.split(',') if item.strip()]

            #print(f"Row {index+1}: travel_methods_raw = '{travel_methods_raw}', travel_methods = '{travel_methods}', travel_modes = {travel_modes}")

            selected_mode = None
            if len(travel_modes) > 0:
                if len(travel_modes) > 1 and any("plane" in mode or "flight" in mode or "airplane" in mode for mode in travel_modes):
                    selected_mode = 'flight'
                elif len(travel_modes) == 1:
                    last_mode = travel_modes[0]
                    if any(mode in last_mode for mode in car_synonyms):
                        selected_mode = 'driving'
                    elif any(mode in last_mode for mode in ['public transport', 'bus', 'train', 'subway']):
                        selected_mode = 'transit'
                    elif 'walking' in last_mode:
                        selected_mode = 'walking'
                    elif 'bicycling' in last_mode:
                        selected_mode = 'bicycling'
                    elif any(mode in last_mode for mode in flight_synonyms):
                        selected_mode = 'flight'
                    else:
                        logging.warning(f"Unsupported travel method in row {index + 1}: {travel_methods}")
                else:
                    logging.warning(f"Skipping row {index+1} due to multiple travel modes and no 'plane', 'flight' or 'airplane' specified")

                if selected_mode:
                    if selected_mode == 'flight':
                        distance = calculate_flight_distance(gmaps, origin, destination)
                    else:
                        distance, _ = calculate_distance(gmaps, origin, destination, selected_mode)
                        if distance is None and destination_country.lower() != "united states":
                            new_origins = ["EWR Airport, Newark, NJ", "JFK Airport, New York, NY"]
                            for new_origin in new_origins:
                                distance = calculate_flight_distance(gmaps, new_origin, destination)
                                if distance is not None:
                                    logging.info(f"Successfully calculated flight distance from {new_origin} to {destination}")
                                    break
                            else:
                                logging.warning(f"Could not calculate flight distance from EWR or JFK to {destination}")
                                distance = 0  # Default distance if calculation fails

                    df.at[index, distance_column_name] = distance

            else:
                logging.warning(f"Skipping row {index + 1} due to empty travel method.")

            #print(f"Processed row {index + 1}/{len(df)}: {origin} to {destination} by {selected_mode}")

        df.to_excel(input_file, index=False)
        print(f"Results updated in {input_file}")

    except FileNotFoundError:
        logging.error(f"Input file not found: {input_file}")
        raise
    except Exception as e:
        logging.exception(f"Error processing Excel file: {str(e)}")
        raise


def main():
    """Main function to run the distance calculation."""
    API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    if not API_KEY:
        logging.error("GOOGLE_MAPS_API_KEY environment variable not set.")
        return

    INPUT_FILE = 'input_locations.xlsx'  # Replace with your input file name

    try:
        process_excel_file(INPUT_FILE, API_KEY)
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()