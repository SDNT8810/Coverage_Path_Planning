"""
Basic tests for the field coverage planner.
"""

import unittest
import tempfile
import os
from pathlib import Path

# Add the src directory to the path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from field_coverage.core.coordinates import GPSCoordinate, UTMCoordinate, CoordinateTransformer
from field_coverage.core.field import Field, FieldBoundary
from field_coverage.core.waypoint import Waypoint, WaypointSequence, WaypointType
from field_coverage.io.csv_handler import CSVHandler
from field_coverage.main import FieldCoveragePlanner


class TestCoordinates(unittest.TestCase):
    """Test coordinate system functionality."""
    
    def test_gps_coordinate_creation(self):
        """Test GPS coordinate creation and validation."""
        # Valid coordinates
        coord = GPSCoordinate(40.7128, -74.0060)
        self.assertEqual(coord.latitude, 40.7128)
        self.assertEqual(coord.longitude, -74.0060)
        
        # Invalid latitude
        with self.assertRaises(ValueError):
            GPSCoordinate(91.0, -74.0060)
        
        # Invalid longitude
        with self.assertRaises(ValueError):
            GPSCoordinate(40.7128, 181.0)
    
    def test_utm_coordinate_creation(self):
        """Test UTM coordinate creation and validation."""
        # Valid coordinates
        coord = UTMCoordinate(585000, 4511000, 18, 'N')
        self.assertEqual(coord.easting, 585000)
        self.assertEqual(coord.northing, 4511000)
        self.assertEqual(coord.zone, 18)
        self.assertEqual(coord.hemisphere, 'N')
        
        # Invalid zone
        with self.assertRaises(ValueError):
            UTMCoordinate(585000, 4511000, 61, 'N')
        
        # Invalid hemisphere
        with self.assertRaises(ValueError):
            UTMCoordinate(585000, 4511000, 18, 'X')
    
    def test_distance_calculation(self):
        """Test distance calculation between GPS coordinates."""
        coord1 = GPSCoordinate(40.7128, -74.0060)
        coord2 = GPSCoordinate(40.7580, -73.9855)
        
        distance = coord1.distance_to(coord2)
        self.assertGreater(distance, 0)
        self.assertLess(distance, 10000)  # Should be less than 10km


class TestField(unittest.TestCase):
    """Test field functionality."""
    
    def setUp(self):
        """Set up test field."""
        self.field_coords = [
            GPSCoordinate(40.7128, -74.0060),
            GPSCoordinate(40.7138, -74.0060),
            GPSCoordinate(40.7138, -74.0050),
            GPSCoordinate(40.7128, -74.0050),
            GPSCoordinate(40.7128, -74.0060),  # Close polygon
        ]
    
    def test_field_creation(self):
        """Test field creation from GPS coordinates."""
        field = Field.from_gps_coordinates(
            coordinates=self.field_coords,
            field_id="test_field"
        )
        
        self.assertEqual(field.field_id, "test_field")
        self.assertEqual(len(field.main_boundary.gps_coordinates), 5)
        self.assertEqual(len(field.holes), 0)
    
    def test_field_area_calculation(self):
        """Test field area calculation."""
        field = Field.from_gps_coordinates(
            coordinates=self.field_coords,
            field_id="test_field"
        )
        
        area = field.calculate_area()
        self.assertGreater(area, 0)
        self.assertLess(area, 1000000)  # Should be reasonable size


class TestWaypoints(unittest.TestCase):
    """Test waypoint functionality."""
    
    def test_waypoint_creation(self):
        """Test waypoint creation."""
        coord = GPSCoordinate(40.7128, -74.0060)
        waypoint = Waypoint(
            gps_coordinate=coord,
            heading=90.0,
            speed=2.0,
            waypoint_type=WaypointType.COVERAGE
        )
        
        self.assertEqual(waypoint.gps_coordinate, coord)
        self.assertEqual(waypoint.heading, 90.0)
        self.assertEqual(waypoint.speed, 2.0)
        self.assertEqual(waypoint.waypoint_type, WaypointType.COVERAGE)
    
    def test_waypoint_sequence(self):
        """Test waypoint sequence functionality."""
        waypoints = []
        for i in range(5):
            coord = GPSCoordinate(40.7128 + i * 0.001, -74.0060)
            waypoint = Waypoint(
                gps_coordinate=coord,
                heading=0.0,
                speed=2.0,
                waypoint_id=i + 1
            )
            waypoints.append(waypoint)
        
        sequence = WaypointSequence(waypoints)
        self.assertEqual(len(sequence), 5)
        
        total_distance = sequence.total_distance()
        self.assertGreater(total_distance, 0)


class TestCSVHandler(unittest.TestCase):
    """Test CSV input/output functionality."""
    
    def test_csv_writing_reading(self):
        """Test writing and reading waypoints to/from CSV."""
        # Create test waypoints
        waypoints = []
        for i in range(3):
            coord = GPSCoordinate(40.7128 + i * 0.001, -74.0060)
            waypoint = Waypoint(
                gps_coordinate=coord,
                heading=90.0,
                speed=2.0,
                waypoint_id=i + 1
            )
            waypoints.append(waypoint)
        
        sequence = WaypointSequence(waypoints)
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_file = f.name
        
        try:
            CSVHandler.write_waypoints_csv(sequence, temp_file)
            
            # Verify file exists and has content
            self.assertTrue(os.path.exists(temp_file))
            
            # Read back waypoints
            loaded_sequence = CSVHandler.read_waypoints_csv(temp_file)
            self.assertEqual(len(loaded_sequence), len(sequence))
            
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.unlink(temp_file)


class TestFieldCoveragePlanner(unittest.TestCase):
    """Test main planner functionality."""
    
    def test_planner_initialization(self):
        """Test planner initialization."""
        planner = FieldCoveragePlanner(
            swath_width=2.0,
            overlap=0.1,
            turn_radius=3.0,
            speed=2.5
        )
        
        self.assertEqual(planner.swath_width, 2.0)
        self.assertEqual(planner.overlap, 0.1)
        self.assertEqual(planner.turn_radius, 3.0)
        self.assertEqual(planner.speed, 2.5)
    
    def test_configuration_validation(self):
        """Test planner configuration validation."""
        planner = FieldCoveragePlanner()
        
        # Valid configuration should have no errors
        errors = planner.validate_configuration()
        self.assertEqual(len(errors), 0)
        
        # Invalid configuration should have errors
        planner.swath_width = -1.0
        errors = planner.validate_configuration()
        self.assertGreater(len(errors), 0)
    
    def test_parameter_updates(self):
        """Test parameter updates."""
        planner = FieldCoveragePlanner()
        
        original_swath = planner.swath_width
        planner.set_parameters(swath_width=5.0)
        
        self.assertNotEqual(planner.swath_width, original_swath)
        self.assertEqual(planner.swath_width, 5.0)


def run_basic_tests():
    """Run basic functionality tests."""
    print("Running Basic Tests...")
    print("=" * 40)
    
    # Test coordinate creation
    print("Testing GPS coordinate creation...")
    try:
        coord = GPSCoordinate(40.7128, -74.0060)
        print(f"✓ GPS coordinate created: {coord.latitude}, {coord.longitude}")
    except Exception as e:
        print(f"✗ GPS coordinate test failed: {e}")
    
    # Test field creation
    print("\nTesting field creation...")
    try:
        field_coords = [
            GPSCoordinate(40.7128, -74.0060),
            GPSCoordinate(40.7138, -74.0060),
            GPSCoordinate(40.7138, -74.0050),
            GPSCoordinate(40.7128, -74.0050),
            GPSCoordinate(40.7128, -74.0060),
        ]
        
        field = Field.from_gps_coordinates(
            coordinates=field_coords,
            field_id="test_field"
        )
        
        area = field.calculate_area()
        print(f"✓ Field created with area: {area:.1f} m²")
    except Exception as e:
        print(f"✗ Field creation test failed: {e}")
    
    # Test planner initialization
    print("\nTesting planner initialization...")
    try:
        planner = FieldCoveragePlanner(
            swath_width=2.0,
            overlap=0.1,
            speed=2.0
        )
        
        errors = planner.validate_configuration()
        if not errors:
            print("✓ Planner initialized and validated successfully")
        else:
            print(f"✗ Planner validation failed: {errors}")
    except Exception as e:
        print(f"✗ Planner initialization test failed: {e}")
    
    print("\nBasic tests completed!")


if __name__ == "__main__":
    # Run basic tests without requiring external dependencies
    run_basic_tests()
    
    print("\n" + "=" * 50)
    print("Note: Full unit tests require numpy, shapely, and pandas")
    print("Run 'python -m pytest tests/' after installing dependencies")
    print("=" * 50)
