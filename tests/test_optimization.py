#!/usr/bin/env python3
"""
Test script to verify the optimization algorithm works correctly.
"""

import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from field_coverage import Field, BoustrophedonPlanner
from field_coverage.io.csv_handler import CSVHandler

def test_optimization():
    print("🔍 Testing coverage optimization on 7-edge polygon...")
    
    # Load the field
    handler = CSVHandler()
    boundary_points = handler.read_field_boundary_csv("data/example_field.csv")
    
    # Create field boundary
    from field_coverage.core.field import FieldBoundary
    boundary = FieldBoundary(boundary_points)
    field = Field(boundary, field_id="test_heptagon")
    
    # Create planner
    planner = BoustrophedonPlanner(swath_width=4.0)
    
    # Test the optimization directly with different step sizes
    print("\n🧮 Running optimization algorithm with 15° steps...")
    optimal_direction_15 = planner.optimize_direction(field, step_size=15.0)
    print(f"✓ Optimal direction (15° steps): {optimal_direction_15}°")
    
    print("\n🧮 Running optimization algorithm with 5° steps...")
    optimal_direction_5 = planner.optimize_direction(field, step_size=5.0)
    print(f"✓ Optimal direction (5° steps): {optimal_direction_5}°")
    
    # Generate coverage with optimal direction from fine optimization
    print(f"\n📐 Generating coverage with optimal direction ({optimal_direction_5}°)...")
    waypoints = planner.plan_coverage(field, direction=optimal_direction_5)
    print(f"✓ Generated {len(waypoints.waypoints)} waypoints")
    print(f"✓ Total path length: {waypoints.total_distance():.1f}m")
    
    # Compare with other directions
    print("\n📊 Comparing with other directions:")
    test_directions = [0, 30, 60, 90, 120, 150]
    
    for direction in test_directions:
        print(f"📐 Using specified direction: {direction}.0°")
        # Generate test coverage quietly (using the internal method)
        waypoints = planner._generate_test_coverage(field, direction)
        path_length = waypoints.total_distance()
        marker = " ⭐" if direction == optimal_direction_5 else ""
        print(f"  Direction {direction:3d}°: {path_length:8.1f}m{marker}")

if __name__ == "__main__":
    test_optimization()
