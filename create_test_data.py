import pandas as pd

# Create test data with various scenarios
test_data = {
    'Starting_City': [
        'New York, NY, USA',
        'London, UK',
        'Tokyo, Japan',
        'Paris, France',
        'Los Angeles, CA, USA',
        'Sydney, Australia',
        'Toronto, Canada',
        'Berlin, Germany',
        'San Francisco, CA, USA',
        'Chicago, IL, USA'
    ],
    'Destination': [
        'Boston, MA, USA',          # Short domestic route (all transport modes possible)
        'Paris, France',            # International route (flight required)
        'Kyoto, Japan',             # Domestic route in different country
        'Amsterdam, Netherlands',    # Short international route (various modes possible)
        'Las Vegas, NV, USA',       # Medium domestic route
        'Melbourne, Australia',      # Domestic route in different country
        'Montreal, Canada',         # Domestic route with good public transport
        'Munich, Germany',          # Short European route
        'Seattle, WA, USA',         # Long domestic route
        'Milwaukee, WI, USA'        # Short domestic route
    ]
}

# Create DataFrame
df = pd.DataFrame(test_data)

# Save to Excel file
output_file = 'input_locations.xlsx'
df.to_excel(output_file, index=False)

print(f"Test data has been generated and saved to {output_file}")

# Display the test cases and their purposes
test_cases_explanation = """
Test Cases Explanation:
1. New York to Boston:
   - Tests short domestic route
   - All transport modes should be available
   - Good for validating public transport options

2. London to Paris:
   - Tests international route with multiple transport options
   - Should show Channel Tunnel rail option
   - Flight option should be available

3. Tokyo to Kyoto:
   - Tests domestic route in Japan
   - Should show bullet train option
   - All transport modes should be available

4. Paris to Amsterdam:
   - Tests European cross-border route
   - Multiple transport options should be available
   - Good for testing international public transport

5. Los Angeles to Las Vegas:
   - Tests medium-distance domestic route
   - Popular driving route
   - Limited public transport options

6. Sydney to Melbourne:
   - Tests domestic route in Australia
   - Popular flight route
   - Long driving distance

7. Toronto to Montreal:
   - Tests Canadian domestic route
   - Good public transport options
   - Multiple viable transport modes

8. Berlin to Munich:
   - Tests German domestic route
   - Excellent public transport options
   - Multiple viable transport modes

9. San Francisco to Seattle:
   - Tests longer domestic US route
   - Multiple transport options
   - Significant distance for driving

10. Chicago to Milwaukee:
    - Tests short domestic US route
    - All transport modes should be available
    - Good public transport options

Expected Outcomes:
- All locations are major cities with good Google Maps coverage
- Mix of domestic and international routes
- Various distances (short, medium, and long)
- Different transport mode availability
- Cross-border scenarios
- Island/continent scenarios
"""

print(test_cases_explanation)