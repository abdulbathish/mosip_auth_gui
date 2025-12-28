#!/bin/bash
# Run script for MOSIP IDA Authentication Testing Tool (Mac)

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Get the project root directory (two levels up from installation/mac/)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Activate virtual environment (created in project root)
if [ ! -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    echo "ERROR: Virtual environment not found at $PROJECT_ROOT/venv"
    echo "Please run install.sh first."
    exit 1
fi

source "$PROJECT_ROOT/venv/bin/activate"

# Change to the project root directory
cd "$PROJECT_ROOT"

# Run the application
python main.py
