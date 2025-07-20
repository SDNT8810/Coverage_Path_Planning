"""
Example usage of the Field Coverage Planner library.
"""

from field_coverage import FieldCoveragePlanner, Field
from field_coverage.core.coordinates import GPSCoordinate
import os


def main():
    """Demonstrate basic usage of the field coverage planner."""
    
    print("Field Coverage Planner - Example Usage")
    print("=" * 40)
    
    # Initialize the planner
    planner = FieldCoveragePlanner(
        swath_width=2.0,    # 2 meter swath width
        overlap=0.1,        # 10% overlap
        turn_radius=3.0,    # 3 meter turn radius
        speed=2.5           # 2.5 m/s default speed
    )
    
    # Example 1: Create a simple rectangular field
    print("\n1. Creating a simple rectangular field...")
    
    # Define a rectangular field (approximately 100m x 50m)
    field_coords = [
        GPSCoordinate(40.7128, -74.0060),  # SW corner
        GPSCoordinate(40.7138, -74.0060),  # NW corner  
        GPSCoordinate(40.7138, -74.0050),  # NE corner
        GPSCoordinate(40.7128, -74.0050),  # SE corner
        GPSCoordinate(40.7128, -74.0060),  # Close polygon
    ]
    
    field = Field.from_gps_coordinates(
        coordinates=field_coords,
        field_id="example_field_1"
    )
    
    print(f"Field area: {field.calculate_area():.1f} m²")
    print(f"Field perimeter: {field.calculate_perimeter():.1f} m")
    
    # Generate coverage path
    print("\n2. Generating coverage path...")
    waypoints = planner.generate_coverage_path(field)
    
    print(f"Generated {len(waypoints)} waypoints")
    print(f"Total path distance: {waypoints.total_distance():.1f} m")
    print(f"Estimated time: {waypoints.total_time()/60:.1f} minutes")
    
    # Export to CSV
    output_dir = "examples/output"
    os.makedirs(output_dir, exist_ok=True)
    
    waypoints_file = os.path.join(output_dir, "example_waypoints.csv")
    planner.export_waypoints(waypoints, waypoints_file)
    print(f"\nWaypoints exported to: {waypoints_file}")
    
    # Generate field report
    report_file = os.path.join(output_dir, "example_report.csv")
    report_summary = planner.generate_field_report(field, waypoints, report_file)
    
    print(f"\nField Report Summary:")
    for key, value in report_summary.items():
        print(f"  {key}: {value}")
    
    # Example 2: Load field from CSV (if example file exists)
    example_csv = "data/example_field.csv"
    if os.path.exists(example_csv):
        print(f"\n3. Loading field from CSV: {example_csv}")
        try:
            csv_field = planner.load_field_from_csv(example_csv)
            csv_waypoints = planner.generate_coverage_path(csv_field)
            
            csv_output = os.path.join(output_dir, "csv_field_waypoints.csv")
            planner.export_waypoints(csv_waypoints, csv_output)
            
            print(f"CSV field processed successfully!")
            print(f"Generated {len(csv_waypoints)} waypoints")
            
        except Exception as e:
            print(f"Error processing CSV field: {e}")
    
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()
