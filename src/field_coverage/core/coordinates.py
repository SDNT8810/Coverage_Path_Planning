"""
Coordinate system handling for GPS and UTM coordinates.
"""

import math
from dataclasses import dataclass
from typing import Tuple, List, Optional
import pyproj
from pyproj import Transformer


@dataclass
class GPSCoordinate:
    """Represents a GPS coordinate with latitude and longitude."""
    
    latitude: float
    longitude: float
    
    def __post_init__(self):
        """Validate GPS coordinates."""
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"Invalid latitude: {self.latitude}. Must be between -90 and 90.")
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"Invalid longitude: {self.longitude}. Must be between -180 and 180.")
    
    def distance_to(self, other: 'GPSCoordinate') -> float:
        """Calculate distance to another GPS coordinate using Haversine formula."""
        R = 6371000  # Earth's radius in meters
        
        lat1_rad = math.radians(self.latitude)
        lat2_rad = math.radians(other.latitude)
        dlat_rad = math.radians(other.latitude - self.latitude)
        dlon_rad = math.radians(other.longitude - self.longitude)
        
        a = (math.sin(dlat_rad / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon_rad / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def bearing_to(self, other: 'GPSCoordinate') -> float:
        """Calculate bearing to another GPS coordinate in degrees."""
        lat1_rad = math.radians(self.latitude)
        lat2_rad = math.radians(other.latitude)
        dlon_rad = math.radians(other.longitude - self.longitude)
        
        y = math.sin(dlon_rad) * math.cos(lat2_rad)
        x = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad))
        
        bearing_rad = math.atan2(y, x)
        bearing_deg = math.degrees(bearing_rad)
        
        return (bearing_deg + 360) % 360


@dataclass
class UTMCoordinate:
    """Represents a UTM coordinate with easting, northing, zone, and hemisphere."""
    
    easting: float
    northing: float
    zone: int
    hemisphere: str  # 'N' or 'S'
    
    def __post_init__(self):
        """Validate UTM coordinates."""
        if not (1 <= self.zone <= 60):
            raise ValueError(f"Invalid UTM zone: {self.zone}. Must be between 1 and 60.")
        if self.hemisphere not in ['N', 'S']:
            raise ValueError(f"Invalid hemisphere: {self.hemisphere}. Must be 'N' or 'S'.")
    
    def distance_to(self, other: 'UTMCoordinate') -> float:
        """Calculate Euclidean distance to another UTM coordinate."""
        if self.zone != other.zone or self.hemisphere != other.hemisphere:
            raise ValueError("Cannot calculate distance between different UTM zones/hemispheres.")
        
        dx = self.easting - other.easting
        dy = self.northing - other.northing
        return math.sqrt(dx ** 2 + dy ** 2)


class CoordinateTransformer:
    """Handles coordinate transformations between GPS and UTM systems."""
    
    def __init__(self, utm_zone: Optional[int] = None, hemisphere: Optional[str] = None):
        """
        Initialize coordinate transformer.
        
        Args:
            utm_zone: UTM zone number (1-60). If None, will be auto-detected.
            hemisphere: 'N' or 'S'. If None, will be auto-detected.
        """
        self.utm_zone = utm_zone
        self.hemisphere = hemisphere
        self._transformer_to_utm = None
        self._transformer_to_gps = None
    
    def _get_utm_zone(self, longitude: float) -> int:
        """Calculate UTM zone from longitude."""
        return int((longitude + 180) / 6) + 1
    
    def _get_hemisphere(self, latitude: float) -> str:
        """Determine hemisphere from latitude."""
        return 'N' if latitude >= 0 else 'S'
    
    def _setup_transformers(self, gps_coord: GPSCoordinate):
        """Setup coordinate transformers based on GPS coordinate."""
        if self.utm_zone is None:
            self.utm_zone = self._get_utm_zone(gps_coord.longitude)
        if self.hemisphere is None:
            self.hemisphere = self._get_hemisphere(gps_coord.latitude)
        
        # Create CRS strings
        gps_crs = "EPSG:4326"  # WGS84
        utm_crs = f"EPSG:326{self.utm_zone:02d}" if self.hemisphere == 'N' else f"EPSG:327{self.utm_zone:02d}"
        
        self._transformer_to_utm = Transformer.from_crs(gps_crs, utm_crs, always_xy=True)
        self._transformer_to_gps = Transformer.from_crs(utm_crs, gps_crs, always_xy=True)
    
    def gps_to_utm(self, gps_coord: GPSCoordinate) -> UTMCoordinate:
        """Convert GPS coordinate to UTM."""
        if self._transformer_to_utm is None:
            self._setup_transformers(gps_coord)
        
        easting, northing = self._transformer_to_utm.transform(
            gps_coord.longitude, gps_coord.latitude
        )
        
        return UTMCoordinate(
            easting=easting,
            northing=northing,
            zone=self.utm_zone,
            hemisphere=self.hemisphere
        )
    
    def utm_to_gps(self, utm_coord: UTMCoordinate) -> GPSCoordinate:
        """Convert UTM coordinate to GPS."""
        if self._transformer_to_gps is None:
            # Setup with dummy GPS coordinate for zone info
            dummy_gps = GPSCoordinate(0.0, 0.0)
            self.utm_zone = utm_coord.zone
            self.hemisphere = utm_coord.hemisphere
            self._setup_transformers(dummy_gps)
        
        longitude, latitude = self._transformer_to_gps.transform(
            utm_coord.easting, utm_coord.northing
        )
        
        return GPSCoordinate(latitude=latitude, longitude=longitude)
    
    def gps_list_to_utm(self, gps_coords: List[GPSCoordinate]) -> List[UTMCoordinate]:
        """Convert a list of GPS coordinates to UTM."""
        if not gps_coords:
            return []
        
        # Use first coordinate to setup transformers
        if self._transformer_to_utm is None:
            self._setup_transformers(gps_coords[0])
        
        utm_coords = []
        for gps_coord in gps_coords:
            utm_coords.append(self.gps_to_utm(gps_coord))
        
        return utm_coords
    
    def utm_list_to_gps(self, utm_coords: List[UTMCoordinate]) -> List[GPSCoordinate]:
        """Convert a list of UTM coordinates to GPS."""
        return [self.utm_to_gps(utm_coord) for utm_coord in utm_coords]
