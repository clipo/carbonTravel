# Distance Calculator with Google Maps API

A Python tool that calculates distances between cities using various modes of transportation via the Google Maps API. This tool takes an Excel spreadsheet containing origin and destination cities and outputs distances and durations for different transport modes including driving, public transport, walking, cycling, and flight distances.

## Features

- Calculates distances for multiple transportation modes:
  - Driving (car)
  - Public Transport
  - Walking
  - Cycling
  - Flight (straight-line distance)
- Handles international and domestic routes
- Provides both distance and duration for each mode
- Automatically marks unavailable routes with NA
- Includes rate limiting to prevent API quota issues
- Comprehensive error handling
- Includes test data generator
- Complete test suite with unit and integration tests

## Prerequisites

- Python 3.7 or higher
- Google Maps API key
- Required Python packages (see Installation section)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/distance-calculator.git
cd distance-calculator
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up your Google Maps API key:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Distance Matrix API and Geocoding API
   - Create API credentials
   - Replace `YOUR_GOOGLE_MAPS_API_KEY` in the script with your actual API key

## Usage

### Basic Usage

1. Prepare your input Excel file with these columns:
   - `Starting_City`
   - `Destination`

2. Run the script:
```bash
python distance_calculator.py
```

### Generate Test Data

To create sample data for testing:
```bash
python test_data_generator.py
```

### Run Tests

To run the test suite:
```bash
python test_distance_calculator.py
```

## Input Format

The input Excel file should have the following format:

| Starting_City | Destination |
|--------------|-------------|
| New York, NY | Boston, MA  |
| London, UK   | Paris, FR   |

## Output Format

The script will generate an Excel file with the following columns:

| Column Name | Description |
|------------|-------------|
| Starting_City | Original starting location |
| Destination | Original destination location |
| Car_Distance_km | Driving distance in kilometers |
| Car_Duration_hrs | Driving duration in hours |
| Public_Transport_Distance_km | Public transport distance in kilometers |
| Public_Transport_Duration_hrs | Public transport duration in hours |
| Walking_Distance_km | Walking distance in kilometers |
| Walking_Duration_hrs | Walking duration in hours |
| Bicycle_Distance_km | Cycling distance in kilometers |
| Bicycle_Duration_hrs | Cycling duration in hours |
| Flight_Distance_km | Direct flight distance in kilometers |

## File Structure

```
distance-calculator/
├── README.md
├── requirements.txt
├── distance_calculator.py
├── test_data_generator.py
├── test_distance_calculator.py
├── input_locations.xlsx
└── distances_output.xlsx
```

## API Rate Limits and Pricing

- The script includes built-in delays to respect Google Maps API rate limits
- Be aware of Google Maps API pricing:
  - Distance Matrix API has usage-based pricing
  - Geocoding API has separate pricing
  - Check current pricing on [Google Maps Platform Pricing](https://cloud.google.com/maps-platform/pricing)

## Error Handling

The script handles various error cases:
- Invalid API key
- Non-existent locations
- Network errors
- Invalid transport modes
- Missing input file
- Malformed input data

## Testing

The test suite includes:
- Unit tests for all major functions
- Integration tests for end-to-end workflow
- Mock objects for API calls
- Test data generation
- Automated cleanup

### Running Specific Tests

To run a specific test case:
```bash
python -m unittest test_distance_calculator.TestDistanceCalculator.test_calculate_distance
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Maps Platform for providing the APIs
- Contributors and testers
- Python community for excellent libraries

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.