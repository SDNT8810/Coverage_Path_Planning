"""
Core data structures and classes for field coverage path planning.
"""

from .coordinates import GPSCoordinate, UTMCoordinate, CoordinateTransformer
from .field import Field, FieldBoundary
from .waypoint import Waypoint, WaypointSequence, WaypointType

__all__ = [
    "GPSCoordinate",
    "UTMCoordinate", 
    "CoordinateTransformer",
    "Field",
    "FieldBoundary",
    "Waypoint",
    "WaypointSequence",
    "WaypointType",
]
