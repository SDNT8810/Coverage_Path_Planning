#!/bin/bash
# Update script for Field Coverage Planner
# This script reinstalls the package to sync the system command with latest changes

echo "🔄 Updating Field Coverage Planner..."

# Navigate to project directory
cd "$(dirname "$0")"

# Uninstall old version (if exists)
echo "📦 Uninstalling old version..."
pip3 uninstall field-coverage-planner -y > /dev/null 2>&1

# Reinstall in development mode
echo "📦 Installing updated version..."
pip3 install -e . > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Update successful!"
    echo ""
    echo "📋 You can now use either:"
    echo "   • field-coverage (system command)"
    echo "   • python3 run.py (direct runner)"
    echo ""
    echo "🧪 Testing installation..."
    field-coverage --help > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ field-coverage command working correctly"
        echo ""
        echo "🎯 Configuration priority:"
        echo "   1. Command line arguments (highest)"
        echo "   2. config/defaults.yaml"
        echo "   3. Hardcoded defaults (lowest)"
    else
        echo "❌ Installation verification failed"
        exit 1
    fi
else
    echo "❌ Update failed"
    exit 1
fi
