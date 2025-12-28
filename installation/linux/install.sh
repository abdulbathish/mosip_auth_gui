#!/bin/bash
# Installation script for MOSIP Auth GUI (Linux)

echo "=========================================="
echo "MOSIP IDA Authentication Testing Tool - Installer"
echo "=========================================="
echo ""

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Get the project root directory (two levels up from installation/linux/)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed. Please install Python 3.10+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Found Python $PYTHON_VERSION"

# Check Python version (need 3.10+)
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "ERROR: Python 3.10+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment in project root
echo ""
echo "Creating virtual environment..."
cd "$PROJECT_ROOT"
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "Installing dependencies..."
pip install -r "$PROJECT_ROOT/requirements.txt" --quiet

# Check if tkinter is available
echo "Checking for tkinter support..."
if python3 -c "import tkinter" 2>/dev/null; then
    echo "tkinter is available"
else
    echo "WARNING: tkinter is not available."
    # Try to install python-tk (Linux)
    if command -v apt-get &> /dev/null; then
        echo "Please run: sudo apt-get install python3-tk"
    elif command -v yum &> /dev/null; then
        echo "Please run: sudo yum install python3-tkinter"
    elif command -v brew &> /dev/null; then
        echo "Please run: brew install python-tk"
    else
        echo "Please install tkinter for your system"
    fi
fi

echo ""
echo "Creating desktop shortcut..."
DESKTOP_DIR="$HOME/Desktop"
APP_NAME="MOSIP IDA Authentication Testing Tool"
DESKTOP_FILE="$DESKTOP_DIR/mosip-auth-gui.desktop"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=$APP_NAME
Comment=MOSIP IDA Authentication Testing Tool
Exec=$PROJECT_ROOT/installation/linux/run.sh
Icon=$PROJECT_ROOT/logo.png
Terminal=false
Categories=Utility;Security;
EOF

chmod +x "$DESKTOP_FILE"
chmod +x "$PROJECT_ROOT/installation/linux/run.sh"

if [ -f "$DESKTOP_FILE" ]; then
    echo "Desktop shortcut created at: $DESKTOP_FILE"
    echo "You may need to right-click the shortcut and select 'Allow Launching' if it doesn't work immediately."
else
    echo "Warning: Could not create desktop shortcut"
fi

echo ""
echo "=========================================="
echo "Installation complete!"
echo "=========================================="
echo ""
echo "To run the application:"
echo "  ./run.sh"
echo ""
echo "Or manually:"
echo "  cd $PROJECT_ROOT"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Or double-click the desktop shortcut: $DESKTOP_FILE"
echo ""
