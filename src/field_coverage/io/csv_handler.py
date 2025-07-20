"""
CSV file handling for input and output operations.
"""

import csv
from pathlib import Path
from typing import List, Optional, Dict, Any
import pandas as pd

from ..core.coordinates import GPSCoordinate
from ..core.field import Field, FieldBoundary
from ..core.waypoint import WaypointSequence, Waypoint, WaypointType
from ..utils.validation import validate_input_csv_format


class CSVHandler:
    """Handles CSV file input and output operations."""
    
    @staticmethod
    def read_field_boundary_csv(file_path: str, 
                               validate: bool = True) -> List[GPSCoordinate]:
        """
        Read field boundary coordinates from CSV file.
        
        Args:
            file_path: Path to CSV file containing GPS coordinates
            validate: Whether to validate the CSV format
            
        Returns:
            List of GPS coordinates representing field boundary
            
        Raises:
            ValueError: If CSV format is invalid
            FileNotFoundError: If file doesn't exist
        """
        # Validate file format if requested
        if validate:
            errors = validate_input_csv_format(file_path)
            if errors:
                raise ValueError(f"Invalid CSV format: {'; '.join(errors)}")
        
        coordinates = []
        
        try:
            df = pd.read_csv(file_path)
            
            for _, row in df.iterrows():
                coordinate = GPSCoordinate(
                    latitude=float(row['latitude']),
                    longitude=float(row['longitude'])
                )
                coordinates.append(coordinate)
            
            return coordinates
            
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {str(e)}")
    
    @staticmethod
    def read_field_with_holes_csv(main_boundary_file: str,
                                 hole_files: Optional[List[str]] = None,
                                 field_id: Optional[str] = None) -> Field:
        """
        Read a complete field definition from CSV files.
        
        Args:
            main_boundary_file: Path to main boundary CSV file
            hole_files: List of paths to hole boundary CSV files
            field_id: Optional field identifier
            
        Returns:
            Field object with boundaries and holes
        """
        # Read main boundary
        main_coords = CSVHandler.read_field_boundary_csv(main_boundary_file)
        main_boundary = FieldBoundary(gps_coordinates=main_coords)
        
        # Read holes if provided
        holes = []
        if hole_files:
            for hole_file in hole_files:
                hole_coords = CSVHandler.read_field_boundary_csv(hole_file)
                hole_boundary = FieldBoundary(
                    gps_coordinates=hole_coords,
                    is_hole=True
                )
                holes.append(hole_boundary)
        
        return Field(
            main_boundary=main_boundary,
            holes=holes,
            field_id=field_id or Path(main_boundary_file).stem
        )
    
    @staticmethod
    def write_waypoints_csv(waypoints: WaypointSequence,
                           file_path: str,
                           include_metadata: bool = False) -> None:
        """
        Write waypoints to CSV file.
        
        Args:
            waypoints: WaypointSequence to export
            file_path: Output CSV file path
            include_metadata: Whether to include waypoint metadata
        """
        # Prepare column headers
        headers = [
            'waypoint_id',
            'latitude', 
            'longitude',
            'heading',
            'speed',
            'waypoint_type'
        ]
        
        if include_metadata:
            # Add metadata columns if any waypoints have metadata
            all_metadata_keys = set()
            for waypoint in waypoints:
                all_metadata_keys.update(waypoint.metadata.keys())
            headers.extend(sorted(all_metadata_keys))
        
        # Write CSV file
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            
            for waypoint in waypoints:
                row = [
                    waypoint.waypoint_id,
                    waypoint.gps_coordinate.latitude,
                    waypoint.gps_coordinate.longitude,
                    waypoint.heading,
                    waypoint.speed,
                    waypoint.waypoint_type.value
                ]
                
                # Add metadata values if requested
                if include_metadata:
                    for key in sorted(all_metadata_keys):
                        row.append(waypoint.metadata.get(key, ''))
                
                writer.writerow(row)
    
    @staticmethod
    def read_waypoints_csv(file_path: str) -> WaypointSequence:
        """
        Read waypoints from CSV file.
        
        Args:
            file_path: Path to waypoints CSV file
            
        Returns:
            WaypointSequence loaded from file
        """
        waypoints = []
        
        try:
            df = pd.read_csv(file_path)
            
            for _, row in df.iterrows():
                # Create GPS coordinate
                gps_coord = GPSCoordinate(
                    latitude=float(row['latitude']),
                    longitude=float(row['longitude'])
                )
                
                # Parse waypoint type
                waypoint_type = WaypointType.COVERAGE
                if 'waypoint_type' in row:
                    try:
                        waypoint_type = WaypointType(row['waypoint_type'])
                    except ValueError:
                        waypoint_type = WaypointType.COVERAGE
                
                # Create metadata dict from remaining columns
                metadata = {}
                excluded_cols = {
                    'waypoint_id', 'latitude', 'longitude', 
                    'heading', 'speed', 'waypoint_type'
                }
                for col in df.columns:
                    if col not in excluded_cols and pd.notna(row[col]):
                        metadata[col] = row[col]
                
                # Create waypoint
                waypoint = Waypoint(
                    gps_coordinate=gps_coord,
                    heading=float(row.get('heading', 0.0)),
                    speed=float(row.get('speed', 2.0)),
                    waypoint_type=waypoint_type,
                    waypoint_id=int(row.get('waypoint_id', 0)),
                    metadata=metadata
                )
                
                waypoints.append(waypoint)
            
            return WaypointSequence(waypoints)
            
        except Exception as e:
            raise ValueError(f"Error reading waypoints CSV: {str(e)}")
    
    @staticmethod
    def write_field_summary_csv(field: Field, file_path: str) -> None:
        """
        Write field summary information to CSV file.
        
        Args:
            field: Field to summarize
            file_path: Output CSV file path
        """
        summary_data = {
            'field_id': [field.field_id],
            'area_m2': [field.calculate_area()],
            'perimeter_m': [field.calculate_perimeter()],
            'num_holes': [len(field.holes)],
            'boundary_points': [len(field.main_boundary.gps_coordinates)],
        }
        
        # Add centroid coordinates
        gps_centroid, utm_centroid = field.get_centroid()
        summary_data['centroid_latitude'] = [gps_centroid.latitude]
        summary_data['centroid_longitude'] = [gps_centroid.longitude]
        
        # Add bounding box
        min_bbox, max_bbox = field.get_bounding_box()
        summary_data['bbox_min_easting'] = [min_bbox.easting]
        summary_data['bbox_min_northing'] = [min_bbox.northing]
        summary_data['bbox_max_easting'] = [max_bbox.easting]
        summary_data['bbox_max_northing'] = [max_bbox.northing]
        
        # Add optimal direction
        summary_data['optimal_direction_deg'] = [field.calculate_optimal_direction()]
        
        # Write to CSV
        df = pd.DataFrame(summary_data)
        df.to_csv(file_path, index=False)
    
    @staticmethod
    def write_coverage_report_csv(field: Field,
                                 waypoints: WaypointSequence,
                                 parameters: Dict[str, Any],
                                 file_path: str) -> None:
        """
        Write a comprehensive coverage planning report to CSV.
        
        Args:
            field: Field that was planned
            waypoints: Generated waypoints
            parameters: Planning parameters used
            file_path: Output CSV file path
        """
        report_data = []
        
        # Field information
        field_area = field.calculate_area()
        total_distance = waypoints.total_distance()
        total_time = waypoints.total_time()
        
        report_data.append({
            'metric': 'Field Area (m²)',
            'value': field_area,
            'unit': 'm²'
        })
        
        report_data.append({
            'metric': 'Field Perimeter (m)',
            'value': field.calculate_perimeter(),
            'unit': 'm'
        })
        
        report_data.append({
            'metric': 'Total Path Distance (m)',
            'value': total_distance,
            'unit': 'm'
        })
        
        report_data.append({
            'metric': 'Estimated Time (s)',
            'value': total_time,
            'unit': 's'
        })
        
        report_data.append({
            'metric': 'Estimated Time (min)',
            'value': total_time / 60,
            'unit': 'min'
        })
        
        report_data.append({
            'metric': 'Number of Waypoints',
            'value': len(waypoints),
            'unit': 'count'
        })
        
        if 'swath_width' in parameters:
            swath_width = parameters['swath_width']
            estimated_coverage = min(field_area, total_distance * swath_width)
            coverage_efficiency = (estimated_coverage / field_area) * 100
            
            report_data.append({
                'metric': 'Swath Width (m)',
                'value': swath_width,
                'unit': 'm'
            })
            
            report_data.append({
                'metric': 'Coverage Efficiency (%)',
                'value': coverage_efficiency,
                'unit': '%'
            })
        
        # Add parameters
        for key, value in parameters.items():
            report_data.append({
                'metric': f'Parameter: {key}',
                'value': value,
                'unit': ''
            })
        
        # Write to CSV
        df = pd.DataFrame(report_data)
        df.to_csv(file_path, index=False)
    
    @staticmethod
    def export_field_boundary_csv(field: Field, file_path: str) -> None:
        """
        Export field boundary to CSV format.
        
        Args:
            field: Field to export
            file_path: Output CSV file path
        """
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['latitude', 'longitude'])
            
            for coord in field.main_boundary.gps_coordinates:
                writer.writerow([coord.latitude, coord.longitude])
    
    @staticmethod
    def validate_and_read_csv(file_path: str) -> List[GPSCoordinate]:
        """
        Validate and read CSV file with comprehensive error reporting.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            List of GPS coordinates
            
        Raises:
            ValueError: With detailed error information
        """
        # First validate format
        validation_errors = validate_input_csv_format(file_path)
        if validation_errors:
            raise ValueError(f"CSV validation failed:\n" + "\n".join(validation_errors))
        
        # Read coordinates
        coordinates = CSVHandler.read_field_boundary_csv(file_path, validate=False)
        
        # Additional validation on coordinates
        from ..utils.validation import validate_gps_coordinates, validate_polygon_closure
        
        coord_errors = validate_gps_coordinates(coordinates)
        if coord_errors:
            raise ValueError(f"GPS coordinate validation failed:\n" + "\n".join(coord_errors))
        
        if not validate_polygon_closure(coordinates):
            # Auto-close polygon if not closed
            if (coordinates[0].latitude != coordinates[-1].latitude or
                coordinates[0].longitude != coordinates[-1].longitude):
                coordinates.append(coordinates[0])
        
        return coordinates
