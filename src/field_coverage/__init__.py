"""
Field Coverage Planning Package

A comprehensive Python package for autonomous field coverage path planning.
"""

VISUALIZATION_AVAILABLE = False

try:
    from .core.coordinates import GPSCoordinate, UTMCoordinate, CoordinateTransformer
    from .core.field import Field, FieldBoundary
    from .core.waypoint import Waypoint, WaypointSequence
    from .algorithms.boustrophedon import BoustrophedonPlanner
    from .main import FieldCoveragePlanner
    from .io.csv_handler import CSVHandler
    from .utils import validation
    
    # Try to import visualization (optional dependency)
    try:
        from .visualization.field_plotter import FieldPlotter, create_coverage_visualization
        VISUALIZATION_AVAILABLE = True
    except ImportError:
        VISUALIZATION_AVAILABLE = False
        print("Warning: Visualization features not available. Install matplotlib for plotting capabilities.")
    
except ImportError as e:
    print(f"Warning: Some dependencies are missing: {e}")

__version__ = "1.0.0"
__author__ = "davoud nikkhouy"
__email__ = "davoudnikkhouy@gmail.com"

__all__ = [
    'GPSCoordinate', 'UTMCoordinate', 'CoordinateTransformer',
    'Field', 'FieldBoundary', 'Waypoint', 'WaypointSequence',
    'BoustrophedonPlanner', 'FieldCoveragePlanner',
    'CSVHandler', 'validation', 'VISUALIZATION_AVAILABLE'
]

if VISUALIZATION_AVAILABLE:
    __all__.extend(['FieldPlotter', 'create_coverage_visualization'])

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

try:
    from .core.coordinates import GPSCoordinate, UTMCoordinate, CoordinateTransformer
    from .core.waypoint import Waypoint, WaypointSequence
    from .core.field import Field
    from .algorithms.boustrophedon import BoustrophedonPlanner
    from .io.csv_handler import CSVHandler
    from .main import FieldCoveragePlanner
except ImportError as e:
    # Handle missing dependencies gracefully
    import warnings
    warnings.warn(f"Some dependencies are missing: {e}. Install requirements.txt for full functionality.")
    
    # Try to import minimal functionality
    try:
        from .core.coordinates import GPSCoordinate
    except ImportError:
        GPSCoordinate = None
    
    FieldCoveragePlanner = None
    Field = None

__all__ = [
    "Field",
    "Waypoint", 
    "WaypointSequence",
    "GPSCoordinate",
    "UTMCoordinate", 
    "CoordinateTransformer",
    "BoustrophedonPlanner",
    "CSVHandler",
    "FieldCoveragePlanner",
]
