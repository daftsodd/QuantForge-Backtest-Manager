@echo off
echo QuantForge Backtest Manager - Installation Check
echo ================================================
echo.
echo Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)
echo.
echo Checking pip...
python -m pip --version
if errorlevel 1 (
    echo ERROR: pip not found!
    pause
    exit /b 1
)
echo.
echo Checking installed packages...
echo.
echo Checking PyQt6...
python -c "import PyQt6; print('✓ PyQt6 version:', PyQt6.__version__)" 2>nul || echo ✗ PyQt6 NOT INSTALLED
echo.
echo Checking pandas...
python -c "import pandas; print('✓ pandas version:', pandas.__version__)" 2>nul || echo ✗ pandas NOT INSTALLED
echo.
echo Checking openpyxl...
python -c "import openpyxl; print('✓ openpyxl version:', openpyxl.__version__)" 2>nul || echo ✗ openpyxl NOT INSTALLED
echo.
echo Checking Pillow...
python -c "import PIL; print('✓ Pillow version:', PIL.__version__)" 2>nul || echo ✗ Pillow NOT INSTALLED
echo.
echo ================================================
echo.
echo If any packages show as NOT INSTALLED, run:
echo   install_dependencies.bat
echo.
pause

