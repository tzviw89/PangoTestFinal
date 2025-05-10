import pytest
from automation_framework.utilities.web_helpers import WebHelper

@pytest.fixture
def web_helper():
    return WebHelper()

def test_get_weather_data(web_helper):
    """Test that we can get weather data for a single city."""
    # Test with a known city
    city = "London"
    data = web_helper.get_weather_data(city)
    
    # Check that we got valid data
    assert data is not None, "Web scraping should return data"
    assert 'temperature' in data, "Data should contain temperature"
    assert 'feels_like' in data, "Data should contain feels_like"
    
    # Check that the temperatures are reasonable values
    assert -50 <= data['temperature'] <= 50, "Temperature should be in reasonable range"
    assert -50 <= data['feels_like'] <= 50, "Feels like temperature should be in reasonable range"

def test_get_weather_data_batch(web_helper):
    """Test that we can get weather data for multiple cities."""
    # Test with a few cities
    cities = ['London', 'Paris', 'Berlin']
    results = web_helper.get_weather_data_batch(cities)
    
    # Check that we got data for all cities
    assert len(results) == len(cities), "Should get data for all cities"
    
    # Check each result
    for result in results:
        assert 'city' in result, "Result should contain city name"
        assert 'temperature' in result, "Result should contain temperature"
        assert 'feels_like' in result, "Result should contain feels_like"
        assert result['city'] in cities, "City should be in the test list"
        assert -50 <= result['temperature'] <= 50, "Temperature should be in reasonable range"
        assert -50 <= result['feels_like'] <= 50, "Feels like temperature should be in reasonable range"

def test_invalid_city(web_helper):
    """Test handling of invalid city names."""
    # Test with a non-existent city
    city = "ThisCityDoesNotExist123"
    data = web_helper.get_weather_data(city)
    
    # Should return None for invalid cities
    assert data is None, "Should return None for invalid cities" 