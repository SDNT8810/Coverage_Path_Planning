"""
Geometric utility functions for field coverage path planning.
"""

import math
from typing import List, Tuple, Optional
from shapely.geometry import Polygon, Point, LineString, MultiLineString
from shapely.ops import linemerge, unary_union
import numpy as np


def calculate_polygon_area(coordinates: List[Tuple[float, float]]) -> float:
    """
    Calculate the area of a polygon using the shoelace formula.
    
    Args:
        coordinates: List of (x, y) coordinate tuples
        
    Returns:
        Area of the polygon
    """
    if len(coordinates) < 3:
        return 0.0
    
    area = 0.0
    n = len(coordinates)
    
    for i in range(n):
        j = (i + 1) % n
        area += coordinates[i][0] * coordinates[j][1]
        area -= coordinates[j][0] * coordinates[i][1]
    
    return abs(area) / 2.0


def calculate_polygon_centroid(coordinates: List[Tuple[float, float]]) -> Tuple[float, float]:
    """
    Calculate the centroid of a polygon.
    
    Args:
        coordinates: List of (x, y) coordinate tuples
        
    Returns:
        (x, y) coordinates of the centroid
    """
    if len(coordinates) < 3:
        raise ValueError("Polygon must have at least 3 coordinates")
    
    area = calculate_polygon_area(coordinates)
    if area == 0:
        raise ValueError("Polygon has zero area")
    
    cx = 0.0
    cy = 0.0
    n = len(coordinates)
    
    for i in range(n):
        j = (i + 1) % n
        factor = coordinates[i][0] * coordinates[j][1] - coordinates[j][0] * coordinates[i][1]
        cx += (coordinates[i][0] + coordinates[j][0]) * factor
        cy += (coordinates[i][1] + coordinates[j][1]) * factor
    
    factor = 1.0 / (6.0 * area)
    return (cx * factor, cy * factor)


def point_to_line_distance(point: Tuple[float, float], 
                          line_start: Tuple[float, float], 
                          line_end: Tuple[float, float]) -> float:
    """
    Calculate the perpendicular distance from a point to a line segment.
    
    Args:
        point: (x, y) coordinates of the point
        line_start: (x, y) coordinates of line start
        line_end: (x, y) coordinates of line end
        
    Returns:
        Distance from point to line
    """
    x0, y0 = point
    x1, y1 = line_start
    x2, y2 = line_end
    
    # Calculate line length squared
    line_length_sq = (x2 - x1) ** 2 + (y2 - y1) ** 2
    
    if line_length_sq == 0:
        # Line is actually a point
        return math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)
    
    # Parameter t that represents position of the closest point on the line
    t = max(0, min(1, ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / line_length_sq))
    
    # Closest point on the line
    closest_x = x1 + t * (x2 - x1)
    closest_y = y1 + t * (y2 - y1)
    
    # Distance from point to closest point on line
    return math.sqrt((x0 - closest_x) ** 2 + (y0 - closest_y) ** 2)


def line_polygon_intersection(line_start: Tuple[float, float],
                            line_end: Tuple[float, float],
                            polygon_coords: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    Find intersection points between a line and a polygon.
    
    Args:
        line_start: Start point of the line
        line_end: End point of the line
        polygon_coords: List of polygon coordinates
        
    Returns:
        List of intersection points
    """
    line = LineString([line_start, line_end])
    polygon = Polygon(polygon_coords)
    
    intersection = polygon.boundary.intersection(line)
    
    points = []
    if hasattr(intersection, 'geoms'):
        # Multiple intersection points
        for geom in intersection.geoms:
            if geom.geom_type == 'Point':
                points.append((geom.x, geom.y))
    elif intersection.geom_type == 'Point':
        points.append((intersection.x, intersection.y))
    
    return points


def create_parallel_lines(base_line: LineString,
                         distance: float,
                         num_lines: int,
                         side: str = 'both') -> List[LineString]:
    """
    Create parallel lines to a base line.
    
    Args:
        base_line: Base line to create parallels from
        distance: Distance between parallel lines
        num_lines: Number of parallel lines to create on each side
        side: 'left', 'right', or 'both'
        
    Returns:
        List of parallel LineString objects
    """
    parallel_lines = []
    
    if side in ['left', 'both']:
        for i in range(1, num_lines + 1):
            offset_line = base_line.parallel_offset(i * distance, 'left')
            if isinstance(offset_line, LineString):
                parallel_lines.append(offset_line)
            elif isinstance(offset_line, MultiLineString):
                parallel_lines.extend(list(offset_line.geoms))
    
    if side in ['right', 'both']:
        for i in range(1, num_lines + 1):
            offset_line = base_line.parallel_offset(i * distance, 'right')
            if isinstance(offset_line, LineString):
                parallel_lines.append(offset_line)
            elif isinstance(offset_line, MultiLineString):
                parallel_lines.extend(list(offset_line.geoms))
    
    return parallel_lines


def clip_line_to_polygon(line: LineString, polygon: Polygon) -> List[LineString]:
    """
    Clip a line to be within a polygon boundary.
    
    Args:
        line: LineString to clip
        polygon: Polygon to clip to
        
    Returns:
        List of clipped LineString segments
    """
    intersection = polygon.intersection(line)
    
    lines = []
    if hasattr(intersection, 'geoms'):
        for geom in intersection.geoms:
            if geom.geom_type == 'LineString':
                lines.append(geom)
    elif intersection.geom_type == 'LineString':
        lines.append(intersection)
    
    return lines


def calculate_line_angle(start_point: Tuple[float, float], 
                        end_point: Tuple[float, float]) -> float:
    """
    Calculate the angle of a line in degrees.
    
    Args:
        start_point: (x, y) coordinates of line start
        end_point: (x, y) coordinates of line end
        
    Returns:
        Angle in degrees (0 = East, 90 = North)
    """
    dx = end_point[0] - start_point[0]
    dy = end_point[1] - start_point[1]
    
    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(angle_rad)
    
    # Convert to standard navigation angle (0 = North, 90 = East)
    nav_angle = (90 - angle_deg) % 360
    
    return nav_angle


def rotate_point(point: Tuple[float, float], 
                center: Tuple[float, float], 
                angle_deg: float) -> Tuple[float, float]:
    """
    Rotate a point around a center point by a given angle.
    
    Args:
        point: Point to rotate
        center: Center of rotation
        angle_deg: Rotation angle in degrees
        
    Returns:
        Rotated point coordinates
    """
    angle_rad = math.radians(angle_deg)
    cos_angle = math.cos(angle_rad)
    sin_angle = math.sin(angle_rad)
    
    # Translate point to origin
    x = point[0] - center[0]
    y = point[1] - center[1]
    
    # Rotate
    rotated_x = x * cos_angle - y * sin_angle
    rotated_y = x * sin_angle + y * cos_angle
    
    # Translate back
    return (rotated_x + center[0], rotated_y + center[1])


def simplify_polygon(coordinates: List[Tuple[float, float]], 
                    tolerance: float = 1.0) -> List[Tuple[float, float]]:
    """
    Simplify a polygon by removing unnecessary points.
    
    Args:
        coordinates: List of polygon coordinates
        tolerance: Simplification tolerance in meters
        
    Returns:
        Simplified polygon coordinates
    """
    if len(coordinates) <= 3:
        return coordinates
    
    polygon = Polygon(coordinates)
    simplified = polygon.simplify(tolerance, preserve_topology=True)
    
    return list(simplified.exterior.coords[:-1])  # Remove duplicate last point


def calculate_turning_radius(speed: float, max_lateral_acceleration: float = 2.0) -> float:
    """
    Calculate minimum turning radius based on speed and acceleration limits.
    
    Args:
        speed: Vehicle speed in m/s
        max_lateral_acceleration: Maximum lateral acceleration in m/s²
        
    Returns:
        Minimum turning radius in meters
    """
    if max_lateral_acceleration <= 0:
        raise ValueError("Maximum lateral acceleration must be positive")
    
    return speed ** 2 / max_lateral_acceleration


def generate_turn_waypoints(start_point: Tuple[float, float],
                          end_point: Tuple[float, float],
                          turn_radius: float,
                          num_points: int = 10) -> List[Tuple[float, float]]:
    """
    Generate waypoints for a smooth turn between two points.
    
    Args:
        start_point: Starting point of the turn
        end_point: Ending point of the turn
        turn_radius: Radius of the turn
        num_points: Number of waypoints to generate
        
    Returns:
        List of turn waypoints
    """
    if num_points < 2:
        return [start_point, end_point]
    
    # For simplicity, generate a straight line with intermediate points
    # In a real implementation, this would generate circular arc waypoints
    waypoints = []
    
    for i in range(num_points):
        t = i / (num_points - 1)
        x = start_point[0] + t * (end_point[0] - start_point[0])
        y = start_point[1] + t * (end_point[1] - start_point[1])
        waypoints.append((x, y))
    
    return waypoints
