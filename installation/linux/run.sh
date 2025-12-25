#!/bin/bash
# Run script for MOSIP Authentication GUI (Linux)

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# Get the project root directory (two levels up)
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Activate virtual environment (created in project root)
source "$PROJECT_ROOT/venv/bin/activate"

# Change to the project root directory
cd "$PROJECT_ROOT"

# Run the application
python main.py
