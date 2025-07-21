"""
Command-line interface for the Field Coverage Planner.
"""

import argparse
import yaml
import os
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from .main import FieldCoveragePlanner
    from . import VISUALIZATION_AVAILABLE
    if VISUALIZATION_AVAILABLE:
        from .visualization.field_plotter import create_coverage_visualization
except ImportError:
    # For direct execution
    import sys
    sys.path.append(str(Path(__file__).parent))
    from main import FieldCoveragePlanner


def find_project_root() -> Path:
    """
    Find the project root directory by looking for key files.
    
    Returns:
        Path to the project root directory
    """
    # Start from current working directory
    current = Path.cwd()
    
    # Look for characteristic files that indicate project root
    markers = ['setup.py', 'requirements.txt', 'README.md', 'config/defaults.yaml']
    
    # Check current directory and parents
    for path in [current] + list(current.parents):
        if any((path / marker).exists() for marker in markers):
            return path
    
    # If not found, try relative to script location
    script_dir = Path(__file__).parent
    for path in [script_dir.parent.parent.parent, script_dir.parent.parent, script_dir.parent]:
        if any((path / marker).exists() for marker in markers):
            return path
    
    # Default to current working directory
    return current


def load_config(config_path: str = "config/defaults.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the YAML configuration file relative to project root
        
    Returns:
        Dictionary with configuration values
    """
    try:
        project_root = find_project_root()
        config_file = project_root / config_path
        
        if not config_file.exists():
            return {}
            
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            return config if config else {}
            
    except Exception as e:
        return {}


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser with config-aware defaults."""
    
    # Find project root for resolving relative paths
    project_root = find_project_root()
    
    # Load configuration from YAML (priority 2)
    config = load_config()
    
    # Define hardcoded defaults (priority 3) - relative to project root
    hardcoded_defaults = {
        'input_file': str(project_root / "data/example_field.csv"),
        'output_file': str(project_root / "output/coverage_result.csv"),
        'swath_width': 3.0,
        'overlap': 0.1,
        'turn_radius': 2.0,
        'speed': 2.0,
        'direction': None,
        'optimization_step': 15.0,
        'field_id': None,
        'algorithm': 'boustrophedon',
        'report': False,
        'plot': True,
        'plot_output': str(project_root / "output/field_coverage_plot.png"),
        'show_plot': False,
        'validate': True,
        'verbose': True
    }
    
    # Convert relative paths in config to absolute paths
    if config:
        if 'input_file' in config and not os.path.isabs(config['input_file']):
            config['input_file'] = str(project_root / config['input_file'])
        if 'output_file' in config and not os.path.isabs(config['output_file']):
            config['output_file'] = str(project_root / config['output_file'])
        if 'plot_output' in config and not os.path.isabs(config['plot_output']):
            config['plot_output'] = str(project_root / config['plot_output'])
    
    # Merge config with hardcoded defaults (config takes priority)
    defaults = {**hardcoded_defaults, **config}
    
    parser = argparse.ArgumentParser(
        description="Field Coverage Path Planner - Generate optimal coverage paths for agricultural fields",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick start with defaults (uses example_field.csv, generates plot)
  field-coverage
  
  # Basic usage with specific files
  field-coverage input.csv output.csv
  
  # With custom parameters
  field-coverage input.csv output.csv --swath-width 3.0 --overlap 0.15
  
  # Fine optimization
  field-coverage --optimization-step 5
  
  # Custom output location
  field-coverage --plot-output my_field_plot.png
        """
    )
    
    parser.add_argument(
        "input_file",
        type=Path,
        nargs='?',
        default=defaults['input_file'],
        help=f"Input CSV file containing field boundary GPS coordinates (default: {defaults['input_file']})"
    )
    
    parser.add_argument(
        "output_file", 
        type=Path,
        nargs='?',
        default=defaults['output_file'],
        help=f"Output CSV file for generated waypoints (default: {defaults['output_file']})"
    )
    
    parser.add_argument(
        "--swath-width", "-w",
        type=float,
        default=defaults['swath_width'],
        help=f"Swath width in meters (default: {defaults['swath_width']})"
    )
    
    parser.add_argument(
        "--overlap", "-o",
        type=float,
        default=defaults['overlap'],
        help=f"Overlap percentage as decimal (0.1 = 10%%, default: {defaults['overlap']})"
    )
    
    parser.add_argument(
        "--turn-radius", "-r",
        type=float,
        default=defaults['turn_radius'],
        help=f"Minimum turning radius in meters (default: {defaults['turn_radius']})"
    )
    
    parser.add_argument(
        "--speed", "-s",
        type=float,
        default=defaults['speed'],
        help=f"Default waypoint speed in m/s (default: {defaults['speed']})"
    )
    
    parser.add_argument(
        "--direction", "-d",
        type=float,
        default=defaults['direction'],
        help="Coverage direction in degrees (0=North, 90=East). If not specified, optimal direction is calculated."
    )
    
    parser.add_argument(
        "--optimization-step",
        type=float,
        default=defaults['optimization_step'],
        help=f"Step size in degrees for direction optimization (default: {defaults['optimization_step']}). Smaller values = more precise but slower."
    )
    
    parser.add_argument(
        "--field-id",
        type=str,
        default=defaults['field_id'],
        help="Field identifier (default: input filename)"
    )
    
    parser.add_argument(
        "--algorithm", "-a",
        choices=['boustrophedon'],
        default=defaults['algorithm'],
        help=f"Coverage algorithm to use (default: {defaults['algorithm']})"
    )
    
    parser.add_argument('--report', action='store_true', default=defaults['report'],
                       help='Generate detailed coverage report')
    parser.add_argument('--plot', action='store_true', default=defaults['plot'],
                       help=f'Generate visualization plot (default: {defaults["plot"]})')
    parser.add_argument('--plot-output', type=str, default=defaults['plot_output'],
                       help=f'Output path for plot image (default: {defaults["plot_output"]})')
    parser.add_argument('--show-plot', action='store_true', default=defaults['show_plot'],
                       help='Display plot window')
    parser.add_argument('--no-show-plot', dest='show_plot', action='store_false',
                       help='Don\'t display plot window (default)')
    
    parser.add_argument(
        "--validate",
        action='store_true',
        default=defaults['validate'],
        help=f"Validate waypoints after generation (default: {defaults['validate']})"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action='store_true',
        default=defaults['verbose'],
        help=f"Enable verbose output (default: {defaults['verbose']})"
    )
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Show configuration info if verbose
        if args.verbose:
            project_root = find_project_root()
            config = load_config()
            config_file = project_root / "config/defaults.yaml"
            
            if config and config_file.exists():
                print(f"📋 Configuration loaded from {config_file}")
            else:
                print("📋 Using hardcoded defaults (no config file found)")
            print(f"📁 Project root: {project_root}")
            print()
        
        # Initialize planner
        planner = FieldCoveragePlanner(
            swath_width=args.swath_width,
            overlap=args.overlap,
            turn_radius=args.turn_radius,
            speed=args.speed,
            algorithm=args.algorithm
        )
        
        # Ensure output directory exists
        output_dir = Path(args.output_file).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if args.verbose:
            print("Initializing Field Coverage Planner...")
            print(f"  Swath width: {args.swath_width}m")
            print(f"  Overlap: {args.overlap*100:.1f}%")
            print(f"  Turn radius: {args.turn_radius}m")
            print(f"  Speed: {args.speed}m/s")
            print(f"  Algorithm: {args.algorithm}")
            print()
        
        # Load field
        field_id = args.field_id or args.input_file.stem
        if args.verbose:
            print(f"Loading field from: {args.input_file}")
        
        field = planner.load_field_from_csv(
            csv_file_path=str(args.input_file), 
            field_id=field_id
        )
        
        if args.verbose:
            print(f"  Field ID: {field.field_id}")
            print(f"  Field area: {field.calculate_area():.1f} m²")
            print(f"  Field perimeter: {field.calculate_perimeter():.1f} m")
            print()
        
        # Generate coverage path
        if args.verbose:
            print("Generating coverage path...")
            if args.direction is not None:
                print(f"  Using specified direction: {args.direction}°")
            else:
                print(f"  Using optimal direction (optimization step: {args.optimization_step}°)")
        
        waypoints = planner.generate_coverage_path(
            field, 
            direction=args.direction,
            optimization_step=args.optimization_step
        )
        
        # Validate waypoints if requested
        if args.validate:
            from .utils.validation import validate_waypoint_sequence
            validation_results = validate_waypoint_sequence(waypoints, max_speed=args.speed*2)
            if validation_results and args.verbose:
                print(f"Warning: Waypoint validation issues: {'; '.join(validation_results)}")
        
        # Calculate statistics
        total_distance = waypoints.total_distance()
        estimated_time = total_distance / args.speed / 60  # minutes
        
        if args.verbose:
            print(f"  Generated {len(waypoints.waypoints)} waypoints")
            print(f"  Total path distance: {total_distance:.1f} m")
            print(f"  Estimated time: {estimated_time:.1f} minutes")
            print()
        
        # Export waypoints
        if args.verbose:
            print(f"Exporting waypoints to: {args.output_file}")
        
        planner.export_waypoints(waypoints, str(args.output_file))
        
        # Generate report if requested
        if args.report:
            report_path = str(args.output_file).replace('.csv', '.report.csv')
            if args.verbose:
                print(f"Generating report: {report_path}")
            
            report_summary = planner.generate_field_report(
                field=field,
                waypoints=waypoints,
                output_file=report_path
            )
            
            # Print summary
            print("\\nCoverage Report Summary:")
            print("-" * 30)
            
            # Add our additional data to the report summary
            report_summary.update({
                'swath_width_m': args.swath_width,
                'overlap_percent': args.overlap * 100,
                'algorithm': args.algorithm
            })
            
            for key, value in report_summary.items():
                if isinstance(value, float):
                    print(f"{key}: {value:.2f}")
                else:
                    print(f"{key}: {value}")
        
        # Generate visualization if requested
        if args.plot:
            if not VISUALIZATION_AVAILABLE:
                print("Warning: Visualization not available. Install matplotlib: pip install matplotlib")
            else:
                if args.verbose:
                    print("\\nGenerating visualization...")
                
                plot_path = args.plot_output
                if plot_path is None and args.output_file:
                    plot_path = str(args.output_file).replace('.csv', '_plot.png')
                
                # Ensure plot output directory exists
                if plot_path:
                    plot_dir = Path(plot_path).parent
                    plot_dir.mkdir(parents=True, exist_ok=True)
                
                try:
                    create_coverage_visualization(
                        field=field,
                        waypoints=waypoints,
                        swath_width=args.swath_width,
                        total_distance=total_distance,
                        estimated_time=estimated_time,
                        output_path=plot_path,
                        show=args.show_plot
                    )
                    if plot_path and args.verbose:
                        print(f"Plot saved to: {plot_path}")
                except Exception as e:
                    print(f"Warning: Could not generate plot: {e}")
        
        print("\\n✓ Coverage planning completed successfully!")
        print(f"  Input: {args.input_file}")
        print(f"  Output: {args.output_file}")
        print(f"  Waypoints: {len(waypoints.waypoints)}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{args.input_file}' not found.")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
