# Field Coverage Path Planner

A Python library for generating optimal coverage paths for agricultural fields using GPS coordinates with intelligent direction optimization and real-time optimization feedback.

## ✨ Features

- **🎯 Multiple Input Sources**: Support for CSV files and ROS topics
- **🗺️ Polygon Field Processing**: Handle any valid polygon shape including complex geometries  
- **🧠 Intelligent Path Optimization**: Automatically finds optimal coverage direction to minimize travel distance
- **⚙️ Configurable Optimization**: Adjustable step size for precision vs speed trade-offs (1° to 30° steps)
- **📍 GPS Coordinate Handling**: Accurate coordinate transformations with UTM projection
- **🔄 Boustrophedon Coverage**: Back-and-forth pattern with proper field boundary intersection using Shapely
- **📊 Visualization**: Plot field boundaries and coverage paths with matplotlib
- **🎛️ Configurable Parameters**: Swath width, overlap, turn radius, optimization precision
- **⭐ Real-time Optimization Display**: See optimization progress with visual feedback markers

## 🚀 Performance Optimization Results

The optimization algorithm can significantly reduce travel distance:

| Optimization Level | Step Size | Directions Tested | Typical Improvement |
|-------------------|-----------|-------------------|-------------------|
| **Quick** | 30° | 6 | 0.5-1% path reduction |
| **Standard** | 15° | 12 | 1-2% path reduction |
| **Fine** | 5° | 36 | 1.5-2.5% path reduction |
| **Precision** | 1° | 180 | 2-3% path reduction |

*Example: 7-edge field optimization found 95.7m (1.15%) improvement from worst to best direction*

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd field-coverage-planner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Command Line Interface
```bash
# Basic coverage with automatic optimization
field-coverage field_boundary.csv waypoints.csv

# Specify coverage direction manually
field-coverage field_boundary.csv waypoints.csv --direction 45

# Fine optimization (slower but more precise)
field-coverage field_boundary.csv waypoints.csv --optimization-step 1

# Quick optimization (faster)
field-coverage field_boundary.csv waypoints.csv --optimization-step 30

# With visualization
field-coverage field_boundary.csv waypoints.csv --plot --plot-output field_plot.png

# All parameters
field-coverage field_boundary.csv waypoints.csv \
  --swath-width 4.0 \
  --overlap 0.15 \
  --direction 90 \
  --plot \
  --verbose
```

### Python API
```python
from field_coverage import FieldCoveragePlanner

# Initialize planner
planner = FieldCoveragePlanner(swath_width=2.0, overlap=0.1)

# Load field from CSV
field = planner.load_field_from_csv('field_boundary.csv')

# Generate coverage path with automatic optimization
waypoints = planner.generate_coverage_path(field, optimization_step=5.0)

# Generate coverage path with specific direction
waypoints = planner.generate_coverage_path(field, direction=45.0)

# Export waypoints
planner.export_waypoints(waypoints, 'waypoints.csv')
```

### From ROS Topic
```python
from field_coverage import ROSFieldPlanner

# Initialize ROS planner
ros_planner = ROSFieldPlanner('/field_boundary', swath_width=2.0)

# Start listening for field boundaries
ros_planner.start_coverage_service()
```

## Input Format

### CSV File Format
```csv
latitude,longitude
40.7128,-74.0060
40.7580,-73.9855
40.7489,-73.9441
40.7128,-74.0060
```

## Output Format

### Waypoints CSV
```csv
waypoint_id,latitude,longitude,heading,speed,waypoint_type
1,40.7128,-74.0060,90.0,2.0,coverage
2,40.7130,-74.0058,90.0,2.0,coverage
3,40.7132,-74.0056,270.0,1.0,turn
4,40.7134,-74.0054,270.0,2.0,coverage
...
```

### Coverage Report
```csv
metric,value,unit
total_waypoints,834,count
total_distance,8312.5,meters
coverage_area,29002.6,square_meters
estimated_time,69.3,minutes
optimal_direction,60.0,degrees
swath_width,4.0,meters
```

## Algorithm Features

### Direction Optimization
- **Automatic**: Tests multiple directions to find minimum path length
- **Configurable Precision**: Adjustable step size (1° to 30°)
- **Performance**: Up to 1.15% path length reduction vs non-optimized
- **User Control**: Can specify exact direction or let algorithm optimize

### Field Boundary Handling
- **Shapely Integration**: Proper geometric intersection with complex polygons
- **No Rectangular Assumption**: Respects actual field boundaries
- **Multi-segment Support**: Handles fields with holes or irregular shapes

## Project Structure

```
field-coverage-planner/
├── src/
│   └── field_coverage/
│       ├── __init__.py
│       ├── main.py                    # Main FieldCoveragePlanner class
│       ├── cli.py                     # Command line interface
│       ├── core/
│       │   ├── __init__.py
│       │   ├── field.py               # Field and boundary classes
│       │   ├── waypoint.py            # Waypoint and sequence classes
│       │   └── coordinates.py         # GPS/UTM coordinate handling
│       ├── algorithms/
│       │   ├── __init__.py
│       │   └── boustrophedon.py       # Boustrophedon coverage with optimization
│       ├── io/
│       │   ├── __init__.py
│       │   ├── csv_handler.py         # CSV input/output
│       │   └── ros_handler.py         # ROS topic support
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── geometry.py            # Geometric utilities
│       │   └── validation.py          # Waypoint validation
│       └── visualization/
│           ├── __init__.py
│           └── field_plotter.py       # Matplotlib visualization
├── tests/                             # Unit and integration tests
├── examples/                          # Example usage scripts
├── data/                              # Sample field data
│   ├── simple_rectangle.csv
│   └── example_field.csv
├── docs/                              # Documentation
├── requirements.txt                   # Python dependencies
├── setup.py                          # Package setup
├── README.md                          # This file
├── TODO.md                           # Project status and todos
└── PROJECT_STATUS.md                 # Implementation summary
```

## License

MIT License
