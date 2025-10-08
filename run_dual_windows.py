#!/usr/bin/env python3
"""
Chess Game with Visible Gesture Control
=======================================

This script launches the chess game with a visible camera window showing 
hand tracking for volume control. Both windows will be displayed side by side.
"""

import sys
import time
import threading
import subprocess
import os

def setup_windows():
    """Setup window positions for chess and camera"""
    print("Setting up dual window display...")

def run_chess_with_visible_gesture():
    """Run chess game with visible gesture control window"""
    print("🎮 Chess Game with Visible Gesture Control")
    print("==========================================")
    print("This will open TWO windows:")
    print("  1. Chess Game - Main game window")
    print("  2. Camera Feed - Hand tracking for volume control")
    print()
    
    try:
        from gesture_control import HandGestureVolumeControl
        import main
        
        # Create gesture controller with specific window positioning
        print("📹 Initializing camera for gesture control...")
        gesture_controller = HandGestureVolumeControl(window_name="Volume Control Camera")
        
        if not gesture_controller.is_available():
            print("❌ No camera available for gesture control")
            print("Starting chess game only...")
            main.main()
            return
        
        print("✅ Camera detected and ready")
        
        # Start gesture control in a separate thread with visible window
        print("🎯 Starting gesture control with visible camera window...")
        gesture_thread = threading.Thread(
            target=gesture_controller.start_gesture_control,
            daemon=False  # Don't make it daemon so window stays open
        )
        gesture_thread.start()
        
        # Give gesture control time to initialize and create window
        time.sleep(2)
        
        print("🎮 Starting chess game...")
        print()
        print("🎯 CONTROLS:")
        print("  Chess: Click and drag pieces in the main window")
        print("  Volume: Pinch thumb/index finger in camera window")
        print("  Q (in camera window): Quit gesture control")
        print("  Close chess window: End game")
        print()
        
        # Start the chess game in main thread
        main.main()
        
    except KeyboardInterrupt:
        print("\n👋 Game interrupted by user")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up gesture control
        try:
            if 'gesture_controller' in locals():
                gesture_controller.stop_threaded()
                gesture_controller.cleanup()
        except:
            pass
        print("🧹 Cleanup complete")

def main():
    """Main function"""
    print("Checking dependencies...")
    
    # Check if we're in the right environment
    try:
        import pygame
        import cv2
        import mediapipe
        import numpy
        import chess
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nTo fix this, run:")
        print("  source .venv/bin/activate")
        print("  pip install -r requirements.txt")
        return 1
    
    print("✅ All dependencies available")
    print()
    
    # Run the dual-window experience
    run_chess_with_visible_gesture()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())