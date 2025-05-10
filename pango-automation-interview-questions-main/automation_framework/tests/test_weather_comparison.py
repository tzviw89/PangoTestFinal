import pytest
from playwright.sync_api import sync_playwright, TimeoutError
import json
from automation_framework.utilities.api_helpers import ApiHelper
from automation_framework.utilities.db_helpers import DbHelper
import time

# List of 20 diverse cities for testing
CITIES = [
    "New York", "London", "Tokyo", "Paris", "Sydney",
    "Dubai", "Singapore", "Mumbai", "Cairo", "Rio de Janeiro",
    "Toronto", "Berlin", "Seoul", "Rome", "Bangkok",
    "Istanbul", "Moscow", "Mexico City", "Cape Town", "Amsterdam"
]

def kelvin_to_celsius(kelvin):
    return round(kelvin - 273.15, 1)

@pytest.fixture(scope="module")
def api():
    return ApiHelper()

@pytest.fixture(scope="module")
def db():
    return DbHelper()

@pytest.fixture(scope="module")
def playwright():
    with sync_playwright() as p:
        yield p

def test_weather_comparison(api, db, playwright):
    print("\nStarting weather comparison test...")
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    results = []
    
    for city in CITIES:
        try:
            print(f"\nProcessing {city}...")
            
            # Get API data
            print("Calling API...")
            api_response = api.get_current_weather(city)
            
            if api_response is None:
                print(f"Failed to get API data for {city}")
                continue
                
            print("API call done. Parsing response...")
            api_data = api_response.json()
            
            if "main" not in api_data:
                print(f"Unexpected API response format for {city}: {api_data}")
                continue
                
            temp_api = kelvin_to_celsius(api_data["main"]["temp"])
            feels_like_api = kelvin_to_celsius(api_data["main"]["feels_like"])
            print(f"API data: temp={temp_api}, feels_like={feels_like_api}")
            
            # Get web data
            city_url = city.lower().replace(' ', '-')
            print(f"Navigating to https://www.timeanddate.com/weather/{city_url}")
            page.goto(f"https://www.timeanddate.com/weather/{city_url}")
            
            # Wait for the page to load
            print("Waiting for page to load...")
            page.wait_for_load_state("networkidle")
            
            # Get temperature
            print("Waiting for temperature selector...")
            try:
                page.wait_for_selector("#wt-temp", timeout=10000)
                print("Temperature selector found. Extracting data...")
                temp_web = page.locator("#wt-temp").text_content()
                print(f"Raw web temperature: {temp_web}")
                temp_web = float(temp_web.replace('°C', '').strip())
                print(f"Web temperature: {temp_web}°C")
                
                # Get feels like temperature
                print("Looking for feels like temperature...")
                feels_like_web = None
                try:
                    # Try to find the feels like temperature in the weather details
                    feels_like_text = page.locator("text=Feels Like").first
                    if feels_like_text:
                        feels_like_web = feels_like_text.locator("xpath=..").text_content()
                        feels_like_web = float(feels_like_web.split('°')[0].strip())
                        print(f"Web feels like: {feels_like_web}°C")
                except Exception as e:
                    print(f"Could not find feels like temperature: {str(e)}")
                
                # Store data in database
                weather_data = {
                    "city": city,
                    "temperature_web": temp_web,
                    "feels_like_web": feels_like_web,
                    "temperature_api": temp_api,
                    "feels_like_api": feels_like_api
                }
                db.insert_weather_data(weather_data)
                
                results.append(weather_data)
                
            except TimeoutError:
                print(f"Timeout waiting for temperature selector on {city_url}")
                print("Page content:", page.content())
                continue
            except Exception as e:
                print(f"Error extracting temperature: {str(e)}")
                continue
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Error processing {city}: {str(e)}")
            continue
    
    browser.close()
    
    if not results:
        print("\nNo results were collected. Check the logs above for errors.")
    else:
        print("\nWeather Comparison Results:")
        for result in results:
            print(f"\nCity: {result['city']}")
            print(f"Web Temperature: {result['temperature_web']}°C")
            if result['feels_like_web'] is not None:
                print(f"Web Feels Like: {result['feels_like_web']}°C")
            print(f"API Temperature: {result['temperature_api']}°C")
            print(f"API Feels Like: {result['feels_like_api']}°C")
            print(f"Temperature Difference: {round(abs(result['temperature_web'] - result['temperature_api']), 1)}°C")
        
        # Print database summary
        print("\nDatabase Summary:")
        all_data = db.get_all_weather_data()
        print(f"Total records in database: {len(all_data)}")
    
    assert len(results) > 0, "No results were collected" 