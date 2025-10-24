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
REM Prefer installing from requirements.txt to keep versions in sync
IF EXIST requirements.txt (
    echo Using requirements.txt
    python -m pip install -r requirements.txt
) ELSE (
    echo requirements.txt not found, installing core packages individually
    python -m pip install PyQt6 pandas openpyxl Pillow numpy numba joblib tqdm tqdm-joblib
)
echo.
echo ====================================================
echo Testing installation...
python -c "import PyQt6; print('PyQt6 installed successfully')"
python -c "import pandas; print('pandas installed successfully')"
python -c "import openpyxl; print('openpyxl installed successfully')"
python -c "import PIL; print('Pillow installed successfully')"
python -c "import numpy; print('numpy installed successfully')"
python -c "import numba; print('numba installed successfully')"
python -c "import joblib; print('joblib installed successfully')"
python -c "import tqdm; print('tqdm installed successfully')"
python -c "import tqdm_joblib; print('tqdm_joblib installed successfully')"
echo.
echo ====================================================
echo Installation complete!
echo.
echo You can now run the application using run_app.bat
echo or by running: python main.py
echo.
pause

