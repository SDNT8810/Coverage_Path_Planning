"""
Waypoint and waypoint sequence classes for path planning.
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum

from .coordinates import GPSCoordinate, UTMCoordinate


class WaypointType(Enum):
    """Types of waypoints in a coverage path."""
    COVERAGE = "coverage"
    TURN = "turn"
    START = "start"
    END = "end"
    HEADLAND = "headland"


@dataclass
class Waypoint:
    """Represents a single waypoint in a coverage path."""
    
    gps_coordinate: GPSCoordinate
    utm_coordinate: Optional[UTMCoordinate] = None
    heading: float = 0.0  # degrees, 0=North, 90=East
    speed: float = 2.0  # m/s
    waypoint_type: WaypointType = WaypointType.COVERAGE
    waypoint_id: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate waypoint data."""
        if not (0 <= self.heading < 360):
            raise ValueError(f"Invalid heading: {self.heading}. Must be between 0 and 360 degrees.")
        if self.speed < 0:
            raise ValueError(f"Invalid speed: {self.speed}. Must be non-negative.")
    
    def distance_to(self, other: 'Waypoint') -> float:
        """Calculate distance to another waypoint."""
        if self.utm_coordinate and other.utm_coordinate:
            return self.utm_coordinate.distance_to(other.utm_coordinate)
        else:
            return self.gps_coordinate.distance_to(other.gps_coordinate)
    
    def bearing_to(self, other: 'Waypoint') -> float:
        """Calculate bearing to another waypoint."""
        return self.gps_coordinate.bearing_to(other.gps_coordinate)
    
    def set_heading_to(self, other: 'Waypoint') -> None:
        """Set heading to point towards another waypoint."""
        self.heading = self.bearing_to(other)


class WaypointSequence:
    """Represents a sequence of waypoints forming a coverage path."""
    
    def __init__(self, waypoints: Optional[List[Waypoint]] = None):
        """Initialize waypoint sequence."""
        self.waypoints: List[Waypoint] = waypoints or []
        self._assign_ids()
    
    def _assign_ids(self) -> None:
        """Assign sequential IDs to waypoints."""
        for i, waypoint in enumerate(self.waypoints):
            waypoint.waypoint_id = i + 1
    
    def add_waypoint(self, waypoint: Waypoint) -> None:
        """Add a waypoint to the sequence."""
        self.waypoints.append(waypoint)
        waypoint.waypoint_id = len(self.waypoints)
    
    def insert_waypoint(self, index: int, waypoint: Waypoint) -> None:
        """Insert a waypoint at a specific index."""
        self.waypoints.insert(index, waypoint)
        self._assign_ids()
    
    def remove_waypoint(self, index: int) -> Waypoint:
        """Remove and return waypoint at index."""
        if 0 <= index < len(self.waypoints):
            waypoint = self.waypoints.pop(index)
            self._assign_ids()
            return waypoint
        else:
            raise IndexError(f"Waypoint index {index} out of range.")
    
    def get_waypoint(self, waypoint_id: int) -> Optional[Waypoint]:
        """Get waypoint by ID."""
        for waypoint in self.waypoints:
            if waypoint.waypoint_id == waypoint_id:
                return waypoint
        return None
    
    def total_distance(self) -> float:
        """Calculate total distance of the path."""
        if len(self.waypoints) < 2:
            return 0.0
        
        total_dist = 0.0
        for i in range(len(self.waypoints) - 1):
            total_dist += self.waypoints[i].distance_to(self.waypoints[i + 1])
        
        return total_dist
    
    def total_time(self) -> float:
        """Calculate total time to complete the path in seconds."""
        if len(self.waypoints) < 2:
            return 0.0
        
        total_time = 0.0
        for i in range(len(self.waypoints) - 1):
            distance = self.waypoints[i].distance_to(self.waypoints[i + 1])
            speed = self.waypoints[i].speed
            if speed > 0:
                total_time += distance / speed
        
        return total_time
    
    def update_headings(self) -> None:
        """Update headings for all waypoints to point to the next waypoint."""
        for i in range(len(self.waypoints) - 1):
            self.waypoints[i].set_heading_to(self.waypoints[i + 1])
        
        # Last waypoint keeps its current heading
        if len(self.waypoints) >= 2:
            self.waypoints[-1].heading = self.waypoints[-2].heading
    
    def smooth_headings(self, smoothing_factor: float = 0.5) -> None:
        """
        Smooth heading transitions between waypoints.
        
        Args:
            smoothing_factor: Factor for smoothing (0.0 = no smoothing, 1.0 = maximum smoothing)
        """
        if len(self.waypoints) < 3:
            return
        
        smoothed_headings = [self.waypoints[0].heading]
        
        for i in range(1, len(self.waypoints) - 1):
            prev_heading = self.waypoints[i - 1].heading
            current_heading = self.waypoints[i].heading
            next_heading = self.waypoints[i + 1].heading
            
            # Calculate average heading considering angle wrapping
            angles = [prev_heading, current_heading, next_heading]
            
            # Convert to unit vectors and average
            x_sum = sum(math.cos(math.radians(angle)) for angle in angles)
            y_sum = sum(math.sin(math.radians(angle)) for angle in angles)
            
            avg_heading = math.degrees(math.atan2(y_sum, x_sum))
            if avg_heading < 0:
                avg_heading += 360
            
            # Apply smoothing factor
            smoothed_heading = (
                current_heading * (1 - smoothing_factor) + 
                avg_heading * smoothing_factor
            )
            
            smoothed_headings.append(smoothed_heading)
        
        smoothed_headings.append(self.waypoints[-1].heading)
        
        # Update waypoint headings
        for i, heading in enumerate(smoothed_headings):
            self.waypoints[i].heading = heading % 360
    
    def get_coverage_waypoints(self) -> List[Waypoint]:
        """Get only coverage waypoints (excluding turns, etc.)."""
        return [wp for wp in self.waypoints if wp.waypoint_type == WaypointType.COVERAGE]
    
    def get_turn_waypoints(self) -> List[Waypoint]:
        """Get only turn waypoints."""
        return [wp for wp in self.waypoints if wp.waypoint_type == WaypointType.TURN]
    
    def validate(self) -> List[str]:
        """
        Validate the waypoint sequence and return list of validation errors.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        if not self.waypoints:
            errors.append("Waypoint sequence is empty")
            return errors
        
        # Check for duplicate consecutive waypoints
        for i in range(len(self.waypoints) - 1):
            if self.waypoints[i].distance_to(self.waypoints[i + 1]) < 0.1:  # 10cm threshold
                errors.append(f"Waypoints {i+1} and {i+2} are too close together")
        
        # Check for valid speeds
        for i, waypoint in enumerate(self.waypoints):
            if waypoint.speed <= 0:
                errors.append(f"Waypoint {i+1} has invalid speed: {waypoint.speed}")
        
        # Check for valid headings
        for i, waypoint in enumerate(self.waypoints):
            if not (0 <= waypoint.heading < 360):
                errors.append(f"Waypoint {i+1} has invalid heading: {waypoint.heading}")
        
        return errors
    
    def __len__(self) -> int:
        """Return number of waypoints."""
        return len(self.waypoints)
    
    def __getitem__(self, index: int) -> Waypoint:
        """Get waypoint by index."""
        return self.waypoints[index]
    
    def __iter__(self):
        """Iterate over waypoints."""
        return iter(self.waypoints)
