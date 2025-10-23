@echo off
echo QuantForge Backtest Manager - Dependency Installation
echo ====================================================
echo.
echo Checking Python installation...
python --version
echo.
echo Installing required packages...
echo.
python -m ensurepip --default-pip
python -m pip install --upgrade pip
python -m pip install PyQt6
python -m pip install pandas
python -m pip install openpyxl
python -m pip install Pillow
echo.
echo ====================================================
echo Testing installation...
python -c "import PyQt6; print('PyQt6 installed successfully')"
python -c "import pandas; print('pandas installed successfully')"
python -c "import openpyxl; print('openpyxl installed successfully')"
python -c "import PIL; print('Pillow installed successfully')"
echo.
echo ====================================================
echo Installation complete!
echo.
echo You can now run the application using run_app.bat
echo or by running: python main.py
echo.
pause

