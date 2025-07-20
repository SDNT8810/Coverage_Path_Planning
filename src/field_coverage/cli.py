"""
Command-line interface for the Field Coverage Planner.
"""

import argparse
from pathlib import Path
from typing import Optional

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


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
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
        default="data/example_field.csv",
        help="Input CSV file containing field boundary GPS coordinates (default: data/example_field.csv)"
    )
    
    parser.add_argument(
        "output_file", 
        type=Path,
        nargs='?',
        default="output/coverage_result.csv",
        help="Output CSV file for generated waypoints (default: output/coverage_result.csv)"
    )
    
    parser.add_argument(
        "--swath-width", "-w",
        type=float,
        default=3.0,
        help="Swath width in meters (default: 3.0)"
    )
    
    parser.add_argument(
        "--overlap", "-o",
        type=float,
        default=0.1,
        help="Overlap percentage as decimal (0.1 = 10%%, default: 0.1)"
    )
    
    parser.add_argument(
        "--turn-radius", "-r",
        type=float,
        default=2.0,
        help="Minimum turning radius in meters (default: 2.0)"
    )
    
    parser.add_argument(
        "--speed", "-s",
        type=float,
        default=2.0,
        help="Default waypoint speed in m/s (default: 2.0)"
    )
    
    parser.add_argument(
        "--direction", "-d",
        type=float,
        help="Coverage direction in degrees (0=North, 90=East). If not specified, optimal direction is calculated."
    )
    
    parser.add_argument(
        "--optimization-step",
        type=float,
        default=15.0,
        help="Step size in degrees for direction optimization (default: 15.0). Smaller values = more precise but slower."
    )
    
    parser.add_argument(
        "--field-id",
        type=str,
        help="Field identifier (default: input filename)"
    )
    
    parser.add_argument(
        "--algorithm", "-a",
        choices=['boustrophedon'],
        default='boustrophedon',
        help="Coverage algorithm to use (default: boustrophedon)"
    )
    
    parser.add_argument('--report', action='store_true', default=False,
                       help='Generate detailed coverage report')
    parser.add_argument('--plot', action='store_true', default=True,
                       help='Generate visualization plot (default: True)')
    parser.add_argument('--plot-output', type=str, default="output/field_coverage_plot.png",
                       help='Output path for plot image (default: output/field_coverage_plot.png)')
    parser.add_argument('--show-plot', action='store_true', default=False,
                       help='Display plot window')
    parser.add_argument('--no-show-plot', dest='show_plot', action='store_false',
                       help='Don\'t display plot window (default)')
    
    parser.add_argument(
        "--validate",
        action='store_true',
        default=True,
        help="Validate waypoints after generation (default: True)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action='store_true',
        default=True,
        help="Enable verbose output (default: True)"
    )
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Initialize planner
        planner = FieldCoveragePlanner(
            swath_width=args.swath_width,
            overlap=args.overlap,
            turn_radius=args.turn_radius,
            speed=args.speed,
            algorithm=args.algorithm
        )
        
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
