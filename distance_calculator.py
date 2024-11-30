import pandas as pd
import googlemaps
from datetime import datetime
import time
import logging
import os
from googlemaps.exceptions import ApiError
from tqdm import tqdm # Added for progress bar

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_gmaps_client(api_key):
    """
    Initialize the Google Maps client with the provided API key.  Includes validation.
    """
    if not api_key:
        raise ValueError("Google Maps API key is missing.")
    try:
        return googlemaps.Client(key=api_key)
    except Exception as e:
        raise Exception(f"Failed to initialize Google Maps client: {str(e)}")

def calculate_distance(gmaps, origin, destination, mode, max_retries=3, retry_delay=2):
    """
    Calculate distance between two points using specified mode of transportation.
    Includes retry mechanism for API errors.
    Returns distance in kilometers and duration in hours.
    """
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
            else:
                status = result['rows'][0]['elements'][0]['status']
                logging.warning(f"Distance Matrix API returned status {status} for {origin} to {destination} using {mode}. Retrying...")
                time.sleep(retry_delay)
                retries +=1

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
    """
    Calculate approximate flight distance using Google Maps geocoding and geometry.
    Includes retry mechanism for API errors.
    Returns distance in kilometers.
    """
    retries = 0
    while retries < max_retries:
        try:
            origin_geocode = gmaps.geocode(origin)[0]['geometry']['location']
            dest_geocode = gmaps.geocode(destination)[0]['geometry']['location']

            result = gmaps.distance_matrix(
                f"{origin_geocode['lat']},{origin_geocode['lng']}",
                f"{dest_geocode['lat']},{dest_geocode['lng']}",
                mode="driving",  # Using driving mode for straight-line distance
                units="metric"
            )

            if result['rows'][0]['elements'][0]['status'] == 'OK':
                distance = result['rows'][0]['elements'][0]['distance']['value'] / 1000
                return round(distance, 2)
            else:
                status = result['rows'][0]['elements'][0]['status']
                logging.warning(f"Distance Matrix API returned status {status} for {origin} to {destination} (flight). Retrying...")
                time.sleep(retry_delay)
                retries +=1
        except (IndexError, KeyError) as e:
            logging.error(f"Geocoding or distance matrix error for {origin} or {destination} (flight): {e}. Retrying...")
            time.sleep(retry_delay)
            retries += 1
        except ApiError as e:
            logging.error(f"API Error calculating flight distance from {origin} to {destination}: {str(e)}. Retrying...")
            time.sleep(retry_delay)
            retries += 1
        except Exception as e:
            logging.exception(f"Error calculating flight distance from {origin} to {destination}: {str(e)}")
            return None
    logging.error(f"Max retries exceeded for flight distance calculation from {origin} to {destination}")
    return None


def process_excel_file(input_file, output_file, api_key):
    """
    Process the input Excel file and generate output with distances.
    Includes progress bar and improved error handling.  Uses Binghamton, NY as default origin if Starting_City is blank.
    """
    try:
        gmaps = initialize_gmaps_client(api_key)
        df = pd.read_excel(input_file)
        required_cols = ['Starting_City', 'Destination']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"Input file must contain columns: {required_cols}")

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

        for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
            origin = row['Starting_City']
            destination = row['Destination']

            # Check for empty or NaN origin and use Binghamton as default
            if pd.isna(origin) or origin.strip() == "":
                origin = "Binghamton, NY"

            for api_mode, column_prefix in transport_modes.items():
                distance, duration = calculate_distance(gmaps, origin, destination, api_mode)
                df.at[index, f'{column_prefix}_Distance_km'] = distance
                df.at[index, f'{column_prefix}_Duration_hrs'] = duration

            flight_distance = calculate_flight_distance(gmaps, origin, destination)
            df.at[index, 'Flight_Distance_km'] = flight_distance

            print(f"Processed row {index + 1}/{len(df)}: {origin} to {destination}")

        df.to_excel(output_file, index=False)
        print(f"Results saved to {output_file}")

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

    INPUT_FILE = 'input_locations.xlsx'
    OUTPUT_FILE = 'distances_output.xlsx'

    try:
        process_excel_file(INPUT_FILE, OUTPUT_FILE, API_KEY)
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()