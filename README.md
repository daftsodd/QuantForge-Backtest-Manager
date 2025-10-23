# QuantForge Backtest Manager

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

A professional desktop application for managing and visualizing quantitative trading strategy backtests. Built with PyQt6 for a modern, native Windows experience.

---

## Quick Start

### 1. Install Dependencies

**Your Python is missing pip!** First, install pip:

Open Command Prompt in this folder and run:
```bash
python -m ensurepip --default-pip
```

Then install packages:
```bash
python -m pip install PyQt6 pandas openpyxl Pillow
```

**OR use the batch file:**
```
Double-click: install_dependencies.bat
```

### 2. Run the Application

```
Double-click: run_app.bat
```

**OR from command line:**
```bash
python main.py
```

### 3. Use the App

1. **File > Open Folder** → Select this folder
2. Click on `StrategyBacktestExample.py` to view code
3. Right-click → **Execute Script** (or press F5)
4. Watch execution in console with progress bar
5. View results automatically in the Results panel

---

## Features

### 4-Panel Layout
- **Left:** File browser with folder tree
- **Top-Right:** Syntax-highlighted code viewer (read-only)
- **Middle-Right:** Live execution console with progress tracking
- **Bottom-Right:** Results viewer with 4 tabs

### Results Viewer Tabs
1. **Overview** - Summary cards with key metrics
2. **Statistics** - Detailed metrics table
3. **Data Tables** - Full Excel data display
4. **Visualizations** - Heatmaps and charts

### Execution Features
- Live console output streaming
- Real-time progress bar with total progress across chunks
- ETA estimation for completion time
- Elapsed time tracking
- Status per file: Not Run, Running, Completed, Failed

---

## Keyboard Shortcuts

- **Ctrl+O** - Open Folder
- **Ctrl+I** - Import File
- **F5** - Run Script / Refresh
- **Ctrl+C** - Stop Execution
- **Ctrl+Q** - Exit

---

## Troubleshooting

### Error: "No module named 'PyQt6'"

**Your Python 3.13.3 is missing pip.** Fix it:

1. Open Command Prompt in this folder
2. Run: `python -m ensurepip --default-pip`
3. Run: `python -m pip install PyQt6 pandas openpyxl Pillow`
4. Run: `python main.py`

### Error: "python is not recognized"

Try using `py` instead:
```bash
py -m ensurepip --default-pip
py -m pip install PyQt6 pandas openpyxl Pillow
py main.py
```

### Check Installation

Run: `check_installation.bat`

You should see:
```
✓ PyQt6 version: 6.x.x
✓ pandas version: 2.x.x
✓ openpyxl version: 3.x.x
✓ Pillow version: 10.x.x
```

### Manual Installation Steps

```bash
# 1. Ensure pip is installed
python -m ensurepip --default-pip

# 2. Upgrade pip
python -m pip install --upgrade pip

# 3. Install packages one by one
python -m pip install PyQt6
python -m pip install pandas
python -m pip install openpyxl
python -m pip install Pillow

# 4. Verify installation
python -c "import PyQt6; print('Success!')"

# 5. Run the app
python main.py
```

---

## Expected Output from Scripts

Your backtest scripts should generate:
- **`.xlsx` files** - Excel with results
- **`.png`/`.jpg` files** - Visualizations

The app automatically finds and displays these files.

---

## Git Workflow

### First Time Setup

1. **Create GitHub repository** (do not initialize with README, .gitignore, or license)
2. **Initialize and push:**

```bash
git init
git add -A
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git push -u origin main
```

### Daily Workflow

**Start Session (Pull Latest):**
```bash
# Easy way:
Double-click: git_start_session.bat

# Manual way:
git fetch origin
git reset --hard origin/main
git clean -nd
git clean -fd
```

**End Session (Push Changes):**
```bash
# Easy way:
Double-click: git_end_session.bat

# Manual way:
git add -A
git commit -m "Your commit message"
git fetch origin
git push --force-with-lease origin HEAD:main
```

### Useful Git Commands

```bash
# Check status
git status

# View changes
git diff

# View commit history
git log --oneline

# Undo last commit (keep changes)
git reset --soft HEAD~1

# View remote URL
git remote -v
```

---

## Application Layout

```
┌──────────────────────────────────────────────────────────┐
│ File | View | Execute | Help                             │
├──────────────┬───────────────────────────────────────────┤
│              │ Code Viewer (Syntax Highlighted)          │
│ File Browser ├───────────────────────────────────────────┤
│              │ Execution Console                         │
│ □ folder/    │ ┌─────────────────────────────────────┐   │
│   📄 script1 │ │ Progress Bar | ETA | Elapsed Time   │   │
│   📄 script2 │ └─────────────────────────────────────┘   │
│              │ Live Console Output...                    │
│ Status:      ├───────────────────────────────────────────┤
│ ⚪ Not Run   │ Results: [Overview][Stats][Tables][Viz]  │
│ 🔵 Running   │                                           │
│ 🟢 Completed │ Summary Cards & Visualizations            │
│ 🔴 Failed    │                                           │
└──────────────┴───────────────────────────────────────────┘
```

---

## Configuration

Settings auto-save to `config.json`:
- Last opened folder
- Window size and position
- Recent folders

---

## Files in This Project

### Application Files
- `main.py` - Main application window
- `config_manager.py` - Settings management
- `file_browser.py` - File tree navigation
- `code_viewer.py` - Syntax-highlighted viewer
- `execution_engine.py` - Script execution engine
- `progress_widget.py` - Progress tracking with ETA
- `results_parser.py` - Results extraction
- `results_viewer.py` - Results display

### Utility Files
- `install_dependencies.bat` - Install packages
- `install_with_launcher.bat` - Install using `py` command
- `run_app.bat` - Launch app
- `run_app_with_launcher.bat` - Launch using `py` command
- `check_installation.bat` - Verify installation
- `git_start_session.bat` - Pull latest from GitHub
- `git_end_session.bat` - Push changes to GitHub

### Example
- `StrategyBacktestExample.py` - Example backtest script

---

## System Requirements

- Windows 10+
- Python 3.8+ (you have 3.13.3 ✓)
- 4GB RAM minimum
- Display: 1920x1080 recommended

---

## What Gets Uploaded to GitHub

**✅ Uploaded:**
- All Python source files
- Documentation files
- Batch scripts
- Example files

**❌ NOT Uploaded (in .gitignore):**
- `__pycache__/` folders
- `config.json` (your personal settings)
- `*_execution.json` (execution logs)
- `*.xlsx` (result files)
- `*.png`, `*.jpg` (generated charts)
- IDE settings

---

## Notes

- All panels are **resizable** (drag borders)
- Scripts run in their own directory
- Execution logs saved as `{script_name}_execution.json`
- Results are cached for fast viewing
- Code viewer is **read-only** (won't modify your files)
- Progress bar shows **total progress** across all chunks with ETA

---

## Quick Test

After installing dependencies, test PyQt6:

```bash
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 works!')"
```

If that works, launch the app:
```bash
python main.py
```

---

## Support

If you're still having issues:

1. Check Python version: `python --version` (should be 3.8+)
2. Check pip: `python -m pip --version`
3. List packages: `python -m pip list`
4. Run check: `check_installation.bat`

**Most Common Issue:** Missing pip
- Solution: `python -m ensurepip --default-pip`

---

## License

MIT License - Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

---

**Happy Backtesting! 📈**
