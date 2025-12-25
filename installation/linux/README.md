# Linux Installation Guide

## Quick Start

1. Open terminal in this directory
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

1. Install Python and tkinter:
   ```bash
   sudo apt-get install python3 python3-venv python3-tk
   # Or for RedHat/CentOS:
   sudo yum install python3 python3-tkinter
   ```
2. Create virtual environment:
   ```bash
   python3 -m venv venv
   ```
3. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r ../../requirements.txt
   ```
5. Run the application:
   ```bash
   python ../../main.py
   ```

## Troubleshooting

### Python not found
- Install: `sudo apt-get install python3` (Debian/Ubuntu)
- Or: `sudo yum install python3` (RedHat/CentOS)

### tkinter not available
- Install: `sudo apt-get install python3-tk` (Debian/Ubuntu)
- Or: `sudo yum install python3-tkinter` (RedHat/CentOS)

### Permission denied
- Make scripts executable: `chmod +x *.sh`
- Or run: `bash install.sh`

