#!/bin/bash
# Quick Test Runner for TinyEncryptor Alpha Testing Suite
# Usage: ./run_tests.sh

echo "======================================"
echo "TinyEncryptor Alpha Testing Suite"
echo "======================================"
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Change to project root
cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run: python -m venv .venv"
    exit 1
fi

# Activate virtual environment and run tests
if [ -f ".venv/bin/python" ]; then
    # Unix-like systems
    PYTHON_CMD=".venv/bin/python"
elif [ -f ".venv/Scripts/python.exe" ]; then
    # Windows
    PYTHON_CMD=".venv/Scripts/python.exe"
else
    echo "Error: Could not find Python in virtual environment!"
    exit 1
fi

# Run the tests
echo "Running tests..."
echo ""
$PYTHON_CMD src/test/alpha_testing.py

# Capture exit code
EXIT_CODE=$?

echo ""
echo "======================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed!"
fi
echo "======================================"

exit $EXIT_CODE
