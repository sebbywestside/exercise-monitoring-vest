#!/bin/bash

# Exercise Monitoring Vest - Dashboard Test Runner
# Easy testing without Arduino hardware

echo "=========================================="
echo "🧪 Dashboard Testing Menu"
echo "=========================================="
echo ""
echo "Choose a testing mode:"
echo ""
echo "1. Mock Data Server (Recommended)"
echo "   → Realistic simulation with 10-minute loop"
echo "   → Perfect for demos and development"
echo ""
echo "2. Quick Demo (30 seconds)"
echo "   → Fast preview of all activity phases"
echo "   → Great for screenshots"
echo ""
echo "3. Stress Test"
echo "   → High-frequency data (10 Hz)"
echo "   → Tests dashboard performance"
echo ""
echo "4. Custom Duration"
echo "   → Specify how long to run"
echo ""
echo "0. Exit"
echo ""
read -p "Enter choice (0-4): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting Mock Data Server..."
        echo ""
        echo "Keep this terminal open!"
        echo "Open dashboard.html in your browser"
        echo ""
        echo "Press Ctrl+C to stop"
        echo ""
        python3 mock_data_server.py
        ;;
    
    2)
        echo ""
        echo "🎬 Starting Quick Demo..."
        echo ""
        python3 test_data_generator.py demo
        ;;
    
    3)
        echo ""
        echo "🔥 Starting Stress Test..."
        read -p "Duration in seconds (default: 60): " duration
        duration=${duration:-60}
        echo ""
        python3 test_data_generator.py stress $duration
        ;;
    
    4)
        echo ""
        read -p "Duration in seconds: " duration
        echo ""
        echo "🏃 Running simulation for $duration seconds..."
        python3 test_data_generator.py normal $duration
        ;;
    
    0)
        echo ""
        echo "👋 Goodbye!"
        exit 0
        ;;
    
    *)
        echo ""
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
