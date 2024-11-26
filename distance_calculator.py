import pandas as pd
import googlemaps
from datetime import datetime
import time
import logging

# Configure logging for better error handling
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_gmaps_client(api_key):
    """Initializes the Google Maps client."""
    try:
        return googlemaps.Client(key=api_key)
    except Exception as e:
        logging.error(f"Failed to initialize Google Maps client: {e}")
        raise  # Re-raise the exception to be handled higher up

def calculate_distance(gmaps, origin, destination, mode):
    """Calculates distance and duration between two points."""
    try:
        valid_modes = ['driving', 'transit', 'walking', 'bicycling']
        if mode not in valid_modes:
            logging.warning(f"Invalid travel mode: {mode}. Skipping.")
            return None, None

        result = gmaps.distance_matrix(origin, destination, mode=mode, departure_time=datetime.now())

        element = result['rows'][0]['elements'][0]
        if element['status'] == 'OK':
            distance = element['distance']['value'] / 1000
            duration = element['duration']['value'] / 3600
            return round(distance, 2), round(duration, 2)
        else:
            logging.warning(f"Distance Matrix API returned status: {element['status']} for {origin} to {destination} ({mode}).")
            return None, None

    except Exception as e:
        logging.error(f"Error calculating {mode} distance from {origin} to {destination}: {e}")
        return None, None

def calculate_flight_distance(gmaps, origin, destination):
    """Calculates approximate flight distance using geocoding and distance matrix."""
    try:
        origin_geocode = gmaps.geocode(origin)
        dest_geocode = gmaps.geocode(destination)

        if not origin_geocode or not dest_geocode:
            logging.warning(f"Geocoding failed for {origin} or {destination}.")
            return None

        origin_coords = origin_geocode[0]['geometry']['location']
        dest_coords = dest_geocode[0]['geometry']['location']

        result = gmaps.distance_matrix(
            f"{origin_coords['lat']},{origin_coords['lng']}",
            f"{dest_coords['lat']},{dest_coords['lng']}",
            mode="driving", units="metric"
        )

        element = result['rows'][0]['elements'][0]
        if element['status'] == 'OK':
            distance = element['distance']['value'] / 1000
            return round(distance, 2)
        else:
            logging.warning(f"Distance Matrix API returned status: {element['status']} for flight distance between {origin} and {destination}.")
            return None

    except Exception as e:
        logging.error(f"Error calculating flight distance from {origin} to {destination}: {e}")
        return None

def process_excel_file(input_file, output_file, api_key):
    """Processes the input Excel file and generates output with distances."""
    try:
        gmaps = initialize_gmaps_client(api_key)
        df = pd.read_excel(input_file)

        transport_modes = {
            'driving': 'Car',
            'transit': 'Public_Transport',
            'walking': 'Walking',
            'bicycling': 'Bicycle'
        }

        for mode in transport_modes.values():
            df[f'{mode}_Distance_km'] = None
            df[f'{mode}_Duration_hrs'] = None
        df['Flight_Distance_km'] = None

        #More efficient iteration using apply
        def calculate_row_distances(row):
            origin = row['Starting_City']
            destination = row['Destination']
            for api_mode, column_prefix in transport_modes.items():
                distance, duration = calculate_distance(gmaps, origin, destination, api_mode)
                row[f'{column_prefix}_Distance_km'] = distance
                row[f'{column_prefix}_Duration_hrs'] = duration
            flight_distance = calculate_flight_distance(gmaps, origin, destination)
            row['Flight_Distance_km'] = flight_distance
            return row

        df = df.apply(calculate_row_distances, axis=1) #apply function row-wise


        df.to_excel(output_file, index=False)
        logging.info(f"Results saved to {output_file}")

    except Exception as e:
        logging.exception(f"Error processing Excel file: {e}") #Logs the full traceback


def main():
    #Configuration.  Consider using a config file or environment variables for better security
    API_KEY = 'API KEY GOES HERE'
    INPUT_FILE = 'input_locations.xlsx'
    OUTPUT_FILE = 'distances_output.xlsx'

    process_excel_file(INPUT_FILE, OUTPUT_FILE, API_KEY)

if __name__ == "__main__":
    main()