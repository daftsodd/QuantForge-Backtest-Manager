@echo off
echo QuantForge Backtest Manager - Installation (Python Launcher)
echo =============================================================
echo.
echo This script uses the Python Launcher (py command)
echo.
echo Checking Python...
py --version
echo.
echo Installing pip if missing...
py -m ensurepip --default-pip
echo.
echo Installing packages...
echo.
py -m pip install --upgrade pip
py -m pip install PyQt6
py -m pip install pandas
py -m pip install openpyxl
py -m pip install Pillow
echo.
echo Testing installation...
py -c "import PyQt6; print('PyQt6 installed successfully')"
py -c "import pandas; print('pandas installed successfully')"
py -c "import openpyxl; print('openpyxl installed successfully')"
py -c "import PIL; print('Pillow installed successfully')"
echo.
echo =============================================================
echo Installation complete!
echo.
echo Run the app using: run_app_with_launcher.bat
echo.
pause

