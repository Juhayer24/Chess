#!/usr/bin/env python3
"""
Test script to verify gesture control integration works properly
"""

import sys
import time
import threading

def test_gesture_control_standalone():
    """Test gesture control as a standalone module"""
    print("=== Testing Gesture Control Standalone ===")
    
    try:
        from gesture_control import HandGestureVolumeControl
        
        controller = HandGestureVolumeControl()
        
        if controller.is_available():
            print("✓ Gesture control initialized successfully")
            print("✓ Camera detected and working")
            print("✓ Volume control system ready")
            
            # Test threaded mode
            if controller.start_threaded():
                print("✓ Background thread started successfully")
                
                # Let it run for a few seconds
                print("Running gesture control for 5 seconds...")
                print("Try pinching your thumb and index finger to test volume control!")
                time.sleep(5)
                
                # Stop the thread
                controller.stop_threaded()
                print("✓ Background thread stopped successfully")
            else:
                print("✗ Failed to start background thread")
                return False
            
            controller.cleanup()
            print("✓ Cleanup completed successfully")
            return True
            
        else:
            print("⚠ No camera available for gesture control")
            print("  This is normal if no camera is connected")
            return True  # Not an error, just unavailable
            
    except Exception as e:
        print(f"✗ Error testing gesture control: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_integration():
    """Test that main.py can import and initialize gesture control"""
    print("\n=== Testing Main.py Integration ===")
    
    try:
        # Test the import that main.py would do
        from gesture_control import HandGestureVolumeControl
        
        # Create controller like main.py does
        controller = HandGestureVolumeControl(window_name="Volume Control (Chess)")
        
        if controller.is_available():
            print("✓ Integration import successful")
            print("✓ Controller creation successful")
            print("✓ Camera available for integration")
        else:
            print("✓ Integration import successful")
            print("✓ Controller creation successful")
            print("⚠ No camera available (this is OK)")
        
        controller.cleanup()
        print("✓ Integration test completed")
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """Test all required dependencies"""
    print("\n=== Testing Dependencies ===")
    
    required_packages = [
        ('pygame', 'pygame'),
        ('cv2', 'opencv-python'),
        ('mediapipe', 'mediapipe'),
        ('numpy', 'numpy')
    ]
    
    all_good = True
    
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"✓ {package_name} installed and importable")
        except ImportError:
            print(f"✗ {package_name} missing or not importable")
            all_good = False
    
    # Test platform-specific audio (optional)
    import platform
    current_os = platform.system()
    print(f"✓ Running on {current_os}")
    
    if current_os == "Windows":
        try:
            import pycaw  # type: ignore
            import comtypes  # type: ignore
            print("✓ Windows audio libraries available")
        except ImportError:
            print("⚠ Windows audio libraries not available (install pycaw)")
    elif current_os == "Darwin":
        print("✓ macOS audio control will use AppleScript")
    elif current_os == "Linux":
        print("✓ Linux audio control will use amixer")
    
    return all_good

def main():
    """Run all tests"""
    print("Chess Game Gesture Control Integration Test")
    print("=" * 50)
    
    # Test dependencies first
    deps_ok = test_dependencies()
    
    if not deps_ok:
        print("\n❌ Dependency test failed!")
        print("Please install missing packages with: pip install -r requirements.txt")
        return False
    
    # Test gesture control standalone
    gesture_ok = test_gesture_control_standalone()
    
    # Test main.py integration
    integration_ok = test_main_integration()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    print(f"Dependencies: {'✓ PASS' if deps_ok else '✗ FAIL'}")
    print(f"Gesture Control: {'✓ PASS' if gesture_ok else '✗ FAIL'}")
    print(f"Integration: {'✓ PASS' if integration_ok else '✗ FAIL'}")
    
    if deps_ok and gesture_ok and integration_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("Your gesture control integration is ready to use!")
        print("\nTo start the chess game with gesture control:")
        print("  python main.py")
        print("  python launcher.py")
        return True
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Please check the error messages above and fix any issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)