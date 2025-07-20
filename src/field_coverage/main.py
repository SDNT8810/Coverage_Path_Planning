"""
Main field coverage planner class that orchestrates all components.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path

from .core.field import Field
from .core.waypoint import WaypointSequence
from .algorithms.boustrophedon import BoustrophedonPlanner
from .io.csv_handler import CSVHandler
from .io.ros_handler import ROSHandler
from .utils.validation import validate_field_parameters, validate_waypoint_sequence


class FieldCoveragePlanner:
    """
    Main class for field coverage path planning.
    
    This class provides a high-level interface for:
    - Loading field boundaries from CSV files or ROS topics
    - Generating optimal coverage paths
    - Exporting waypoints to CSV files
    - Validating inputs and outputs
    """
    
    def __init__(self,
                 swath_width: float = 2.0,
                 overlap: float = 0.1,
                 turn_radius: float = 2.0,
                 speed: float = 2.0,
                 algorithm: str = 'boustrophedon'):
        """
        Initialize the field coverage planner.
        
        Args:
            swath_width: Width of coverage swath in meters
            overlap: Overlap between swaths (0.0 to 1.0)
            turn_radius: Minimum turning radius in meters
            speed: Default waypoint speed in m/s
            algorithm: Coverage algorithm ('boustrophedon', 'spiral', etc.)
        """
        self.swath_width = swath_width
        self.overlap = overlap
        self.turn_radius = turn_radius
        self.speed = speed
        self.algorithm = algorithm
        
        # Initialize components
        self.csv_handler = CSVHandler()
        self.ros_handler = None  # Initialized on demand
        
        # Initialize algorithm
        if algorithm == 'boustrophedon':
            self.planner = BoustrophedonPlanner(
                swath_width=swath_width,
                overlap=overlap,
                turn_radius=turn_radius,
                speed=speed
            )
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    def load_field_from_csv(self, 
                           csv_file_path: str,
                           hole_files: Optional[List[str]] = None,
                           field_id: Optional[str] = None,
                           validate: bool = True) -> Field:
        """
        Load field boundary from CSV file.
        
        Args:
            csv_file_path: Path to CSV file with field boundary coordinates
            hole_files: Optional list of CSV files with hole boundaries
            field_id: Optional field identifier
            validate: Whether to validate the field parameters
            
        Returns:
            Field object loaded from CSV
            
        Raises:
            ValueError: If validation fails or file format is invalid
        """
        try:
            # Load field from CSV
            if hole_files:
                field = self.csv_handler.read_field_with_holes_csv(
                    main_boundary_file=csv_file_path,
                    hole_files=hole_files,
                    field_id=field_id
                )
            else:
                coordinates = self.csv_handler.validate_and_read_csv(csv_file_path)
                field = Field.from_gps_coordinates(
                    coordinates=coordinates,
                    field_id=field_id or Path(csv_file_path).stem
                )
            
            # Validate field parameters if requested
            if validate:
                errors = validate_field_parameters(
                    field=field,
                    swath_width=self.swath_width,
                    overlap=self.overlap,
                    min_turn_radius=self.turn_radius
                )
                if errors:
                    raise ValueError(f"Field validation failed: {'; '.join(errors)}")
            
            return field
            
        except Exception as e:
            raise ValueError(f"Failed to load field from CSV: {str(e)}")
    
    def load_field_from_ros(self,
                          topic_name: str = '/field_boundary',
                          timeout: float = 30.0) -> Optional[Field]:
        """
        Load field boundary from ROS topic.
        
        Args:
            topic_name: ROS topic name for field boundary
            timeout: Maximum time to wait for message in seconds
            
        Returns:
            Field object if received, None if timeout
        """
        if self.ros_handler is None:
            self.ros_handler = ROSHandler()
        
        return self.ros_handler.wait_for_field_boundary(topic_name, timeout)
    
    def generate_coverage_path(self,
                             field: Field,
                             direction: Optional[float] = None,
                             optimize_direction: bool = True,
                             optimization_step: float = 15.0,
                             validate_output: bool = True) -> WaypointSequence:
        """
        Generate coverage path for the field.
        
        Args:
            field: Field to generate coverage for
            direction: Coverage direction in degrees. If None, uses optimal.
            optimize_direction: Whether to optimize coverage direction
            optimization_step: Step size in degrees for optimization (default: 15.0)
            validate_output: Whether to validate generated waypoints
            
        Returns:
            WaypointSequence with coverage path
            
        Raises:
            ValueError: If path generation or validation fails
        """
        try:
            # Generate coverage path (planner will optimize direction if None)
            waypoints = self.planner.plan_coverage(
                field=field,
                direction=direction,
                optimization_step=optimization_step
            )
            
            # Validate output if requested
            if validate_output:
                errors = validate_waypoint_sequence(
                    waypoints=waypoints,
                    max_speed=self.speed * 2,  # Allow some tolerance
                    max_heading_change=90.0
                )
                if errors:
                    print(f"Warning: Waypoint validation issues: {'; '.join(errors)}")
            
            return waypoints
            
        except Exception as e:
            raise ValueError(f"Failed to generate coverage path: {str(e)}")
    
    def export_waypoints(self,
                        waypoints: WaypointSequence,
                        output_file: str,
                        include_metadata: bool = False) -> None:
        """
        Export waypoints to CSV file.
        
        Args:
            waypoints: WaypointSequence to export
            output_file: Output CSV file path
            include_metadata: Whether to include waypoint metadata
        """
        try:
            self.csv_handler.write_waypoints_csv(
                waypoints=waypoints,
                file_path=output_file,
                include_metadata=include_metadata
            )
        except Exception as e:
            raise ValueError(f"Failed to export waypoints: {str(e)}")
    
    def publish_waypoints_ros(self,
                            waypoints: WaypointSequence,
                            topic_name: str = '/waypoints') -> None:
        """
        Publish waypoints to ROS topic.
        
        Args:
            waypoints: WaypointSequence to publish
            topic_name: ROS topic name for waypoints
        """
        if self.ros_handler is None:
            self.ros_handler = ROSHandler()
        
        self.ros_handler.publish_waypoints(waypoints, topic_name)
    
    def generate_field_report(self,
                            field: Field,
                            waypoints: WaypointSequence,
                            output_file: str) -> Dict[str, Any]:
        """
        Generate comprehensive field coverage report.
        
        Args:
            field: Field that was planned
            waypoints: Generated waypoints
            output_file: Output file path for detailed report
            
        Returns:
            Dictionary with report summary
        """
        try:
            # Calculate basic metrics
            field_area = field.calculate_area()
            total_distance = waypoints.total_distance()
            total_time = waypoints.total_time()
            
            # Calculate coverage metrics
            if hasattr(self.planner, 'calculate_coverage_area'):
                coverage_area = self.planner.calculate_coverage_area(waypoints)
                coverage_efficiency = (coverage_area / field_area) * 100
            else:
                # Simplified coverage calculation
                estimated_coverage = min(field_area, total_distance * self.swath_width)
                coverage_efficiency = (estimated_coverage / field_area) * 100
            
            # Prepare report data
            report_summary = {
                'field_id': field.field_id,
                'field_area_m2': field_area,
                'field_perimeter_m': field.calculate_perimeter(),
                'total_path_distance_m': total_distance,
                'estimated_time_min': total_time / 60,
                'number_of_waypoints': len(waypoints),
                'coverage_efficiency_percent': coverage_efficiency,
                'swath_width_m': self.swath_width,
                'overlap_percent': self.overlap * 100,
                'algorithm': self.algorithm
            }
            
            # Write detailed report to CSV
            parameters = {
                'swath_width': self.swath_width,
                'overlap': self.overlap,
                'turn_radius': self.turn_radius,
                'speed': self.speed,
                'algorithm': self.algorithm
            }
            
            self.csv_handler.write_coverage_report_csv(
                field=field,
                waypoints=waypoints,
                parameters=parameters,
                file_path=output_file
            )
            
            return report_summary
            
        except Exception as e:
            raise ValueError(f"Failed to generate field report: {str(e)}")
    
    def validate_configuration(self) -> List[str]:
        """
        Validate the current planner configuration.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate swath width
        if self.swath_width <= 0:
            errors.append(f"Invalid swath width: {self.swath_width}")
        
        # Validate overlap
        if not (0.0 <= self.overlap < 1.0):
            errors.append(f"Invalid overlap: {self.overlap}")
        
        # Validate turn radius
        if self.turn_radius <= 0:
            errors.append(f"Invalid turn radius: {self.turn_radius}")
        
        # Validate speed
        if self.speed <= 0:
            errors.append(f"Invalid speed: {self.speed}")
        
        return errors
    
    def set_parameters(self,
                      swath_width: Optional[float] = None,
                      overlap: Optional[float] = None,
                      turn_radius: Optional[float] = None,
                      speed: Optional[float] = None) -> None:
        """
        Update planner parameters.
        
        Args:
            swath_width: New swath width in meters
            overlap: New overlap fraction
            turn_radius: New turn radius in meters
            speed: New default speed in m/s
        """
        if swath_width is not None:
            self.swath_width = swath_width
            self.planner.swath_width = swath_width
        
        if overlap is not None:
            self.overlap = overlap
            self.planner.overlap = overlap
        
        if turn_radius is not None:
            self.turn_radius = turn_radius
            self.planner.turn_radius = turn_radius
        
        if speed is not None:
            self.speed = speed
            self.planner.speed = speed
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get current planner parameters.
        
        Returns:
            Dictionary with current parameters
        """
        return {
            'swath_width': self.swath_width,
            'overlap': self.overlap,
            'turn_radius': self.turn_radius,
            'speed': self.speed,
            'algorithm': self.algorithm
        }
    
    def process_field_file(self,
                         input_csv: str,
                         output_csv: str,
                         direction: Optional[float] = None,
                         field_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete workflow: load field, generate path, export waypoints.
        
        Args:
            input_csv: Input CSV file with field boundary
            output_csv: Output CSV file for waypoints
            direction: Coverage direction (None for optimal)
            field_id: Optional field identifier
            
        Returns:
            Dictionary with processing summary
        """
        try:
            # Load field
            field = self.load_field_from_csv(input_csv, field_id=field_id)
            
            # Generate coverage path
            waypoints = self.generate_coverage_path(field, direction=direction)
            
            # Export waypoints
            self.export_waypoints(waypoints, output_csv)
            
            # Generate summary
            summary = {
                'input_file': input_csv,
                'output_file': output_csv,
                'field_area_m2': field.calculate_area(),
                'waypoints_generated': len(waypoints),
                'total_distance_m': waypoints.total_distance(),
                'estimated_time_min': waypoints.total_time() / 60,
                'success': True
            }
            
            return summary
            
        except Exception as e:
            return {
                'input_file': input_csv,
                'output_file': output_csv,
                'error': str(e),
                'success': False
            }
