#!/usr/bin/env python3
"""
Platform compatibility checker for Field Coverage Planner.
Verifies that all dependencies and features work correctly on the current platform.
"""

import sys
import platform
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version < (3, 8):
        print("   ❌ Python 3.8+ required")
        return False
    else:
        print("   ✅ Python version compatible")
        return True

def check_platform():
    """Check platform information."""
    print(f"\n🖥️  Platform Information:")
    print(f"   System: {platform.system()}")
    print(f"   Release: {platform.release()}")
    print(f"   Machine: {platform.machine()}")
    print(f"   Platform: {platform.platform()}")
    
    system = platform.system()
    if system in ['Windows', 'Darwin', 'Linux']:
        print(f"   ✅ {system} is supported")
        return True
    else:
        print(f"   ⚠️  {system} may not be fully tested")
        return True

def check_dependencies():
    """Check if all required dependencies are available."""
    print(f"\n📦 Checking Dependencies:")
    
    required_packages = [
        'numpy',
        'pandas', 
        'matplotlib',
        'shapely',
        'pyproj',
        'geopandas',
        'yaml'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'yaml':
                import yaml
            else:
                __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n   Missing packages: {', '.join(missing)}")
        print(f"   Install with: pip install {' '.join(missing)}")
        return False
    else:
        print("   ✅ All dependencies available")
        return True

def check_project_structure():
    """Check if project structure is correct."""
    print(f"\n📁 Checking Project Structure:")
    
    required_files = [
        'src/field_coverage/__init__.py',
        'src/field_coverage/cli.py',
        'src/field_coverage/main.py',
        'config/defaults.yaml',
        'data/example_field.csv',
        'requirements.txt',
        'run.py'
    ]
    
    missing = []
    # Get project root (parent directory since we're in tests/)
    project_root = Path(__file__).parent.parent
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            missing.append(file_path)
    
    if missing:
        print(f"\n   Missing files: {len(missing)}")
        return False
    else:
        print("   ✅ Project structure complete")
        return True

def test_basic_functionality():
    """Test basic functionality."""
    print(f"\n🧪 Testing Basic Functionality:")
    
    try:
        # Test imports
        print("   Testing imports...")
        # Add the project src directory to path (parent/src since we're in tests/)
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        from field_coverage import FieldCoveragePlanner
        print("   ✅ Core imports working")
        
        # Test configuration loading
        print("   Testing configuration...")
        from field_coverage.cli import load_config
        config = load_config()
        if config:
            print("   ✅ Configuration loading working")
        else:
            print("   ⚠️  Configuration file not found (but not critical)")
        
        # Test path handling
        print("   Testing path handling...")
        from field_coverage.cli import find_project_root
        root = find_project_root()
        print(f"   ✅ Project root: {root}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_command_line():
    """Test command line interface."""
    print(f"\n💻 Testing Command Line Interface:")
    
    try:
        # Test run.py (need to run from project root)
        project_root = Path(__file__).parent.parent
        result = subprocess.run([sys.executable, 'run.py', '--help'], 
                              capture_output=True, text=True, timeout=30,
                              cwd=project_root)
        if result.returncode == 0:
            print("   ✅ run.py --help working")
        else:
            print("   ❌ run.py --help failed")
            return False
            
        # Test if field-coverage command exists (if installed)
        try:
            result = subprocess.run(['field-coverage', '--help'], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("   ✅ field-coverage command available")
            else:
                print("   ⚠️  field-coverage command not installed (use pip install -e .)")
        except FileNotFoundError:
            print("   ⚠️  field-coverage command not found (not installed)")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error testing CLI: {e}")
        return False

def main():
    """Run all compatibility checks."""
    print("🔍 Field Coverage Planner - Platform Compatibility Check")
    print("=" * 60)
    
    checks = [
        check_python_version(),
        check_platform(), 
        check_dependencies(),
        check_project_structure(),
        test_basic_functionality(),
        test_command_line()
    ]
    
    print("\n" + "=" * 60)
    print("📊 COMPATIBILITY SUMMARY:")
    print("=" * 60)
    
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print("🎉 ALL CHECKS PASSED - Platform fully compatible!")
        print("\n✅ Your system is ready to run Field Coverage Planner")
        print("\n🚀 Quick start:")
        if platform.system() == 'Windows':
            print("   python run.py --help")
            print("   run.bat --help")
        else:
            print("   python3 run.py --help")
        return 0
    else:
        print(f"⚠️  {passed}/{total} checks passed")
        print("\n❌ Some issues found. Please resolve them before using the planner.")
        
        if not checks[2]:  # Dependencies check failed
            print("\n🔧 To install missing dependencies:")
            if platform.system() == 'Windows':
                print("   pip install -r requirements.txt")
            else:
                print("   pip3 install -r requirements.txt")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
