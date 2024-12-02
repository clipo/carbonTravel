# Google Maps Distance Calculator

This Python script efficiently calculates distances and travel times between pairs of cities. It uses the Google Maps Distance Matrix API for most calculations and leverages the `geopy` library for flight distance estimations. The script supports various transportation modes (driving, transit, walking, bicycling, flight), handles inconsistent data formats, and includes robust error handling. Results are directly written to the input Excel file.

## Features:

* **Multi-Modal Distance Calculation:** Computes distances and durations for driving, transit, walking, and bicycling.
* **Approximate Flight Distance:** Estimates the straight-line (great-circle) distance between locations using the `geopy` library.  Prioritizes flight distance if multiple travel methods are specified.
* **Excel Input/Output:** Reads city pairs from an Excel file and directly updates the file with calculated distances.
* **Robust Error Handling:** Includes comprehensive error handling and retry mechanisms for API requests and file operations, including fallback locations for distance calculation failures.
* **Progress Indication:** Displays a progress bar during processing for larger datasets.
* **Secure API Key Management:** Uses environment variables for secure storage of the Google Maps API key.
* **Detailed Logging:** Provides informative logging for debugging and monitoring.
* **Command-Line Arguments:** Accepts an optional input file name via the command line.
* **Default Origin:** The script defaults to Binghamton, NY as the starting location if the 'Starting_City' field is blank or missing.


## Requirements:

* Python 3.7+
* `googlemaps` library: `pip install googlemaps`
* `pandas` library: `pip install pandas`
* `tqdm` library: `pip install tqdm`
* `geopy` library: `pip install geopy`
* `argparse` library: (included with Python 3.2+)
* `unittest-mock` library (for testing, optional): `pip install unittest-mock`


## Setup:

1. **Obtain a Google Maps API Key:**
    * Create a Google Cloud Platform (GCP) project.
    * Enable the Distance Matrix API and Geocoding API.
    * Create an API key and restrict it to these APIs (highly recommended for security).

2. **Set the API Key as an Environment Variable:** This is crucial for security; avoid hardcoding your API key.
    * **Linux/macOS:** `export GOOGLE_MAPS_API_KEY="YOUR_API_KEY"`
    * **Windows:** Add `GOOGLE_MAPS_API_KEY` as a system environment variable with your API key as the value.

3. **Install Dependencies:**
    ```bash
    pip install googlemaps pandas tqdm geopy
    ```

4. **Prepare Input Data:** Create an Excel file (e.g., `input_locations.xlsx`) with columns: `"trip_info_departure_city"`, `"trip_info_departure_state"`, `"trip_info_destination_city"`, `"trip_info_destination_state"`, `"trip_info_destination_country"`, and `"travel_info_methods_methods"`.

## Usage:

1. Place the Python script (`distance_calculator.py`) and the input Excel file in the same directory.
2. Run the script from your terminal, providing your API key:
   ```bash
   python distance_calculator.py your_api_key [-i input_file.xlsx]