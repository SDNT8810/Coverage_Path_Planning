#!/usr/bin/env python3
"""
Visualization Demonstration for Field Coverage Planner

This script demonstrates the new visualization capabilities added to the
Field Coverage Planner project.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and display results."""
    print(f"\n🔧 {description}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
            
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def check_file_exists(filepath, description):
    """Check if a file exists and display info."""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"✅ {description}: {filepath} ({size} bytes)")
        return True
    else:
        print(f"❌ {description}: {filepath} (not found)")
        return False

def main():
    """Run visualization demonstrations."""
    print("🎨 Field Coverage Planner - Visualization Demonstration")
    print("=" * 70)
    
    # Change to project directory
    project_dir = Path(__file__).parent.parent
    os.chdir(project_dir)
    
    print(f"📁 Working directory: {os.getcwd()}")
    
    # Test 1: Simple field with visualization
    print("\\n" + "=" * 50)
    print("TEST 1: Simple Rectangle Field with Visualization")
    print("=" * 50)
    
    cmd1 = [
        "field-coverage",
        "data/simple_rectangle.csv",
        "output/viz_demo_simple.csv",
        "--plot",
        "--plot-output", "output/viz_demo_simple_plot.png",
        "--swath-width", "2.0",
        "--overlap", "0.15",
        "--no-show-plot",
        "--verbose"
    ]
    
    success1 = run_command(cmd1, "Generate simple field coverage with visualization")
    
    if success1:
        check_file_exists("output/viz_demo_simple.csv", "Waypoints CSV")
        check_file_exists("output/viz_demo_simple_plot.png", "Visualization Plot")
    
    # Test 2: Complex field with report and visualization
    print("\\n" + "=" * 50)
    print("TEST 2: Complex Field with Report and Visualization")
    print("=" * 50)
    
    cmd2 = [
        "field-coverage",
        "data/example_field.csv",
        "output/viz_demo_complex.csv",
        "--plot",
        "--plot-output", "output/viz_demo_complex_plot.png",
        "--report",
        "--swath-width", "3.5",
        "--overlap", "0.08",
        "--direction", "30",
        "--no-show-plot",
        "--verbose"
    ]
    
    success2 = run_command(cmd2, "Generate complex field coverage with report and visualization")
    
    if success2:
        check_file_exists("output/viz_demo_complex.csv", "Waypoints CSV")
        check_file_exists("output/viz_demo_complex.report.csv", "Coverage Report")
        check_file_exists("output/viz_demo_complex_plot.png", "Visualization Plot")
    
    # Test 3: Test different parameters
    print("\\n" + "=" * 50)
    print("TEST 3: Parameter Comparison")
    print("=" * 50)
    
    # Wide swath
    cmd3a = [
        "field-coverage",
        "data/simple_rectangle.csv",
        "output/viz_demo_wide_swath.csv",
        "--plot",
        "--plot-output", "output/viz_demo_wide_swath_plot.png",
        "--swath-width", "5.0",
        "--overlap", "0.05",
        "--no-show-plot"
    ]
    
    success3a = run_command(cmd3a, "Wide swath (5m) visualization")
    
    # Narrow swath
    cmd3b = [
        "field-coverage",
        "data/simple_rectangle.csv",
        "output/viz_demo_narrow_swath.csv",
        "--plot",
        "--plot-output", "output/viz_demo_narrow_swath_plot.png",
        "--swath-width", "1.5",
        "--overlap", "0.20",
        "--no-show-plot"
    ]
    
    success3b = run_command(cmd3b, "Narrow swath (1.5m) visualization")
    
    # Summary
    print("\\n" + "=" * 70)
    print("📊 DEMONSTRATION RESULTS")
    print("=" * 70)
    
    tests = [
        ("Simple field visualization", success1),
        ("Complex field with report", success2),
        ("Wide swath comparison", success3a),
        ("Narrow swath comparison", success3b)
    ]
    
    for test_name, success in tests:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    # Generated files summary
    print("\\n📁 Generated Visualization Files:")
    viz_files = [
        "output/viz_demo_simple_plot.png",
        "output/viz_demo_complex_plot.png", 
        "output/viz_demo_wide_swath_plot.png",
        "output/viz_demo_narrow_swath_plot.png"
    ]
    
    for filepath in viz_files:
        check_file_exists(filepath, os.path.basename(filepath))
    
    # Usage examples
    print("\\n" + "=" * 70)
    print("🚀 VISUALIZATION USAGE EXAMPLES")
    print("=" * 70)
    
    print("""
📋 Basic visualization:
   field-coverage input.csv output.csv --plot
   
📋 Save plot to specific file:
   field-coverage input.csv output.csv --plot --plot-output my_plot.png
   
📋 Generate plot without showing window:
   field-coverage input.csv output.csv --plot --no-show-plot
   
📋 Complete analysis with visualization:
   field-coverage input.csv output.csv --plot --report --verbose
   
📋 Custom parameters with visualization:
   field-coverage input.csv output.csv --plot --swath-width 3.0 --overlap 0.1
   """)
    
    # Capabilities overview
    print("\\n" + "=" * 70)
    print("🎯 VISUALIZATION CAPABILITIES")
    print("=" * 70)
    
    print("""
✅ Field boundary plotting with GPS coordinates
✅ Coverage path visualization with waypoints
✅ Start and end point highlighting
✅ Field statistics display (area, distance, time)
✅ Configurable plot styling and colors
✅ High-resolution image export (PNG format)
✅ Optional plot window display control
✅ Integration with coverage reports
✅ Support for different field shapes and sizes
✅ Parameter comparison visualization
    """)
    
    print("\\n🎉 Visualization demonstration completed!")
    print("Check the output/ directory for generated plot files.")

if __name__ == "__main__":
    main()
