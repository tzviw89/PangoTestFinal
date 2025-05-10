# Weather API Testing & Analysis Project

## Overview
This project compares real-time temperature readings from timeanddate.com and OpenWeatherMap API, stores the data, and provides analysis through reports and an interactive dashboard.

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pango-automation-interview-questions-main
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Unix/MacOS
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

4. **Configure API Key**
   - Create a `config.ini` file in the root directory
   - Add your OpenWeatherMap API key:
     ```ini
     [API]
     API_KEY = your_api_key_here
     BASE_URL = https://api.openweathermap.org/data/2.5/weather
     ```

## Running Tests

1. **Run all tests**
   ```bash
   python -m pytest tests/
   ```

2. **Run specific test files**
   ```bash
   # Test web scraping
   python tests/test_web_scraping.py
   
   # Test API integration
   python tests/test_openweather_api.py
   
   # Test database operations
   python tests/test_db_operations.py
   
   # Test report generation
   python tests/test_report_generation.py
   ```

## Viewing Reports

1. **CSV Reports**
   - Reports are generated in the `reports` directory
   - Filename format: `weather_report_YYYYMMDD_HHMMSS.csv`
   - Contains temperature data and discrepancy analysis

2. **Interactive Dashboard**
   ```bash
   python run_dashboard.py
   ```
   - Open your browser and navigate to http://127.0.0.1:8050/
   - Features:
     - Real-time temperature comparisons
     - Discrepancy analysis
     - Summary statistics
     - Auto-refresh every 5 minutes

## Project Structure

```
pango-automation-interview-questions-main/
├── automation_framework/
│   ├── utilities/
│   │   ├── web_helpers.py      # Web scraping functionality
│   │   ├── api_helpers.py      # API integration
│   │   ├── db_helpers.py       # Database operations
│   │   ├── report_helpers.py   # Report generation
│   │   └── city_list.py        # List of cities to monitor
│   └── dashboard/
│       └── app.py              # Interactive dashboard
├── tests/
│   ├── test_web_scraping.py
│   ├── test_openweather_api.py
│   ├── test_db_operations.py
│   └── test_report_generation.py
├── reports/                    # Generated reports
├── config.ini                  # Configuration file
├── setup.py                    # Package setup
└── run_dashboard.py           # Dashboard runner
```

## Features

1. **Data Collection**
   - Web scraping from timeanddate.com
   - OpenWeatherMap API integration
   - Temperature and feels-like data collection

2. **Data Storage**
   - SQLite database integration
   - Computed average temperatures
   - Historical data tracking

3. **Analysis & Reporting**
   - CSV report generation
   - Temperature discrepancy analysis
   - Summary statistics

4. **Interactive Dashboard**
   - Real-time data visualization
   - Temperature comparisons
   - Discrepancy monitoring
   - Auto-refresh functionality

## Troubleshooting

1. **Web Scraping Issues**
   - Ensure stable internet connection
   - Check if timeanddate.com is accessible
   - Verify city names in city_list.py

2. **API Issues**
   - Verify API key in config.ini
   - Check API rate limits
   - Ensure correct city names

3. **Database Issues**
   - Check database file permissions
   - Verify database schema
   - Ensure proper data types

4. **Dashboard Issues**
   - Check if port 8050 is available
   - Verify all dependencies are installed
   - Check browser compatibility

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
