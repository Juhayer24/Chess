#!/bin/bash

# Quick starter for dual windows
echo "🎮 Starting Chess Game with Camera Window"
echo "========================================"

# Start camera window in background
echo "📹 Opening camera window..."
source .venv/bin/activate && python run_camera_only.py &
CAMERA_PID=$!

# Wait a moment for camera to initialize
sleep 3

# Start chess game
echo "🎮 Opening chess game..."
source .venv/bin/activate && python main.py

# When chess game closes, also close camera
echo "🧹 Cleaning up..."
kill $CAMERA_PID 2>/dev/null

echo "👋 All windows closed!"