@echo off
echo QuantForge Backtest Manager
echo ========================
echo.
echo Starting application using Python Launcher...
echo.
py main.py
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Application failed to start
    echo ========================================
    echo.
    echo Try running: check_installation.bat
    echo Or see: TROUBLESHOOTING.md
    echo.
)
pause

