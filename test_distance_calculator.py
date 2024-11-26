import unittest
from unittest.mock import Mock, patch
import pandas as pd
from datetime import datetime
import json
import os

# Import the main script (assuming it's named distance_calculator.py)
from distance_calculator import (
    initialize_gmaps_client,
    calculate_distance,
    calculate_flight_distance,
    process_excel_file
)


class TestDistanceCalculator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures that will be used for all tests"""
        # Sample API response for distance matrix
        cls.sample_distance_response = {
            'rows': [{
                'elements': [{
                    'status': 'OK',
                    'distance': {'value': 50000, 'text': '50 km'},
                    'duration': {'value': 3600, 'text': '1 hour'}
                }]
            }]
        }

        # Sample API response for failed route
        cls.failed_distance_response = {
            'rows': [{
                'elements': [{
                    'status': 'ZERO_RESULTS'
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

    def setUp(self):
        """Set up test fixtures before each test"""
        # Create a mock API key
        self.api_key = 'test_api_key'

        # Create sample test data
        self.test_data = pd.DataFrame({
            'Starting_City': ['New York', 'London'],
            'Destination': ['Boston', 'Paris']
        })

        # Save test data to temporary Excel file
        self.test_input_file = 'test_input.xlsx'
        self.test_output_file = 'test_output.xlsx'
        self.test_data.to_excel(self.test_input_file, index=False)

    def tearDown(self):
        """Clean up test fixtures after each test"""
        # Remove temporary files
        if os.path.exists(self.test_input_file):
            os.remove(self.test_input_file)
        if os.path.exists(self.test_output_file):
            os.remove(self.test_output_file)

    @patch('googlemaps.Client')
    def test_initialize_gmaps_client(self, mock_client):
        """Test Google Maps client initialization"""
        # Test successful initialization
        client = initialize_gmaps_client(self.api_key)
        mock_client.assert_called_once_with(key=self.api_key)

        # Test failed initialization
        mock_client.side_effect = Exception('API Key Error')
        with self.assertRaises(Exception):
            initialize_gmaps_client('invalid_key')

    @patch('googlemaps.Client')
    def test_calculate_distance(self, mock_client):
        """Test distance calculation for different modes"""
        mock_gmaps = Mock()
        mock_gmaps.distance_matrix.return_value = self.sample_distance_response

        # Test successful distance calculation
        for mode in ['driving', 'transit', 'walking', 'bicycling']:
            distance, duration = calculate_distance(
                mock_gmaps,
                'New York',
                'Boston',
                mode
            )
            self.assertEqual(distance, 50.0)  # 50000m converted to km
            self.assertEqual(duration, 1.0)  # 3600s converted to hours

        # Test invalid mode
        distance, duration = calculate_distance(
            mock_gmaps,
            'New York',
            'Boston',
            'invalid_mode'
        )
        self.assertIsNone(distance)
        self.assertIsNone(duration)

        # Test failed route
        mock_gmaps.distance_matrix.return_value = self.failed_distance_response
        distance, duration = calculate_distance(
            mock_gmaps,
            'New York',
            'Tokyo',
            'driving'
        )
        self.assertIsNone(distance)
        self.assertIsNone(duration)

    @patch('googlemaps.Client')
    def test_calculate_flight_distance(self, mock_client):
        """Test flight distance calculation"""
        mock_gmaps = Mock()
        mock_gmaps.geocode.return_value = self.sample_geocode_response
        mock_gmaps.distance_matrix.return_value = self.sample_distance_response

        # Test successful flight distance calculation
        distance = calculate_flight_distance(
            mock_gmaps,
            'New York',
            'London'
        )
        self.assertEqual(distance, 50.0)

        # Test failed geocoding
        mock_gmaps.geocode.side_effect = Exception('Geocoding Error')
        distance = calculate_flight_distance(
            mock_gmaps,
            'Invalid City',
            'London'
        )
        self.assertIsNone(distance)

    @patch('googlemaps.Client')
    def test_process_excel_file(self, mock_client):
        """Test Excel file processing"""
        mock_gmaps = Mock()
        mock_gmaps.distance_matrix.return_value = self.sample_distance_response
        mock_gmaps.geocode.return_value = self.sample_geocode_response
        mock_client.return_value = mock_gmaps

        # Test successful file processing
        process_excel_file(self.test_input_file, self.test_output_file, self.api_key)

        # Verify output file exists and has correct structure
        self.assertTrue(os.path.exists(self.test_output_file))
        output_df = pd.read_excel(self.test_output_file)

        # Check if all expected columns are present
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

        # Test file processing with invalid input file
        with self.assertRaises(Exception):
            process_excel_file('invalid_file.xlsx', self.test_output_file, self.api_key)


class TestDistanceCalculatorIntegration(unittest.TestCase):
    """Integration tests for the Distance Calculator"""

    @patch('googlemaps.Client')
    def test_end_to_end_processing(self, mock_client):
        """Test end-to-end processing with mock data"""
        # Create test input file
        test_data = pd.DataFrame({
            'Starting_City': ['New York', 'London', 'Tokyo'],
            'Destination': ['Boston', 'Paris', 'Kyoto']
        })
        input_file = 'integration_test_input.xlsx'
        output_file = 'integration_test_output.xlsx'
        test_data.to_excel(input_file, index=False)

        try:
            # Mock Google Maps client responses
            mock_gmaps = Mock()
            mock_gmaps.distance_matrix.return_value = {
                'rows': [{
                    'elements': [{
                        'status': 'OK',
                        'distance': {'value': 50000, 'text': '50 km'},
                        'duration': {'value': 3600, 'text': '1 hour'}
                    }]
                }]
            }
            mock_gmaps.geocode.return_value = [{
                'geometry': {
                    'location': {'lat': 40.7128, 'lng': -74.0060}
                }
            }]
            mock_client.return_value = mock_gmaps

            # Process the file
            process_excel_file(input_file, output_file, 'test_api_key')

            # Verify results
            result_df = pd.read_excel(output_file)

            # Check if all rows were processed
            self.assertEqual(len(result_df), 3)

            # Check if all distance columns contain valid data
            distance_columns = [col for col in result_df.columns if 'Distance' in col]
            for col in distance_columns:
                self.assertFalse(result_df[col].isnull().all())

        finally:
            # Clean up test files
            if os.path.exists(input_file):
                os.remove(input_file)
            if os.path.exists(output_file):
                os.remove(output_file)


def run_tests():
    """Run all tests with detailed output"""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    run_tests()