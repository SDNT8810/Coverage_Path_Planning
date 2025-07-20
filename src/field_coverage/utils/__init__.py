"""
Utility functions and classes for field coverage path planning.
"""

from .geometry import (
    calculate_polygon_area,
    calculate_polygon_centroid,
    point_to_line_distance,
    line_polygon_intersection,
    create_parallel_lines,
    clip_line_to_polygon,
    calculate_line_angle,
    rotate_point,
    simplify_polygon,
    calculate_turning_radius,
    generate_turn_waypoints
)

from .validation import (
    validate_gps_coordinates,
    validate_polygon_closure,
    validate_polygon_self_intersection,
    validate_field_parameters,
    validate_waypoint_sequence,
    validate_coverage_completeness,
    validate_input_csv_format
)

__all__ = [
    # Geometry utilities
    "calculate_polygon_area",
    "calculate_polygon_centroid", 
    "point_to_line_distance",
    "line_polygon_intersection",
    "create_parallel_lines",
    "clip_line_to_polygon",
    "calculate_line_angle",
    "rotate_point",
    "simplify_polygon",
    "calculate_turning_radius",
    "generate_turn_waypoints",
    
    # Validation utilities
    "validate_gps_coordinates",
    "validate_polygon_closure",
    "validate_polygon_self_intersection", 
    "validate_field_parameters",
    "validate_waypoint_sequence",
    "validate_coverage_completeness",
    "validate_input_csv_format",
]
