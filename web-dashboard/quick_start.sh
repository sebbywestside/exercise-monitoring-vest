#!/bin/bash

# Exercise Monitoring Vest - Quick Start Script
# This script helps you get started with the web dashboard

echo "=========================================="
echo "Exercise Monitoring Vest - Quick Start"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed"
    echo "Please install pip3"
    exit 1
fi

echo "✅ pip3 found"
echo ""

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Connect your Arduino Mega via USB"
echo ""
echo "2. Find your serial port:"
echo "   Mac/Linux: ls /dev/cu.* /dev/ttyUSB*"
echo "   Windows: Check Device Manager"
echo ""
echo "3. Update serial_bridge.py with your port:"
echo "   Edit line 13: SERIAL_PORT = '/dev/cu.usbserial-XXXX'"
echo ""
echo "4. Start the WebSocket bridge:"
echo "   python3 serial_bridge.py"
echo ""
echo "5. Open the dashboard in your browser:"
echo "   exercise_vest_dashboard.html"
echo ""
echo "=========================================="
echo "Testing Without Hardware:"
echo "=========================================="
echo ""
echo "To test the dashboard without Arduino:"
echo "   python3 test_data_generator.py"
echo ""
echo "This will generate simulated sensor data"
echo ""
echo "=========================================="
echo "✅ Setup complete! Follow the steps above."
echo "=========================================="
