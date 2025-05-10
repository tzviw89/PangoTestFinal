import sqlite3
from typing import List, Dict, Any

class DbHelper:
    def __init__(self, db_path: str = "data.db"):
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self):
        """Create the required tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS weather_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT NOT NULL,
                    temperature_web REAL,
                    feels_like_web REAL,
                    temperature_api REAL,
                    feels_like_api REAL,
                    avg_temperature REAL GENERATED ALWAYS AS ((temperature_web + temperature_api) / 2) STORED,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def save_weather_data(self, web_data: Dict[str, Any], api_data: Dict[str, Any]):
        """Save weather data from both sources."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO weather_data (
                    city, temperature_web, feels_like_web,
                    temperature_api, feels_like_api
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                web_data['city'],
                web_data['temperature'],
                web_data['feels_like'],
                api_data['temperature'],
                api_data['feels_like']
            ))
    
    def get_discrepancy_report(self, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """Get cities where temperature difference exceeds threshold."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT 
                    city,
                    temperature_web,
                    temperature_api,
                    avg_temperature,
                    ABS(temperature_web - temperature_api) as discrepancy
                FROM weather_data
                WHERE ABS(temperature_web - temperature_api) > ?
                ORDER BY discrepancy DESC
            """, (threshold,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_summary_stats(self) -> Dict[str, float]:
        """Get summary statistics of temperature discrepancies."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT 
                    AVG(ABS(temperature_web - temperature_api)) as mean_discrepancy,
                    MAX(ABS(temperature_web - temperature_api)) as max_discrepancy,
                    MIN(ABS(temperature_web - temperature_api)) as min_discrepancy
                FROM weather_data
            """)
            row = cursor.fetchone()
            return {
                'mean_discrepancy': row[0],
                'max_discrepancy': row[1],
                'min_discrepancy': row[2]
            }

