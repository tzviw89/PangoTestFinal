import pytest
from automation_framework.utilities.api_helpers import ApiHelper
from automation_framework.utilities.db_helpers import DbHelper
from automation_framework.utilities.report_helpers import ReportHelper
from automation_framework.utilities.config_helpers import ConfigHelper

@pytest.fixture(scope="module")
def api():
    return ApiHelper()

@pytest.fixture
def api_helper():
    return ApiHelper()

@pytest.fixture
def db_helper():
    return DbHelper()

@pytest.fixture
def report_helper():
    return ReportHelper()

@pytest.fixture
def config_helper():
    return ConfigHelper()

def test_get_weather_data(api):
    """Test that we can get weather data from the API."""
    # Test with a known city
    city = "London"
    response = api.get_current_weather(city)
    
    # Check that we got a valid response
    assert response is not None, "API response should not be None"
    assert response.status_code == 200, f"API returned status code {response.status_code}"
    
    # Parse the response
    data = response.json()
    
    # Check that we got the expected data structure
    assert "main" in data, "Response should contain 'main' data"
    assert "temp" in data["main"], "Response should contain temperature"
    assert "feels_like" in data["main"], "Response should contain feels_like temperature"
    
    # Check that the temperatures are reasonable values (in Kelvin)
    assert 200 < data["main"]["temp"] < 350, "Temperature should be in reasonable range"
    assert 200 < data["main"]["feels_like"] < 350, "Feels like temperature should be in reasonable range"
    
    # Check that we got the correct city
    assert data["name"].lower() == city.lower(), f"Expected city {city}, got {data['name']}"

def test_api_connection(api_helper):
    """Test that the API connection is working."""
    response = api_helper.get_current_weather("London")
    assert response is not None
    assert response.status_code == 200

def test_api_data_structure(api_helper):
    """Test that the API response has the expected structure."""
    response = api_helper.get_current_weather("London")
    data = response.json()
    
    assert "main" in data
    assert "temp" in data["main"]
    assert "feels_like" in data["main"]
    assert isinstance(data["main"]["temp"], (int, float))
    assert isinstance(data["main"]["feels_like"], (int, float))

def test_temperature_range(api_helper):
    """Test that the temperature values are within reasonable ranges."""
    response = api_helper.get_current_weather("London")
    data = response.json()
    
    # Convert Kelvin to Celsius
    temp_c = data["main"]["temp"] - 273.15
    feels_like_c = data["main"]["feels_like"] - 273.15
    
    # Temperature should be between -50°C and 50°C
    assert -50 <= temp_c <= 50
    assert -50 <= feels_like_c <= 50

def test_database_operations(db_helper):
    """Test database operations for storing weather data."""
    # Test data
    test_data = {
        'city': 'London',
        'temperature_web': 20.5,
        'feels_like_web': 19.8,
        'temperature_api': 21.0,
        'feels_like_api': 20.2
    }
    
    # Insert test data
    db_helper.insert_weather_data(test_data)
    
    # Verify data was inserted
    result = db_helper.get_city_weather_data('London')
    assert result is not None
    assert len(result) > 0
    latest_data = result[0]  # Get the most recent entry
    assert latest_data[1] == test_data['city']  # city is at index 1
    assert latest_data[2] == test_data['temperature_web']  # temperature_web is at index 2
    assert latest_data[4] == test_data['temperature_api']  # temperature_api is at index 4

def test_report_generation(report_helper, db_helper):
    """Test report generation functionality."""
    # Create test data
    test_data = [
        {
            'city': 'London',
            'temperature_web': 20.5,
            'temperature_api': 21.0
        },
        {
            'city': 'Paris',
            'temperature_web': 22.0,
            'temperature_api': 18.0  # Large difference to test threshold
        },
        {
            'city': 'Berlin',
            'temperature_web': 19.0,
            'temperature_api': 19.5
        }
    ]
    
    # Generate reports
    report_result = report_helper.generate_reports(test_data)
    
    # Verify report files were created
    assert report_result['csv_path'] is not None
    assert report_result['html_path'] is not None
    
    # Verify statistics
    stats = report_result['statistics']
    assert 'mean_difference' in stats
    assert 'max_difference' in stats
    assert 'min_difference' in stats
    assert 'cities_exceeding_threshold' in stats
    
    # Verify that Paris is counted in cities exceeding threshold
    assert stats['cities_exceeding_threshold'] >= 1
    
    # Verify report files exist
    import os
    assert os.path.exists(report_result['csv_path'])
    assert os.path.exists(report_result['html_path'])

def test_end_to_end_workflow(api_helper, db_helper, report_helper):
    """Test the complete workflow from API call to report generation."""
    # Get weather data for multiple cities
    cities = ['London', 'Paris', 'Berlin', 'Madrid', 'Rome']
    weather_data = []
    
    for city in cities:
        # Get API data
        response = api_helper.get_current_weather(city)
        assert response.status_code == 200
        api_data = response.json()
        
        # Simulate web scraping data (in real scenario, this would come from web scraping)
        web_temp = api_data['main']['temp'] - 273.15  # Convert to Celsius
        web_feels_like = api_data['main']['feels_like'] - 273.15
        
        # Prepare data
        city_data = {
            'city': city,
            'temperature_web': web_temp,
            'feels_like_web': web_feels_like,
            'temperature_api': api_data['main']['temp'] - 273.15,
            'feels_like_api': api_data['main']['feels_like'] - 273.15
        }
        
        # Store in database
        db_helper.insert_weather_data(city_data)
        weather_data.append(city_data)
    
    # Generate reports
    report_result = report_helper.generate_reports(weather_data)
    
    # Verify the complete workflow
    assert report_result['csv_path'] is not None
    assert report_result['html_path'] is not None
    assert len(report_result['statistics']) > 0 