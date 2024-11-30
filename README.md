# Google Maps Distance Calculator

This Python script efficiently calculates distances and travel times between pairs of cities using the Google Maps Distance Matrix API. It supports various transportation modes (driving, transit, walking, bicycling) and provides an approximate flight distance. Results are neatly organized and saved to an Excel file. The project includes a comprehensive unit test suite for enhanced reliability.

## Features:

* **Multi-Modal Distance Calculation:** Computes distances and durations for driving, transit, walking, and bicycling.
* **Approximate Flight Distance:** Estimates the straight-line (great-circle) distance between locations.
* **Excel Input/Output:** Reads city pairs from an Excel file and writes results to another Excel file.
* **Robust Error Handling:** Includes comprehensive error handling and retry mechanisms for API requests and file operations.
* **Progress Indication:** Displays a progress bar during processing for larger datasets.
* **Secure API Key Management:** Uses environment variables for secure storage of the Google Maps API key.
* **Detailed Logging:** Provides informative logging for debugging and monitoring.
* **Comprehensive Unit Testing:** A robust unit test suite ensures code quality and reliability.
* **Default Origin:**  The script now defaults to Binghamton, NY as the starting location if the 'Starting_City' field in the input Excel file is blank or missing.


## Requirements:

* Python 3.7+
* `googlemaps` library: `pip install googlemaps`
* `pandas` library: `pip install pandas`
* `tqdm` library: `pip install tqdm`
* `unittest-mock` library (for testing): `pip install unittest-mock`


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
    pip install googlemaps pandas tqdm unittest-mock
    ```

4. **Prepare Input Data:** Create an Excel file (e.g., `input_locations.xlsx`) with at least two columns: `"Starting_City"` and `"Destination"`. Each row represents a city pair.  Leaving the `"Starting_City"` column blank will use Binghamton, NY as the origin.

## Usage:

1. Place the Python script (`distance_calculator.py`), the input Excel file, and the test file (`test_distance_calculator.py` - if you have tests) in the same directory.
2. Run the script from your terminal: `python distance_calculator.py`
3. The results will be saved to `distances_output.xlsx`.

## Running Unit Tests:

To run the unit tests (if you've created them in `test_distance_calculator.py`), execute the following command in your terminal:

```bash
python -m unittest test_distance_calculator.py