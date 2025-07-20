#!/usr/bin/env python3
"""
Simple runner script for Field Coverage Planner.

This script allows you to run the field coverage planner without installing the package.
It automatically adds the src directory to Python path and runs the CLI.
"""

import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Import and run the CLI
from field_coverage.cli import main

if __name__ == "__main__":
    sys.exit(main())
