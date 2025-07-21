@echo off
REM Windows batch script to run Field Coverage Planner
REM This script automatically finds Python and runs the coverage planner

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Change to the script directory
cd /d "%SCRIPT_DIR%"

REM Try to run with python command
python run.py %*
if %ERRORLEVEL% EQU 0 goto :end

REM If that fails, try python3
python3 run.py %*
if %ERRORLEVEL% EQU 0 goto :end

REM If that fails, try py launcher
py run.py %*
if %ERRORLEVEL% EQU 0 goto :end

REM If all fail, show error
echo Error: Could not find Python interpreter
echo Please install Python from python.org or Microsoft Store
exit /b 1

:end
