import time
from playwright.sync_api import sync_playwright, TimeoutError
from typing import Optional, Dict, Any, List

class WebHelper:
    def __init__(self, debug_mode: bool = False, headless: bool = True):
        self.debug_mode = debug_mode
        self.headless = headless
        self.base_url = "https://www.timeanddate.com/weather/"
        self.playwright = None
        self.browser = None
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        
        # Map of cities to their country codes
        self.city_country_map = {
            "London": "uk",
            "Paris": "france",
            "New York": "usa",
            "Tokyo": "japan",
            "Sydney": "australia",
            "Berlin": "germany",
            "Rome": "italy",
            "Madrid": "spain",
            "Moscow": "russia",
            "Dubai": "uae",
            "Singapore": "singapore",
            "Hong Kong": "hong-kong",
            "Toronto": "canada",
            "Seoul": "south-korea",
            "Istanbul": "turkey",
            "Bangkok": "thailand",
            "Amsterdam": "netherlands",
            "Vienna": "austria",
            "Stockholm": "sweden",
            "Cairo": "egypt"
        }
    
    def _log_debug(self, message: str):
        """Log debug messages if debug mode is enabled."""
        if self.debug_mode:
            # Skip logging raw HTML content
            if "Page content:" in message or "Raw text:" in message:
                return
            # Clean up temperature logging
            if "Raw temperature text:" in message:
                message = message.replace("Raw temperature text:", "Temperature found:")
            if "Raw feels-like text:" in message:
                message = message.replace("Raw feels-like text:", "Feels-like found:")
            print(f"[DEBUG] {message}")
    
    def _extract_temperature(self, text: str) -> Optional[float]:
        """Extract temperature value from text."""
        try:
            # Remove °F and convert to Celsius
            if '°F' in text:
                fahrenheit = float(''.join(c for c in text if c.isdigit() or c in '.-'))
                celsius = (fahrenheit - 32) * 5/9
                return round(celsius, 1)
            # Handle Celsius
            elif '°C' in text:
                celsius = float(''.join(c for c in text if c.isdigit() or c in '.-'))
                return round(celsius, 1)
            return None
        except (ValueError, TypeError):
            return None

    def _init_browser(self):
        """Initialize the browser if not already initialized."""
        if not self.playwright:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=['--disable-dev-shm-usage', '--no-sandbox']
            )

    def _close_browser(self):
        """Close the browser and playwright instance."""
        if self.browser:
            self.browser.close()
            self.browser = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None

    def get_weather_data(self, city: str) -> Optional[Dict[str, Any]]:
        """Get weather data for a single city."""
        for attempt in range(self.max_retries):
            try:
                self._init_browser()
                page = self.browser.new_page()
                
                # Get country code for the city
                country_code = self.city_country_map.get(city)
                if not country_code:
                    self._log_debug(f"No country code found for {city}")
                    return None
                
                # Format city name for URL
                city_url = city.lower().replace(" ", "-")
                url = f"{self.base_url}{country_code}/{city_url}"
                
                self._log_debug(f"Processing {city} (Attempt {attempt + 1}/{self.max_retries})")
                page.goto(url, timeout=60000)
                
                # Wait for the main content to load
                page.wait_for_selector("div#wt-temp, div.h2", timeout=30000)
                
                # Try different selectors for temperature
                temp_element = None
                for selector in ["div#wt-temp", "div.h2", "span.h2"]:
                    temp_element = page.query_selector(selector)
                    if temp_element:
                        break
                
                if not temp_element:
                    self._log_debug(f"Temperature element not found for {city}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return None
                
                temp_text = temp_element.inner_text()
                temperature = self._extract_temperature(temp_text)
                if temperature is None:
                    self._log_debug(f"Could not extract temperature for {city}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return None
                
                # Get feels like temperature
                feels_like = None
                
                # Get all elements that might contain temperature
                all_temps = page.evaluate("""
                    () => {
                        const elements = Array.from(document.querySelectorAll('div, span'));
                        return elements
                            .map(el => el.textContent)
                            .filter(text => text.includes('°'))
                            .map(text => text.trim());
                    }
                """)
                
                if all_temps and len(all_temps) > 1:
                    # Try to find the feels-like temperature
                    for temp_text in all_temps:
                        # Skip the main temperature
                        if temp_text == temp_element.inner_text():
                            continue
                        # Try to extract temperature
                        temp = self._extract_temperature(temp_text)
                        if temp is not None:
                            feels_like = temp
                            break
                
                self._log_debug(f"{city}: {temperature}°C (feels like: {feels_like}°C)")
                
                return {
                    'city': city,
                    'temperature': temperature,
                    'feels_like': feels_like
                }
                
            except Exception as e:
                self._log_debug(f"Error processing {city}: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return None
            finally:
                if page:
                    page.close()
    
    def get_weather_data_batch(self, cities: List[str]) -> List[Dict[str, Any]]:
        """Get weather data for multiple cities."""
        results = []
        try:
            for city in cities:
                self._log_debug(f"Processing {city}")
                data = self.get_weather_data(city)
                if data:
                    results.append(data)
                time.sleep(3)  # Increased delay between requests
        finally:
            self._close_browser()
        return results 