import pandas as pd
import googlemaps
from datetime import datetime
import time


def initialize_gmaps_client(api_key):
    """
    Initialize the Google Maps client with the provided API key
    """
    try:
        return googlemaps.Client(key=api_key)
    except Exception as e:
        raise Exception(f"Failed to initialize Google Maps client: {str(e)}")


def calculate_distance(gmaps, origin, destination, mode):
    """
    Calculate distance between two points using specified mode of transportation
    Returns distance in kilometers and duration in hours
    """
    try:
        # Define valid transportation modes
        valid_modes = {
            'driving': 'car',
            'transit': 'public transport',
            'walking': 'walking',
            'bicycling': 'bicycle'
        }

        if mode not in valid_modes:
            return None, None

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
        return None, None

    except Exception as e:
        print(f"Error calculating {mode} distance from {origin} to {destination}: {str(e)}")
        return None, None


def calculate_flight_distance(gmaps, origin, destination):
    """
    Calculate direct flight distance using Google Maps geocoding and geometry
    Returns distance in kilometers
    """
    try:
        # Get coordinates for origin and destination
        origin_geocode = gmaps.geocode(origin)[0]['geometry']['location']
        dest_geocode = gmaps.geocode(destination)[0]['geometry']['location']

        # Calculate direct distance
        result = gmaps.distance_matrix(
            f"{origin_geocode['lat']},{origin_geocode['lng']}",
            f"{dest_geocode['lat']},{dest_geocode['lng']}",
            mode="driving",  # Using driving mode but will only use the straight-line distance
            units="metric"
        )

        if result['rows'][0]['elements'][0]['status'] == 'OK':
            # Get straight-line distance (approximate flight distance)
            distance = result['rows'][0]['elements'][0]['distance']['value'] / 1000
            return round(distance, 2)
        return None

    except Exception as e:
        print(f"Error calculating flight distance from {origin} to {destination}: {str(e)}")
        return None


def process_excel_file(input_file, output_file, api_key):
    """
    Process the input Excel file and generate output with distances
    """
    try:
        # Initialize Google Maps client
        gmaps = initialize_gmaps_client(api_key)

        # Read input Excel file
        df = pd.read_excel(input_file)

        # Initialize new columns for distances and durations
        transport_modes = {
            'driving': 'Car',
            'transit': 'Public_Transport',
            'walking': 'Walking',
            'bicycling': 'Bicycle'
        }

        # Add columns for each mode of transportation
        for mode in transport_modes.values():
            df[f'{mode}_Distance_km'] = None
            df[f'{mode}_Duration_hrs'] = None

        df['Flight_Distance_km'] = None

        # Process each row
        for index, row in df.iterrows():
            origin = row['Starting_City']
            destination = row['Destination']

            # Calculate distances for each mode of transportation
            for api_mode, column_prefix in transport_modes.items():
                distance, duration = calculate_distance(gmaps, origin, destination, api_mode)
                df.at[index, f'{column_prefix}_Distance_km'] = distance
                df.at[index, f'{column_prefix}_Duration_hrs'] = duration

                # Add delay to avoid hitting API rate limits
                time.sleep(0.1)

            # Calculate flight distance
            flight_distance = calculate_flight_distance(gmaps, origin, destination)
            df.at[index, 'Flight_Distance_km'] = flight_distance

            # Add delay to avoid hitting API rate limits
            time.sleep(0.1)

            print(f"Processed row {index + 1}/{len(df)}: {origin} to {destination}")

        # Save results to new Excel file
        df.to_excel(output_file, index=False)
        print(f"Results saved to {output_file}")

    except Exception as e:
        print(f"Error processing Excel file: {str(e)}")


def main():
    # Configuration
    API_KEY = 'PUT THE API KEY HERE'  # Replace with your actual API key
    INPUT_FILE = 'input_locations.xlsx'  # Replace with your input file name
    OUTPUT_FILE = 'distances_output.xlsx'  # Replace with desired output file name

    # Process the file
    process_excel_file(INPUT_FILE, OUTPUT_FILE, API_KEY)


if __name__ == "__main__":
    main()