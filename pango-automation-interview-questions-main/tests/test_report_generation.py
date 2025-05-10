from automation_framework.utilities.db_helpers import DbHelper
from automation_framework.utilities.report_helpers import ReportHelper
import os

def test_report_generation():
    # Initialize helpers
    db_helper = DbHelper()
    report_helper = ReportHelper()
    
    # Get discrepancy data and stats from database
    discrepancy_data = db_helper.get_discrepancy_report(threshold=0.0)  # Get all data
    stats = db_helper.get_summary_stats()
    
    # Generate report
    report_path = report_helper.generate_csv_report(discrepancy_data, stats)
    
    # Verify report was created
    assert os.path.exists(report_path), "Report file was not created"
    
    # Print report location
    print(f"\nReport generated successfully at: {report_path}")
    
    # Print summary
    print("\nSummary Statistics:")
    print(f"Mean Temperature Difference: {stats['mean_discrepancy']:.1f}°C")
    print(f"Maximum Temperature Difference: {stats['max_discrepancy']:.1f}°C")
    print(f"Minimum Temperature Difference: {stats['min_discrepancy']:.1f}°C")
    
    # Print cities with largest discrepancies
    print("\nTop 5 Cities with Largest Temperature Differences:")
    sorted_data = sorted(discrepancy_data, key=lambda x: abs(x['discrepancy']), reverse=True)
    for item in sorted_data[:5]:
        print(f"{item['city']}: {abs(item['discrepancy']):.1f}°C difference")

if __name__ == "__main__":
    test_report_generation() 