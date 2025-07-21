@echo off
REM Windows update script for Field Coverage Planner
echo 🔄 Updating Field Coverage Planner on Windows...

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo 📦 Uninstalling old version...
pip uninstall field-coverage-planner -y >nul 2>&1
if not %ERRORLEVEL% == 0 (
    python -m pip uninstall field-coverage-planner -y >nul 2>&1
)

echo 📦 Installing updated version...
pip install -e . >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo ✅ Update successful!
    echo.
    echo 📋 You can now use either:
    echo    • field-coverage (system command^)
    echo    • python run.py (direct runner^)
    echo    • run.bat (Windows batch script^)
    echo.
    echo 🧪 Testing installation...
    field-coverage --help >nul 2>&1
    if %ERRORLEVEL% == 0 (
        echo ✅ field-coverage command working correctly
    ) else (
        echo ❌ field-coverage command failed, but run.py should still work
    )
) else (
    echo ❌ Update failed - trying with python -m pip...
    python -m pip install -e .
    if %ERRORLEVEL% == 0 (
        echo ✅ Update successful with python -m pip!
    ) else (
        echo ❌ Update failed completely
        exit /b 1
    )
)

echo.
echo 🎯 Configuration priority:
echo    1. Command line arguments (highest^)
echo    2. config\defaults.yaml
echo    3. Hardcoded defaults (lowest^)

pause
