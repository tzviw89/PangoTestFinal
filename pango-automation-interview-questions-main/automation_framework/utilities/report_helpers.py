import csv
import os
from datetime import datetime
from automation_framework.utilities.config_helpers import ConfigHelper
from typing import List, Dict, Any

class ReportHelper:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        self.config = ConfigHelper()
        self.report_dir = self.config.get_report_dir()
        self.threshold = self.config.get_temperature_threshold()
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_reports(self, weather_data):
        """Generate both CSV and HTML reports for the weather data.
        
        Args:
            weather_data (list): List of dictionaries containing weather data for each city
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Calculate statistics
        stats = self._calculate_statistics(weather_data)
        
        # Generate reports
        csv_path = self._generate_csv_report(weather_data, stats, timestamp)
        html_path = self._generate_html_report(weather_data, stats, timestamp)
        
        return {
            'csv_path': csv_path,
            'html_path': html_path,
            'statistics': stats
        }
    
    def _calculate_statistics(self, weather_data):
        """Calculate statistics for the weather data."""
        differences = [abs(d['temperature_web'] - d['temperature_api']) for d in weather_data]
        exceeded_threshold = [d for d in weather_data if abs(d['temperature_web'] - d['temperature_api']) > self.threshold]
        
        return {
            'mean_difference': sum(differences) / len(differences) if differences else 0,
            'max_difference': max(differences) if differences else 0,
            'min_difference': min(differences) if differences else 0,
            'cities_exceeding_threshold': len(exceeded_threshold),
            'threshold': self.threshold
        }
    
    def _generate_csv_report(self, weather_data, stats, timestamp):
        """Generate a CSV report."""
        filename = f"{self.output_dir}/weather_report_{timestamp}.csv"
        
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['City', 'Web Temperature (°C)', 'API Temperature (°C)', 
                           'Temperature Difference (°C)', 'Exceeds Threshold'])
            
            # Write data rows
            for data in weather_data:
                diff = abs(data['temperature_web'] - data['temperature_api'])
                exceeds = 'Yes' if diff > self.threshold else 'No'
                writer.writerow([
                    data['city'],
                    data['temperature_web'],
                    data['temperature_api'],
                    round(diff, 1),
                    exceeds
                ])
            
            # Write statistics
            writer.writerow([])  # Empty row
            writer.writerow(['Statistics'])
            writer.writerow(['Mean Temperature Difference (°C)', round(stats['mean_difference'], 1)])
            writer.writerow(['Maximum Temperature Difference (°C)', round(stats['max_difference'], 1)])
            writer.writerow(['Minimum Temperature Difference (°C)', round(stats['min_difference'], 1)])
            writer.writerow(['Cities Exceeding Threshold', stats['cities_exceeding_threshold']])
            writer.writerow(['Temperature Threshold (°C)', self.threshold])
        
        return filename
    
    def _generate_html_report(self, weather_data, stats, timestamp):
        """Generate an HTML report."""
        filename = f"weather_report_{timestamp}.html"
        filepath = os.path.join(self.report_dir, filename)
        
        # Start HTML content
        html_content = [
            '<!DOCTYPE html>',
            '<html>',
            '<head>',
            '    <title>Weather Comparison Report</title>',
            '    <style>',
            '        body { font-family: Arial, sans-serif; margin: 20px; }',
            '        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }',
            '        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }',
            '        th { background-color: #f2f2f2; }',
            '        .exceeds { background-color: #ffebee; }',
            '        .stats { background-color: #f5f5f5; padding: 15px; border-radius: 5px; }',
            '    </style>',
            '</head>',
            '<body>',
            '    <h1>Weather Comparison Report</h1>',
            '    <p>Generated on: ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '</p>',
            '    <h2>Temperature Comparison</h2>',
            '    <table>',
            '        <tr>',
            '            <th>City</th>',
            '            <th>Web Temperature (°C)</th>',
            '            <th>API Temperature (°C)</th>',
            '            <th>Temperature Difference (°C)</th>',
            '            <th>Exceeds Threshold</th>',
            '        </tr>'
        ]
        
        # Add data rows
        for data in weather_data:
            diff = abs(data['temperature_web'] - data['temperature_api'])
            exceeds = 'Yes' if diff > self.threshold else 'No'
            row_class = ' class="exceeds"' if exceeds == 'Yes' else ''
            
            html_content.extend([
                f'        <tr{row_class}>',
                f'            <td>{data["city"]}</td>',
                f'            <td>{data["temperature_web"]}</td>',
                f'            <td>{data["temperature_api"]}</td>',
                f'            <td>{round(diff, 1)}</td>',
                f'            <td>{exceeds}</td>',
                '        </tr>'
            ])
        
        # Add statistics section
        html_content.extend([
            '    </table>',
            '    <div class="stats">',
            '        <h2>Statistics</h2>',
            f'        <p>Mean Temperature Difference: {round(stats["mean_difference"], 1)}°C</p>',
            f'        <p>Maximum Temperature Difference: {round(stats["max_difference"], 1)}°C</p>',
            f'        <p>Minimum Temperature Difference: {round(stats["min_difference"], 1)}°C</p>',
            f'        <p>Cities Exceeding Threshold: {stats["cities_exceeding_threshold"]}</p>',
            f'        <p>Temperature Threshold: {self.threshold}°C</p>',
            '    </div>',
            '</body>',
            '</html>'
        ])
        
        # Write to file
        with open(filepath, 'w') as f:
            f.write('\n'.join(html_content))
        
        return filepath

    def generate_csv_report(self, discrepancy_data: List[Dict[str, Any]], stats: Dict[str, float]) -> str:
        """Generate a CSV report with weather data and analysis."""
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"weather_report_{timestamp}.csv"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'City',
                'Web Temperature (°C)',
                'API Temperature (°C)',
                'Average Temperature (°C)',
                'Temperature Difference (°C)',
                'Web Feels Like (°C)',
                'API Feels Like (°C)',
                'Feels Like Difference (°C)'
            ])
            
            # Write data rows
            for item in discrepancy_data:
                writer.writerow([
                    item['city'],
                    f"{item['temperature_web']:.1f}",
                    f"{item['temperature_api']:.1f}",
                    f"{item['avg_temperature']:.1f}",
                    f"{item['discrepancy']:.1f}",
                    f"{item.get('feels_like_web', 'N/A')}",
                    f"{item.get('feels_like_api', 'N/A')}",
                    f"{abs(item.get('feels_like_web', 0) - item.get('feels_like_api', 0)):.1f}" if 'feels_like_web' in item and 'feels_like_api' in item else 'N/A'
                ])
            
            # Write summary statistics
            writer.writerow([])  # Empty row for spacing
            writer.writerow(['Summary Statistics'])
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Mean Temperature Difference', f"{stats['mean_discrepancy']:.1f}°C"])
            writer.writerow(['Maximum Temperature Difference', f"{stats['max_discrepancy']:.1f}°C"])
            writer.writerow(['Minimum Temperature Difference', f"{stats['min_discrepancy']:.1f}°C"])
            
            # Add timestamp
            writer.writerow([])
            writer.writerow(['Report Generated', datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        
        return filepath 