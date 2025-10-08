#!/usr/bin/env python3
"""
Chess Game with Gesture Control Launcher
========================================

This script launches both the chess game and the hand gesture volume control
simultaneously. The gesture control runs in a separate thread so both can
operate independently.

Usage:
    python launcher.py [options]

Options:
    --no-gesture    Start only the chess game without gesture control
    --gesture-only  Start only the gesture control
    --help         Show this help message
"""

import sys
import argparse
import threading
import time
import signal
from typing import Optional

def check_dependencies():
    """Check if all required packages are installed"""
    missing_packages = []
    
    try:
        import pygame
    except ImportError:
        missing_packages.append("pygame")
    
    try:
        import cv2
        import mediapipe
        import numpy
    except ImportError as e:
        missing_packages.append("opencv-python, mediapipe, numpy")
    
    if missing_packages:
        print("ERROR: Missing required packages!")
        print("Please install them with:")
        print(f"    pip install {' '.join(missing_packages)}")
        print("\nOr install all requirements:")
        print("    pip install -r requirements.txt")
        return False
    
    return True

def run_chess_game():
    """Run the chess game in the main thread"""
    try:
        print("Starting Chess Game...")
        import main
        main.main()
    except KeyboardInterrupt:
        print("\nChess game interrupted by user")
    except Exception as e:
        print(f"Error running chess game: {e}")
        import traceback
        traceback.print_exc()

def run_gesture_control():
    """Run gesture control in a separate thread"""
    try:
        print("Starting Hand Gesture Volume Control...")
        from gesture_control import HandGestureVolumeControl
        
        controller = HandGestureVolumeControl(window_name="Volume Control (Chess)")
        if controller.is_available():
            controller.start_gesture_control()
        else:
            print("Gesture control not available - no camera detected")
    except KeyboardInterrupt:
        print("\nGesture control interrupted by user")
    except Exception as e:
        print(f"Error running gesture control: {e}")
        import traceback
        traceback.print_exc()

def run_both():
    """Run both chess game and gesture control simultaneously"""
    print("Chess Game with Gesture Control Launcher")
    print("=======================================")
    print("Starting both chess game and gesture control...")
    print("Press Ctrl+C to quit both applications")
    print()
    
    # Import gesture control to check availability
    try:
        from gesture_control import HandGestureVolumeControl
        gesture_controller = HandGestureVolumeControl(window_name="Volume Control (Chess)")
        
        if gesture_controller.is_available():
            # Start gesture control in a background thread
            gesture_thread = threading.Thread(
                target=lambda: gesture_controller.start_gesture_control(),
                daemon=True
            )
            gesture_thread.start()
            print("✓ Gesture control started in background")
            
            # Small delay to let gesture control initialize
            time.sleep(1)
        else:
            print("⚠ Gesture control unavailable - no camera detected")
            print("  Only chess game will start")
            
    except Exception as e:
        print(f"⚠ Could not initialize gesture control: {e}")
        print("  Only chess game will start")
    
    # Run chess game in main thread
    try:
        print("✓ Starting chess game...")
        run_chess_game()
    except KeyboardInterrupt:
        print("\n✓ Shutting down...")
    finally:
        print("✓ Cleanup complete")

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\nShutting down...")
    sys.exit(0)

def main():
    """Main launcher function"""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Launch chess game with optional gesture control",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python launcher.py                 # Start both chess and gesture control
    python launcher.py --no-gesture    # Start only chess game
    python launcher.py --gesture-only  # Start only gesture control
        """
    )
    
    parser.add_argument(
        '--no-gesture', 
        action='store_true',
        help='Start only the chess game without gesture control'
    )
    
    parser.add_argument(
        '--gesture-only', 
        action='store_true',
        help='Start only the gesture control'
    )
    
    args = parser.parse_args()
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    try:
        if args.gesture_only:
            # Run only gesture control
            print("Starting gesture control only...")
            run_gesture_control()
        elif args.no_gesture:
            # Run only chess game
            print("Starting chess game only...")
            run_chess_game()
        else:
            # Run both (default)
            run_both()
    except KeyboardInterrupt:
        print("\n✓ Launcher interrupted by user")
    except Exception as e:
        print(f"✗ Launcher error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()