"""
Validation utilities for field coverage path planning.
"""

import math
from typing import List, Tuple, Optional, Dict, Any
from ..core.coordinates import GPSCoordinate
from ..core.field import Field
from ..core.waypoint import WaypointSequence


def validate_gps_coordinates(coordinates: List[GPSCoordinate]) -> List[str]:
    """
    Validate a list of GPS coordinates.
    
    Args:
        coordinates: List of GPS coordinates to validate
        
    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []
    
    if not coordinates:
        errors.append("Coordinate list is empty")
        return errors
    
    if len(coordinates) < 3:
        errors.append("At least 3 coordinates are required to form a polygon")
    
    for i, coord in enumerate(coordinates):
        try:
            # This will raise ValueError if coordinates are invalid
            _ = GPSCoordinate(coord.latitude, coord.longitude)
        except ValueError as e:
            errors.append(f"Invalid coordinate at index {i}: {str(e)}")
    
    # Check for duplicate consecutive points
    for i in range(len(coordinates) - 1):
        if (abs(coordinates[i].latitude - coordinates[i + 1].latitude) < 1e-8 and
            abs(coordinates[i].longitude - coordinates[i + 1].longitude) < 1e-8):
            errors.append(f"Duplicate consecutive coordinates at indices {i} and {i + 1}")
    
    return errors


def validate_polygon_closure(coordinates: List[GPSCoordinate], 
                           tolerance: float = 1e-6) -> bool:
    """
    Check if a polygon is properly closed.
    
    Args:
        coordinates: List of GPS coordinates
        tolerance: Tolerance for coordinate comparison
        
    Returns:
        True if polygon is closed, False otherwise
    """
    if len(coordinates) < 4:  # At least 3 unique points + closing point
        return False
    
    first = coordinates[0]
    last = coordinates[-1]
    
    return (abs(first.latitude - last.latitude) < tolerance and
            abs(first.longitude - last.longitude) < tolerance)


def validate_polygon_self_intersection(coordinates: List[Tuple[float, float]]) -> List[str]:
    """
    Check for self-intersections in a polygon.
    
    Args:
        coordinates: List of (x, y) coordinates
        
    Returns:
        List of validation error messages
    """
    errors = []
    n = len(coordinates)
    
    if n < 4:
        return errors
    
    # Check each edge against every other non-adjacent edge
    for i in range(n - 1):
        line1_start = coordinates[i]
        line1_end = coordinates[i + 1]
        
        for j in range(i + 2, n - 1):
            if j == n - 2 and i == 0:
                # Skip checking last edge against first edge (they share a vertex)
                continue
                
            line2_start = coordinates[j]
            line2_end = coordinates[j + 1]
            
            if _lines_intersect(line1_start, line1_end, line2_start, line2_end):
                errors.append(f"Self-intersection detected between edges {i}-{i+1} and {j}-{j+1}")
    
    return errors


def _lines_intersect(p1: Tuple[float, float], p2: Tuple[float, float],
                    p3: Tuple[float, float], p4: Tuple[float, float]) -> bool:
    """
    Check if two line segments intersect.
    
    Args:
        p1, p2: First line segment endpoints
        p3, p4: Second line segment endpoints
        
    Returns:
        True if lines intersect, False otherwise
    """
    def _ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
    
    return _ccw(p1, p3, p4) != _ccw(p2, p3, p4) and _ccw(p1, p2, p3) != _ccw(p1, p2, p4)


def validate_field_parameters(field: Field, 
                            swath_width: float, 
                            overlap: float = 0.0,
                            min_turn_radius: float = 1.0) -> List[str]:
    """
    Validate field and coverage parameters.
    
    Args:
        field: Field to validate
        swath_width: Width of coverage swath in meters
        overlap: Overlap percentage (0.0 to 1.0)
        min_turn_radius: Minimum turning radius in meters
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    # Validate swath width
    if swath_width <= 0:
        errors.append(f"Invalid swath width: {swath_width}. Must be positive.")
    
    # Validate overlap
    if not (0.0 <= overlap < 1.0):
        errors.append(f"Invalid overlap: {overlap}. Must be between 0.0 and 1.0.")
    
    # Validate turn radius
    if min_turn_radius <= 0:
        errors.append(f"Invalid minimum turn radius: {min_turn_radius}. Must be positive.")
    
    # Check if swath width is reasonable for field size
    try:
        field_area = field.calculate_area()
        min_bbox, max_bbox = field.get_bounding_box()
        field_width = max_bbox.easting - min_bbox.easting
        field_height = max_bbox.northing - min_bbox.northing
        min_dimension = min(field_width, field_height)
        
        if swath_width > min_dimension:
            errors.append(
                f"Swath width ({swath_width}m) is larger than minimum field dimension ({min_dimension:.1f}m)"
            )
        
        if swath_width > min_dimension / 2:
            errors.append(
                f"Warning: Swath width ({swath_width}m) is more than half the minimum field dimension"
            )
            
    except Exception as e:
        errors.append(f"Error calculating field dimensions: {str(e)}")
    
    return errors


def validate_waypoint_sequence(waypoints: WaypointSequence,
                             max_speed: float = 10.0,
                             max_heading_change: float = 45.0) -> List[str]:
    """
    Validate a waypoint sequence for feasibility.
    
    Args:
        waypoints: Waypoint sequence to validate
        max_speed: Maximum allowed speed in m/s
        max_heading_change: Maximum heading change between waypoints in degrees
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    if len(waypoints) == 0:
        errors.append("Waypoint sequence is empty")
        return errors
    
    for i, waypoint in enumerate(waypoints):
        # Validate speed
        if waypoint.speed > max_speed:
            errors.append(f"Waypoint {i+1}: Speed {waypoint.speed} exceeds maximum {max_speed}")
        
        if waypoint.speed <= 0:
            errors.append(f"Waypoint {i+1}: Invalid speed {waypoint.speed}")
        
        # Validate heading
        if not (0 <= waypoint.heading < 360):
            errors.append(f"Waypoint {i+1}: Invalid heading {waypoint.heading}")
        
        # Check heading changes (but allow U-turns in coverage patterns)
        if i > 0:
            prev_heading = waypoints[i-1].heading
            heading_change = abs(waypoint.heading - prev_heading)
            # Handle wrap-around
            if heading_change > 180:
                heading_change = 360 - heading_change
            
            # Only flag as error if it's not a typical boustrophedon U-turn (160-180°)
            # and exceeds the maximum for normal navigation
            if heading_change > max_heading_change and not (160 <= heading_change <= 180):
                errors.append(
                    f"Waypoint {i+1}: Unusual heading change {heading_change:.1f}° from previous waypoint"
                )
    
    return errors


def validate_coverage_completeness(field: Field, 
                                 waypoints: WaypointSequence,
                                 swath_width: float,
                                 min_coverage: float = 0.95) -> Dict[str, Any]:
    """
    Validate that waypoints provide adequate field coverage.
    
    Args:
        field: Field to be covered
        waypoints: Generated waypoints
        swath_width: Width of coverage swath
        min_coverage: Minimum required coverage percentage (0.0 to 1.0)
        
    Returns:
        Dictionary with coverage analysis results
    """
    try:
        field_area = field.calculate_area()
        
        # Simplified coverage calculation
        # In practice, this would involve complex geometric analysis
        total_distance = waypoints.total_distance()
        estimated_coverage_area = total_distance * swath_width
        
        coverage_percentage = min(1.0, estimated_coverage_area / field_area)
        
        result = {
            'coverage_percentage': coverage_percentage,
            'field_area_m2': field_area,
            'estimated_covered_area_m2': estimated_coverage_area,
            'meets_minimum': coverage_percentage >= min_coverage,
            'total_path_distance_m': total_distance,
            'efficiency': coverage_percentage * field_area / total_distance if total_distance > 0 else 0
        }
        
        return result
        
    except Exception as e:
        return {
            'error': str(e),
            'coverage_percentage': 0.0,
            'meets_minimum': False
        }


def validate_input_csv_format(file_path: str) -> List[str]:
    """
    Validate CSV file format for field boundary input.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        List of validation error messages
    """
    errors = []
    
    try:
        import pandas as pd
        
        # Try to read the CSV file
        df = pd.read_csv(file_path)
        
        # Check required columns
        required_columns = ['latitude', 'longitude']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")
            return errors
        
        # Check for empty file
        if len(df) == 0:
            errors.append("CSV file is empty")
            return errors
        
        # Check minimum number of rows
        if len(df) < 3:
            errors.append("CSV file must contain at least 3 coordinate pairs")
        
        # Check for valid numeric data
        for i, row in df.iterrows():
            try:
                lat = float(row['latitude'])
                lon = float(row['longitude'])
                
                if not (-90 <= lat <= 90):
                    errors.append(f"Row {i+1}: Invalid latitude {lat}")
                
                if not (-180 <= lon <= 180):
                    errors.append(f"Row {i+1}: Invalid longitude {lon}")
                    
            except (ValueError, TypeError):
                errors.append(f"Row {i+1}: Non-numeric latitude or longitude values")
        
    except FileNotFoundError:
        errors.append(f"File not found: {file_path}")
    except Exception as e:
        errors.append(f"Error reading CSV file: {str(e)}")
    
    return errors
