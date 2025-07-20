"""
Field representation and management for coverage path planning.
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
import numpy as np

from .coordinates import GPSCoordinate, UTMCoordinate, CoordinateTransformer


@dataclass
class FieldBoundary:
    """Represents a field boundary as a polygon."""
    
    gps_coordinates: List[GPSCoordinate]
    utm_coordinates: Optional[List[UTMCoordinate]] = None
    is_hole: bool = False  # True if this boundary represents a hole/obstacle
    
    def __post_init__(self):
        """Validate field boundary."""
        if len(self.gps_coordinates) < 3:
            raise ValueError("Field boundary must have at least 3 coordinates.")
        
        # Ensure polygon is closed
        if (self.gps_coordinates[0].latitude != self.gps_coordinates[-1].latitude or
            self.gps_coordinates[0].longitude != self.gps_coordinates[-1].longitude):
            self.gps_coordinates.append(self.gps_coordinates[0])
    
    def to_shapely_polygon(self, use_utm: bool = True) -> Polygon:
        """Convert to Shapely polygon for geometric operations."""
        if use_utm and self.utm_coordinates:
            coords = [(utm.easting, utm.northing) for utm in self.utm_coordinates]
        else:
            coords = [(gps.longitude, gps.latitude) for gps in self.gps_coordinates]
        
        return Polygon(coords)


class Field:
    """
    Represents an agricultural field with boundaries and obstacles.
    """
    
    def __init__(self, 
                 main_boundary: FieldBoundary,
                 holes: Optional[List[FieldBoundary]] = None,
                 field_id: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a field.
        
        Args:
            main_boundary: Main field boundary
            holes: List of holes/obstacles within the field
            field_id: Unique identifier for the field
            metadata: Additional field metadata
        """
        self.main_boundary = main_boundary
        self.holes = holes or []
        self.field_id = field_id
        self.metadata = metadata or {}
        self.coordinate_transformer = CoordinateTransformer()
        
        # Convert to UTM coordinates if not already done
        self._ensure_utm_coordinates()
        
        # Validate field geometry
        self._validate_field()
    
    def _ensure_utm_coordinates(self) -> None:
        """Ensure all boundaries have UTM coordinates."""
        # Convert main boundary
        if self.main_boundary.utm_coordinates is None:
            self.main_boundary.utm_coordinates = (
                self.coordinate_transformer.gps_list_to_utm(self.main_boundary.gps_coordinates)
            )
        
        # Convert holes
        for hole in self.holes:
            if hole.utm_coordinates is None:
                hole.utm_coordinates = (
                    self.coordinate_transformer.gps_list_to_utm(hole.gps_coordinates)
                )
    
    def _validate_field(self) -> None:
        """Validate field geometry."""
        # Check if main boundary is a valid polygon
        main_poly = self.main_boundary.to_shapely_polygon(use_utm=True)
        if not main_poly.is_valid:
            raise ValueError("Main field boundary is not a valid polygon.")
        
        # Check if holes are within the main boundary and don't overlap
        for i, hole in enumerate(self.holes):
            hole_poly = hole.to_shapely_polygon(use_utm=True)
            
            if not hole_poly.is_valid:
                raise ValueError(f"Hole {i} is not a valid polygon.")
            
            if not main_poly.contains(hole_poly):
                raise ValueError(f"Hole {i} is not completely within the main boundary.")
            
            # Check for overlapping holes
            for j, other_hole in enumerate(self.holes[i+1:], i+1):
                other_poly = other_hole.to_shapely_polygon(use_utm=True)
                if hole_poly.intersects(other_poly):
                    raise ValueError(f"Hole {i} overlaps with hole {j}.")
    
    def get_working_area_polygon(self, use_utm: bool = True) -> Polygon:
        """
        Get the working area polygon (main boundary minus holes).
        
        Args:
            use_utm: Whether to use UTM coordinates (True) or GPS (False)
            
        Returns:
            Shapely polygon representing the working area
        """
        main_poly = self.main_boundary.to_shapely_polygon(use_utm=use_utm)
        
        if not self.holes:
            return main_poly
        
        # Subtract holes from main polygon
        hole_polys = [hole.to_shapely_polygon(use_utm=use_utm) for hole in self.holes]
        union_holes = unary_union(hole_polys)
        
        return main_poly.difference(union_holes)
    
    def calculate_area(self) -> float:
        """
        Calculate the working area of the field in square meters.
        
        Returns:
            Area in square meters
        """
        working_area = self.get_working_area_polygon(use_utm=True)
        return working_area.area
    
    def calculate_perimeter(self) -> float:
        """
        Calculate the perimeter of the working area in meters.
        
        Returns:
            Perimeter in meters
        """
        working_area = self.get_working_area_polygon(use_utm=True)
        return working_area.length
    
    def get_centroid(self) -> Tuple[GPSCoordinate, UTMCoordinate]:
        """
        Get the centroid of the working area.
        
        Returns:
            Tuple of (GPS coordinate, UTM coordinate) of centroid
        """
        working_area = self.get_working_area_polygon(use_utm=True)
        centroid_point = working_area.centroid
        
        utm_centroid = UTMCoordinate(
            easting=centroid_point.x,
            northing=centroid_point.y,
            zone=self.coordinate_transformer.utm_zone,
            hemisphere=self.coordinate_transformer.hemisphere
        )
        
        gps_centroid = self.coordinate_transformer.utm_to_gps(utm_centroid)
        
        return gps_centroid, utm_centroid
    
    def get_bounding_box(self) -> Tuple[UTMCoordinate, UTMCoordinate]:
        """
        Get the bounding box of the working area.
        
        Returns:
            Tuple of (min_coordinate, max_coordinate) in UTM
        """
        working_area = self.get_working_area_polygon(use_utm=True)
        minx, miny, maxx, maxy = working_area.bounds
        
        min_coord = UTMCoordinate(
            easting=minx,
            northing=miny,
            zone=self.coordinate_transformer.utm_zone,
            hemisphere=self.coordinate_transformer.hemisphere
        )
        
        max_coord = UTMCoordinate(
            easting=maxx,
            northing=maxy,
            zone=self.coordinate_transformer.utm_zone,
            hemisphere=self.coordinate_transformer.hemisphere
        )
        
        return min_coord, max_coord
    
    def calculate_optimal_direction(self) -> float:
        """
        Calculate the optimal direction for coverage patterns based on field shape.
        Uses a simple heuristic based on field dimensions.
        For advanced optimization, use BoustrophedonPlanner.optimize_direction() directly.
        
        Returns:
            Optimal direction in degrees (0 = North, 90 = East)
        """
        # Get the minimum bounding rectangle
        working_area = self.get_working_area_polygon(use_utm=True)
        
        # For simple approach, use the longest side of the bounding box
        minx, miny, maxx, maxy = working_area.bounds
        width = maxx - minx
        height = maxy - miny
        
        if width > height:
            # Field is wider than tall, optimal direction is North-South (0 degrees)
            return 0.0
        else:
            # Field is taller than wide, optimal direction is East-West (90 degrees)
            return 90.0
    
    def contains_point(self, point: UTMCoordinate) -> bool:
        """
        Check if a point is within the working area of the field.
        
        Args:
            point: UTM coordinate to check
            
        Returns:
            True if point is within the working area
        """
        working_area = self.get_working_area_polygon(use_utm=True)
        shapely_point = Point(point.easting, point.northing)
        return working_area.contains(shapely_point)
    
    def get_intersection_points(self, line: LineString) -> List[Point]:
        """
        Find intersection points between a line and the field boundary.
        
        Args:
            line: Shapely LineString to intersect with field
            
        Returns:
            List of intersection points
        """
        working_area = self.get_working_area_polygon(use_utm=True)
        intersection = working_area.intersection(line)
        
        points = []
        if hasattr(intersection, 'geoms'):
            # MultiPoint or GeometryCollection
            for geom in intersection.geoms:
                if geom.geom_type == 'Point':
                    points.append(geom)
        elif intersection.geom_type == 'Point':
            points.append(intersection)
        
        return points
    
    def add_hole(self, hole_boundary: FieldBoundary) -> None:
        """
        Add a hole/obstacle to the field.
        
        Args:
            hole_boundary: Boundary of the hole to add
        """
        # Ensure UTM coordinates
        if hole_boundary.utm_coordinates is None:
            hole_boundary.utm_coordinates = (
                self.coordinate_transformer.gps_list_to_utm(hole_boundary.gps_coordinates)
            )
        
        hole_boundary.is_hole = True
        self.holes.append(hole_boundary)
        
        # Re-validate field
        self._validate_field()
    
    def remove_hole(self, hole_index: int) -> FieldBoundary:
        """
        Remove a hole from the field.
        
        Args:
            hole_index: Index of the hole to remove
            
        Returns:
            The removed hole boundary
        """
        if 0 <= hole_index < len(self.holes):
            return self.holes.pop(hole_index)
        else:
            raise IndexError(f"Hole index {hole_index} out of range.")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert field to dictionary representation.
        
        Returns:
            Dictionary representation of the field
        """
        return {
            'field_id': self.field_id,
            'main_boundary': {
                'gps_coordinates': [
                    {'latitude': coord.latitude, 'longitude': coord.longitude}
                    for coord in self.main_boundary.gps_coordinates
                ]
            },
            'holes': [
                {
                    'gps_coordinates': [
                        {'latitude': coord.latitude, 'longitude': coord.longitude}
                        for coord in hole.gps_coordinates
                    ]
                }
                for hole in self.holes
            ],
            'area_m2': self.calculate_area(),
            'perimeter_m': self.calculate_perimeter(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_gps_coordinates(cls, 
                           coordinates: List[GPSCoordinate],
                           holes: Optional[List[List[GPSCoordinate]]] = None,
                           field_id: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> 'Field':
        """
        Create a field from GPS coordinates.
        
        Args:
            coordinates: GPS coordinates of the main boundary
            holes: List of hole boundaries (each as list of GPS coordinates)
            field_id: Unique identifier for the field
            metadata: Additional field metadata
            
        Returns:
            New Field instance
        """
        main_boundary = FieldBoundary(gps_coordinates=coordinates)
        
        hole_boundaries = []
        if holes:
            for hole_coords in holes:
                hole_boundaries.append(FieldBoundary(
                    gps_coordinates=hole_coords,
                    is_hole=True
                ))
        
        return cls(
            main_boundary=main_boundary,
            holes=hole_boundaries,
            field_id=field_id,
            metadata=metadata
        )
