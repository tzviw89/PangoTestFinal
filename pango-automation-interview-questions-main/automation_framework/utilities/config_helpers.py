import configparser
import os

class ConfigHelper:
    def __init__(self, config_file="automation_framework/config/config.ini"):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        
        # Create reports directory if it doesn't exist
        self.report_dir = self.get_report_dir()
        os.makedirs(self.report_dir, exist_ok=True)
    
    def get_api_key(self):
        """Get the OpenWeatherMap API key."""
        return self.config['API']['API_KEY']
    
    def get_db_name(self):
        """Get the database name."""
        return self.config['DB']['DB_NAME']
    
    def get_temperature_threshold(self):
        """Get the temperature difference threshold in Celsius."""
        return float(self.config['REPORT']['TEMPERATURE_THRESHOLD'])
    
    def get_report_dir(self):
        """Get the directory for storing reports."""
        return self.config['REPORT']['REPORT_DIR'] 