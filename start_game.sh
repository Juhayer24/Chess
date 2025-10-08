#!/bin/bash

# Chess Game with Gesture Volume Control Starter Script
# =====================================================

echo "🎮 Starting Chess Game with Gesture Volume Control"
echo "=================================================="

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
python -c "import pygame, cv2, mediapipe, numpy, chess" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing dependencies! Installing..."
    pip install -r requirements.txt
fi

echo "✅ Dependencies ready!"
echo ""

# Display instructions
echo "🎯 GAME CONTROLS:"
echo "  Chess: Click and drag pieces in the game window"
echo "  Volume: Pinch thumb and index finger (close = quiet, far = loud)"
echo ""
echo "⌨️  GESTURE CONTROLS:"
echo "  Q: Quit gesture control"
echo "  R: Reset volume"
echo "  D: Toggle debug info"
echo ""

# Start the game
echo "🚀 Starting chess game with integrated gesture control..."
echo "   (Gesture control runs automatically in background)"
echo ""

# Run the main game
python main.py

echo ""
echo "👋 Game ended. Thanks for playing!"