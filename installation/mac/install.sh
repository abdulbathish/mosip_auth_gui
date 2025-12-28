#!/bin/bash
# Installation script for MOSIP Auth GUI (Mac/Linux)

echo "=========================================="
echo "MOSIP IDA Authentication Testing Tool - Installer"
echo "=========================================="
echo ""

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Get the project root directory (two levels up from installation/mac/)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Determine which Python to use (prefer python3.12, fallback to python3)
if command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
    echo "Using python3.12"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo "Using python3"
else
    echo "ERROR: Python 3 is not installed. Please install Python 3.10+ first."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Found Python $PYTHON_VERSION"

# Check Python version (need 3.10+)
if ! $PYTHON_CMD -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "ERROR: Python 3.10+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment in project root
echo ""
echo "Creating virtual environment..."
cd "$PROJECT_ROOT"
$PYTHON_CMD -m venv venv

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
if $PYTHON_CMD -c "import tkinter" 2>/dev/null; then
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
APP_BUNDLE="$DESKTOP_DIR/$APP_NAME.app"
CONTENTS_DIR="$APP_BUNDLE/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

if [ -f "$PROJECT_ROOT/logo.png" ]; then
    cp "$PROJECT_ROOT/logo.png" "$RESOURCES_DIR/logo.png"
fi

cat > "$CONTENTS_DIR/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>mosip_auth_gui</string>
    <key>CFBundleIdentifier</key>
    <string>com.mosip.auth.gui</string>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleIconFile</key>
    <string>logo</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>
EOF

cat > "$MACOS_DIR/mosip_auth_gui" << 'LAUNCHER_EOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../.." && pwd)"

if [ ! -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    osascript -e 'display dialog "Virtual environment not found. Please run install.sh first." buttons {"OK"} default button "OK" with icon stop'
    exit 1
fi

source "$PROJECT_ROOT/venv/bin/activate"
cd "$PROJECT_ROOT"
python main.py
LAUNCHER_EOF

chmod +x "$MACOS_DIR/mosip_auth_gui"
chmod +x "$PROJECT_ROOT/installation/mac/run.sh"

if [ -d "$APP_BUNDLE" ]; then
    echo "Desktop shortcut created at: $APP_BUNDLE"
    echo "You can now launch the application from your Desktop."
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
echo "Or double-click the desktop shortcut: $APP_BUNDLE"
echo ""
