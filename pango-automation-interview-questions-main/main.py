import os
from automation_framework.utilities.web_helpers import WebHelper
from automation_framework.utilities.api_helpers import ApiHelper
from automation_framework.utilities.db_helpers import DbHelper
from automation_framework.utilities.report_helpers import ReportHelper
from automation_framework.utilities.config_helpers import ConfigHelper
from automation_framework.utilities.city_list import CITIES

def main():
    # Initialize configuration
    config = ConfigHelper()
    api_key = config.get_api_key()
    
    # Initialize helpers
    web_helper = WebHelper(debug_mode=True)
    api_helper = ApiHelper(api_key=api_key)
    db_helper = DbHelper()
    report_helper = ReportHelper()
    
    print("Starting weather data collection...")
    
    # Get weather data from web scraping
    print("\nCollecting data from website...")
    web_data = web_helper.get_weather_data_batch(CITIES)
    
    # Get weather data from API
    print("\nCollecting data from API...")
    api_data = api_helper.get_weather_data_batch(CITIES)
    
    # Save data to database
    print("\nSaving data to database...")
    for city in CITIES:
        web_city_data = next((d for d in web_data if d['city'] == city), None)
        api_city_data = next((d for d in api_data if d['city'] == city), None)
        
        if web_city_data and api_city_data:
            db_helper.save_weather_data(web_city_data, api_city_data)
    
    # Generate reports
    print("\nGenerating reports...")
    discrepancy_data = db_helper.get_discrepancy_report()
    stats = db_helper.get_summary_stats()
    
    report_path = report_helper.generate_csv_report(discrepancy_data, stats)
    
    print(f"\nAnalysis complete! Report generated at: {report_path}")
    print("\nSummary Statistics:")
    print(f"Mean Discrepancy: {stats['mean_discrepancy']:.1f}°C")
    print(f"Max Discrepancy: {stats['max_discrepancy']:.1f}°C")
    print(f"Min Discrepancy: {stats['min_discrepancy']:.1f}°C")

if __name__ == "__main__":
    main() 