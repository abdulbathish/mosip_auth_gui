# Mac Installation Guide

## Quick Start

1. Open Terminal in this directory
2. Make scripts executable:
   ```bash
   chmod +x install.sh run.sh
   ```
3. Run installer:
   ```bash
   ./install.sh
   ```
4. Run application:
   ```bash
   ./run.sh
   ```

## Manual Installation

If the automated installer doesn't work:

1. Create virtual environment:
   ```bash
   python3 -m venv venv
   ```
2. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r ../../requirements.txt
   ```
4. Run the application:
   ```bash
   python ../../main.py
   ```

## Troubleshooting

### Python not found
- Install Python 3.10+ using Homebrew: `brew install python@3.12`
- Or download from [python.org](https://www.python.org/downloads/)

### tkinter not available
- Install: `brew install python-tk@3.12`
- Or use system Python which includes tkinter

### Permission denied
- Make scripts executable: `chmod +x *.sh`
- Or run: `bash install.sh`

