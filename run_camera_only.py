#!/usr/bin/env python3
"""
Standalone Gesture Control with Window
======================================

This script runs ONLY the gesture control with a visible camera window.
Run this in one terminal, then run the chess game in another terminal.
"""

import sys
import time

def main():
    """Run gesture control with visible window"""
    print("📹 Hand Gesture Volume Control")
    print("=============================")
    print("This window shows your camera feed with hand tracking.")
    print("Use this to control your computer's volume while playing chess.")
    print()
    
    try:
        from gesture_control import HandGestureVolumeControl
        
        # Create gesture controller
        print("🎯 Initializing camera...")
        controller = HandGestureVolumeControl(window_name="Volume Control - Chess Game")
        
        if not controller.is_available():
            print("❌ No camera available")
            print("Make sure your camera is connected and permissions are granted")
            return 1
        
        print("✅ Camera ready!")
        print()
        print("🎮 INSTRUCTIONS:")
        print("  1. Keep this window open")
        print("  2. In another terminal, run: python main.py")
        print("  3. Play chess in that window")
        print("  4. Control volume here by pinching fingers")
        print()
        print("🎯 VOLUME CONTROLS:")
        print("  👆 Pinch Close: Lower volume")
        print("  ✋ Pinch Far: Higher volume")
        print("  Q: Quit")
        print("  R: Reset volume")
        print("  D: Toggle debug info")
        print()
        print("Starting gesture control...")
        
        # Run in main thread for proper window handling
        controller.start_gesture_control()
        
    except KeyboardInterrupt:
        print("\n👋 Gesture control stopped")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure dependencies are installed:")
        print("  source .venv/bin/activate")
        print("  pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🧹 Cleanup complete")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())