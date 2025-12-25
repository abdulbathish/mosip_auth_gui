# Windows Installation Guide

## Quick Start

1. Double-click `install.bat`
2. Wait for installation to complete (1-2 minutes)
3. Double-click `run.bat` to start the application

## Manual Installation

If the automated installer doesn't work:

1. Open Command Prompt in this directory
2. Create virtual environment:
   ```
   python -m venv venv
   ```
3. Activate virtual environment:
   ```
   venv\Scripts\activate
   ```
4. Install dependencies:
   ```
   pip install -r ../../requirements.txt
   ```
5. Run the application:
   ```
   python ../../main.py
   ```

## Troubleshooting

### Python not found
- Install Python 3.10+ from [python.org](https://www.python.org/downloads/)
- Check "Add Python to PATH" during installation

### tkinter not available
- Reinstall Python and select "tcl/tk" option
- Or install: `pip install tk`

### Virtual environment errors
- Run Command Prompt as Administrator
- Try: `python -m venv --clear venv`
