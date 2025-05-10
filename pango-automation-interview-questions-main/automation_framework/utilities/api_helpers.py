import requests
from typing import Optional, Dict, Any

class ApiHelper:
    def __init__(self, api_key: str):
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.api_key = api_key
    
    def get_weather_data(self, city: str) -> Optional[Dict[str, Any]]:
        """Get weather data from OpenWeatherMap API."""
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'  # Get temperature in Celsius
            }
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return {
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like']
            }
        except Exception:
            return None
    
    def get_weather_data_batch(self, cities: list) -> list:
        """Get weather data for multiple cities."""
        results = []
        for city in cities:
            data = self.get_weather_data(city)
            if data:
                data['city'] = city
                results.append(data)
        return results
