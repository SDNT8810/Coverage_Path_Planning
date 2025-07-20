"""
Boustrophedon (back-and-forth) coverage path planning algorithm with proper direction handling and optimization.
"""

import math
from typing import List, Tuple, Optional
from shapely.geometry import LineString, Point
import numpy as np

from ..core.field import Field
from ..core.waypoint import Waypoint, WaypointSequence, WaypointType
from ..core.coordinates import GPSCoordinate, UTMCoordinate, CoordinateTransformer


class BoustrophedonPlanner:
    """
    Implements boustrophedon (back-and-forth) coverage pattern planning with proper direction handling and optimization.
    """
    
    def __init__(self, 
                 swath_width: float = 2.0,
                 overlap: float = 0.1,
                 turn_radius: float = 2.0,
                 speed: float = 2.0):
        """
        Initialize boustrophedon planner.
        
        Args:
            swath_width: Width of each coverage swath in meters
            overlap: Overlap between swaths as fraction (0.0 to 1.0)
            turn_radius: Minimum turning radius in meters
            speed: Default speed for waypoints in m/s
        """
        self.swath_width = swath_width
        self.overlap = overlap
        self.turn_radius = turn_radius
        self.speed = speed
        self.coordinate_transformer = CoordinateTransformer()
    
    def plan_coverage(self, 
                     field: Field,
                     direction: Optional[float] = None,
                     start_point: Optional[UTMCoordinate] = None,
                     optimization_step: float = 15.0) -> WaypointSequence:
        """
        Generate boustrophedon coverage pattern that respects field boundaries.
        
        Args:
            field: Field to cover
            direction: Coverage direction in degrees (0=North, 90=East). If None, optimizes automatically.
            start_point: Starting point for coverage
            optimization_step: Step size in degrees for optimization when direction is None (default: 15.0)
            
        Returns:
            WaypointSequence with coverage waypoints
        """
        # Determine coverage direction
        if direction is None:
            print("🔍 Optimizing coverage direction...")
            direction = self.optimize_direction(field, step_size=optimization_step)
            print(f"✓ Optimal direction found: {direction:.1f}°")
        else:
            print(f"📐 Using specified direction: {direction:.1f}°")
        
        # Get field bounding box and working area polygon
        min_bbox, max_bbox = field.get_bounding_box()
        field_polygon = field.get_working_area_polygon(use_utm=True)
        
        # Use field's coordinate transformer
        transformer = field.coordinate_transformer
        
        # Calculate effective swath spacing
        effective_swath_width = self.swath_width * (1 - self.overlap)
        
        waypoints = []
        waypoint_id = 1
        
        # Convert direction to radians for calculations
        direction_rad = math.radians(direction)
        
        # Calculate scan line direction (perpendicular to coverage direction)
        scan_direction_rad = direction_rad + math.pi / 2
        
        # Get field bounds
        minx, miny, maxx, maxy = field_polygon.bounds
        field_center_x = (minx + maxx) / 2
        field_center_y = (miny + maxy) / 2
        
        # Calculate the extent needed to cover the entire field
        diagonal = math.sqrt((maxx - minx)**2 + (maxy - miny)**2)
        
        # Calculate number of scan lines needed
        # Project field diagonal onto perpendicular direction to get coverage width
        field_width_in_scan_dir = diagonal  # Conservative estimate
        num_lines = int(field_width_in_scan_dir / effective_swath_width) + 2
        
        # Generate scan lines perpendicular to coverage direction
        for i in range(-num_lines//2, num_lines//2 + 1):
            # Calculate offset from center in scan direction
            offset = i * effective_swath_width
            
            # Calculate scan line center point
            scan_center_x = field_center_x + offset * math.cos(scan_direction_rad)
            scan_center_y = field_center_y + offset * math.sin(scan_direction_rad)
            
            # Create scan line extending beyond field bounds
            line_half_length = diagonal
            
            # Start and end points of scan line in coverage direction
            start_x = scan_center_x - line_half_length * math.cos(direction_rad)
            start_y = scan_center_y - line_half_length * math.sin(direction_rad)
            end_x = scan_center_x + line_half_length * math.cos(direction_rad)
            end_y = scan_center_y + line_half_length * math.sin(direction_rad)
            
            # Create line and find intersections with field boundary
            coverage_line = LineString([(start_x, start_y), (end_x, end_y)])
            
            # Find intersection with field polygon
            intersection = field_polygon.intersection(coverage_line)
            
            if intersection.is_empty:
                continue
                
            # Handle different intersection types
            if hasattr(intersection, 'geoms'):  # MultiLineString
                line_segments = list(intersection.geoms)
            else:  # Single LineString
                line_segments = [intersection] if hasattr(intersection, 'coords') else []
            
            # Process each line segment
            for segment in line_segments:
                if not hasattr(segment, 'coords'):
                    continue
                    
                coords = list(segment.coords)
                if len(coords) < 2:
                    continue
                
                # Determine direction for boustrophedon pattern
                line_index = i + num_lines//2  # Convert to 0-based index
                if line_index % 2 == 0:
                    # Forward direction (keep original order)
                    heading = direction
                    start_coord = coords[0]
                    end_coord = coords[-1]
                else:
                    # Reverse direction for boustrophedon pattern
                    heading = (direction + 180) % 360
                    start_coord = coords[-1]
                    end_coord = coords[0]
                
                # Create waypoints for this line segment
                line_waypoints = self._create_line_waypoints(
                    start_coord[0], start_coord[1], 
                    end_coord[0], end_coord[1], 
                    transformer, waypoint_id, heading
                )
                waypoints.extend(line_waypoints)
                waypoint_id += len(line_waypoints)
        
        return WaypointSequence(waypoints)
    
    def _create_line_waypoints(self,
                             x1: float, y1: float,
                             x2: float, y2: float,
                             transformer: CoordinateTransformer,
                             start_id: int,
                             heading: float,
                             sampling_distance: float = 10.0) -> List[Waypoint]:
        """
        Create waypoints along a line.
        
        Args:
            x1, y1: Start coordinates in UTM
            x2, y2: End coordinates in UTM
            transformer: Coordinate transformer
            start_id: Starting waypoint ID
            heading: Heading for waypoints
            sampling_distance: Distance between waypoints in meters
            
        Returns:
            List of waypoints along the line
        """
        waypoints = []
        
        # Calculate line length and direction
        dx = x2 - x1
        dy = y2 - y1
        length = math.sqrt(dx**2 + dy**2)
        
        if length < sampling_distance:
            # Line is short, just create start and end points
            points = [(x1, y1), (x2, y2)]
        else:
            # Sample points along the line
            num_points = max(2, int(length / sampling_distance) + 1)
            points = []
            
            for i in range(num_points):
                t = i / (num_points - 1)
                x = x1 + t * dx
                y = y1 + t * dy
                points.append((x, y))
        
        # Create waypoints
        for i, (x, y) in enumerate(points):
            utm_coord = UTMCoordinate(
                easting=x, northing=y,
                zone=transformer.utm_zone,
                hemisphere=transformer.hemisphere
            )
            
            gps_coord = transformer.utm_to_gps(utm_coord)
            
            waypoint = Waypoint(
                gps_coordinate=gps_coord,
                utm_coordinate=utm_coord,
                heading=heading,
                speed=self.speed,
                waypoint_type=WaypointType.COVERAGE,
                waypoint_id=start_id + i
            )
            waypoints.append(waypoint)
        
        return waypoints
    
    def optimize_direction(self, field: Field, step_size: float = 15.0) -> float:
        """
        Find the optimal coverage direction to minimize total path length.
        This tests multiple directions and selects the one with minimum travel distance.
        
        Args:
            field: Field to optimize for
            step_size: Step size in degrees for testing directions (default: 15.0)
            
        Returns:
            Optimal direction in degrees (0-179, since 180+ is equivalent to 0-179)
        """
        # Test directions with specified step size from 0 to 180-step_size
        max_angle = 180
        test_directions = []
        angle = 0
        while angle < max_angle:
            test_directions.append(angle)
            angle += step_size
        
        print(f"  Testing {len(test_directions)} directions (step: {step_size}°)...")
        
        # First pass: calculate all path lengths
        results = []
        best_direction = 0
        min_path_length = float('inf')
        
        for direction in test_directions:
            try:
                waypoints = self._generate_test_coverage(field, direction)
                path_length = waypoints.total_distance()
                results.append((direction, path_length))
                
                if path_length < min_path_length:
                    min_path_length = path_length
                    best_direction = direction
            except Exception as e:
                print(f"    Direction {direction:6.1f}°: Error - {e}")
                results.append((direction, None))
                continue
        
        # Second pass: print results with star for best direction
        for direction, path_length in results:
            if path_length is not None:
                marker = " ⭐" if direction == best_direction else ""
                print(f"    Direction {direction:6.1f}°: {path_length:8.1f}m total path{marker}")
        
        print(f"  Best direction: {best_direction}° with {min_path_length:.1f}m total path")
        return best_direction
    
    def _generate_test_coverage(self, field: Field, direction: float) -> WaypointSequence:
        """
        Generate test coverage for optimization (simplified version).
        """
        # Temporarily disable print statements for test coverage
        original_plan = self.plan_coverage
        
        # Create a simplified version that doesn't print
        field_polygon = field.get_working_area_polygon(use_utm=True)
        transformer = field.coordinate_transformer
        effective_swath_width = self.swath_width * (1 - self.overlap)
        
        waypoints = []
        waypoint_id = 1
        
        # Convert direction to radians for calculations
        direction_rad = math.radians(direction)
        scan_direction_rad = direction_rad + math.pi / 2
        
        # Get field bounds
        minx, miny, maxx, maxy = field_polygon.bounds
        field_center_x = (minx + maxx) / 2
        field_center_y = (miny + maxy) / 2
        diagonal = math.sqrt((maxx - minx)**2 + (maxy - miny)**2)
        
        # Calculate number of scan lines needed
        field_width_in_scan_dir = diagonal
        num_lines = int(field_width_in_scan_dir / effective_swath_width) + 2
        
        # Generate scan lines
        for i in range(-num_lines//2, num_lines//2 + 1):
            offset = i * effective_swath_width
            scan_center_x = field_center_x + offset * math.cos(scan_direction_rad)
            scan_center_y = field_center_y + offset * math.sin(scan_direction_rad)
            
            line_half_length = diagonal
            start_x = scan_center_x - line_half_length * math.cos(direction_rad)
            start_y = scan_center_y - line_half_length * math.sin(direction_rad)
            end_x = scan_center_x + line_half_length * math.cos(direction_rad)
            end_y = scan_center_y + line_half_length * math.sin(direction_rad)
            
            coverage_line = LineString([(start_x, start_y), (end_x, end_y)])
            intersection = field_polygon.intersection(coverage_line)
            
            if intersection.is_empty:
                continue
                
            if hasattr(intersection, 'geoms'):
                line_segments = list(intersection.geoms)
            else:
                line_segments = [intersection] if hasattr(intersection, 'coords') else []
            
            for segment in line_segments:
                if not hasattr(segment, 'coords'):
                    continue
                    
                coords = list(segment.coords)
                if len(coords) < 2:
                    continue
                
                line_index = i + num_lines//2
                if line_index % 2 == 0:
                    heading = direction
                    start_coord = coords[0]
                    end_coord = coords[-1]
                else:
                    heading = (direction + 180) % 360
                    start_coord = coords[-1]
                    end_coord = coords[0]
                
                line_waypoints = self._create_line_waypoints(
                    start_coord[0], start_coord[1], 
                    end_coord[0], end_coord[1], 
                    transformer, waypoint_id, heading, 20.0  # Larger sampling for speed
                )
                waypoints.extend(line_waypoints)
                waypoint_id += len(line_waypoints)
        
        return WaypointSequence(waypoints)
    
    def calculate_coverage_area(self, waypoints: WaypointSequence) -> float:
        """
        Calculate the area covered by the waypoint sequence.
        
        Args:
            waypoints: Coverage waypoint sequence
            
        Returns:
            Estimated coverage area in square meters
        """
        coverage_waypoints = waypoints.get_coverage_waypoints()
        
        if len(coverage_waypoints) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(len(coverage_waypoints) - 1):
            total_distance += coverage_waypoints[i].distance_to(coverage_waypoints[i + 1])
        
        return total_distance * self.swath_width
