import unittest
from unittest.mock import Mock, patch
import pandas as pd
from datetime import datetime
import json
import os
import logging

# Import the main script (assuming it's named distance_calculator.py)
from distance_calculator import (
    initialize_gmaps_client,
    calculate_distance,
    calculate_flight_distance,
    process_excel_file
)

# Configure logging for tests (optional, but helpful)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TestDistanceCalculator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures that will be used for all tests"""
        # Sample API response for distance matrix (OK status)
        cls.sample_distance_response_ok = {
            'rows': [{
                'elements': [{
                    'status': 'OK',
                    'distance': {'value': 50000, 'text': '50 km'},
                    'duration': {'value': 3600, 'text': '1 hour'}
                }]
            }]
        }

        # Sample API response for distance matrix (failed status)
        cls.sample_distance_response_failed = {
            'rows': [{
                'elements': [{
                    'status': 'ZERO_RESULTS'
                }]
            }]
        }

        # Sample API response for distance matrix (other error status)
        cls.sample_distance_response_other_error = {
            'rows': [{
                'elements': [{
                    'status': 'INVALID_REQUEST'
                }]
            }]
        }

        # Sample geocoding response
        cls.sample_geocode_response = [{
            'geometry': {
                'location': {
                    'lat': 40.7128,
                    'lng': -74.0060
                }
            }
        }]

        # Sample geocoding response with error
        cls.sample_geocode_response_error = []

    def setUp(self):
        """Set up test fixtures before each test"""
        self.api_key = 'test_api_key'
        self.test_data = pd.DataFrame({
            'Starting_City': ['New York', 'London'],
            'Destination': ['Boston', 'Paris']
        })
        self.test_input_file = 'test_input.xlsx'
        self.test_output_file = 'test_output.xlsx'
        self.test_data.to_excel(self.test_input_file, index=False)

    def tearDown(self):
        """Clean up test fixtures after each test"""
        if os.path.exists(self.test_input_file):
            os.remove(self.test_input_file)
        if os.path.exists(self.test_output_file):
            os.remove(self.test_output_file)

    @patch('googlemaps.Client')
    def test_initialize_gmaps_client(self, mock_client):
        """Test Google Maps client initialization"""
        client = initialize_gmaps_client(self.api_key)
        mock_client.assert_called_once_with(key=self.api_key)

        mock_client.side_effect = Exception('API Key Error')
        with self.assertRaises(Exception) as context:
            initialize_gmaps_client('invalid_key')
        self.assertTrue('Failed to initialize Google Maps client' in str(context.exception))

    @patch('googlemaps.Client')
    def test_calculate_distance(self, mock_client):
        """Test distance calculation for different modes"""
        mock_gmaps = Mock()

        # Test OK response
        mock_gmaps.distance_matrix.return_value = self.sample_distance_response_ok
        for mode in ['driving', 'transit', 'walking', 'bicycling']:
            distance, duration = calculate_distance(mock_gmaps, 'New York', 'Boston', mode)
            self.assertEqual(distance, 50.0)
            self.assertEqual(duration, 1.0)

        # Test invalid mode
        distance, duration = calculate_distance(mock_gmaps, 'New York', 'Boston', 'invalid_mode')
        self.assertIsNone(distance)
        self.assertIsNone(duration)

        # Test failed route
        mock_gmaps.distance_matrix.return_value = self.sample_distance_response_failed
        distance, duration = calculate_distance(mock_gmaps, 'New York', 'Tokyo', 'driving')
        self.assertIsNone(distance)
        self.assertIsNone(duration)

        # Test other error status
        mock_gmaps.distance_matrix.return_value = self.sample_distance_response_other_error
        distance, duration = calculate_distance(mock_gmaps, 'New York', 'Tokyo', 'driving')
        self.assertIsNone(distance)
        self.assertIsNone(duration)

    @patch('googlemaps.Client')
    def test_calculate_flight_distance(self, mock_client):
        """Test flight distance calculation"""
        mock_gmaps = Mock()
        mock_gmaps.geocode.return_value = self.sample_geocode_response
        mock_gmaps.distance_matrix.return_value = self.sample_distance_response_ok

        distance = calculate_flight_distance(mock_gmaps, 'New York', 'London')
        self.assertEqual(distance, 50.0)

        mock_gmaps.geocode.side_effect = Exception('Geocoding Error')
        distance = calculate_flight_distance(mock_gmaps, 'Invalid City', 'London')
        self.assertIsNone(distance)

        mock_gmaps.geocode.return_value = self.sample_geocode_response_error
        distance = calculate_flight_distance(mock_gmaps, 'Invalid City', 'London')
        self.assertIsNone(distance)

    @patch('googlemaps.Client')
    def test_process_excel_file(self, mock_client):
        """Test Excel file processing"""
        mock_gmaps = Mock()
        mock_gmaps.distance_matrix.return_value = self.sample_distance_response_ok
        mock_gmaps.geocode.return_value = self.sample_geocode_response
        mock_client.return_value = mock_gmaps

        process_excel_file(self.test_input_file, self.test_output_file, self.api_key)
        self.assertTrue(os.path.exists(self.test_output_file))
        output_df = pd.read_excel(self.test_output_file)

        expected_columns = [
            'Starting_City', 'Destination',
            'Car_Distance_km', 'Car_Duration_hrs',
            'Public_Transport_Distance_km', 'Public_Transport_Duration_hrs',
            'Walking_Distance_km', 'Walking_Duration_hrs',
            'Bicycle_Distance_km', 'Bicycle_Duration_hrs',
            'Flight_Distance_km'
        ]
        for column in expected_columns:
            self.assertIn(column, output_df.columns)

        with self.assertRaises(FileNotFoundError) as context:
            process_excel_file('invalid_file.xlsx', self.test_output_file, self.api_key)
        self.assertTrue('Input file not found' in str(context.exception))

    @patch('distance_calculator.calculate_distance')
    @patch('distance_calculator.calculate_flight_distance')
    @patch('pandas.read_excel')
    def test_process_excel_file_with_exceptions(self, mock_read_excel, mock_calculate_flight_distance,
                                                mock_calculate_distance):
        # Simulate exceptions in calculate_distance and calculate_flight_distance
        mock_calculate_distance.side_effect = Exception("Distance Calculation Error")
        mock_calculate_flight_distance.side_effect = Exception("Flight Distance Calculation Error")

        with self.assertRaises(Exception) as context:
            process_excel_file(self.test_input_file, self.test_output_file, self.api_key)
        self.assertTrue("Error processing Excel file" in str(context.exception))

        mock_calculate_distance.side_effect = None
        mock_calculate_flight_distance.side_effect = None


class TestDistanceCalculatorIntegration(unittest.TestCase):
    """Integration tests (these will actually call the Google Maps API - Requires API key and network access)"""
    # These tests are commented out as they require a valid API key and network connection.  Uncomment and replace with your API key to run these tests

    # @unittest.skipUnless(os.environ.get('GOOGLE_MAPS_API_KEY'), "GOOGLE_MAPS_API_KEY environment variable not set")
    # def test_end_to_end_processing(self):
    #     """Test end-to-end processing with real data (requires API key)"""
    #     test_data = pd.DataFrame({
    #         'Starting_City': ['New York', 'London', 'Tokyo'],
    #         'Destination': ['Boston', 'Paris', 'Kyoto']
    #     })
    #     input_file = 'integration_test_input.xlsx'
    #     output_file = 'integration_test_output.xlsx'
    #     test_data.to_excel(input_file, index=False)
    #
    #     try:
    #         process_excel_file(input_file, output_file, os.environ['GOOGLE_MAPS_API_KEY'])
    #         result_df = pd.read_excel(output_file)
    #         self.assertEqual(len(result_df), 3)
    #         distance_columns = [col for col in result_df.columns if 'Distance' in col]
    #         for col in distance_columns:
    #             self.assertFalse(result_df[col].isnull().all())
    #     finally:
    #         if os.path.exists(input_file):
    #             os.remove(input_file)
    #         if os.path.exists(output_file):
    #             os.remove(output_file)


def run_tests():
    """Run all tests with detailed output"""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    run_tests()