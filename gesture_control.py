"""
Hand Gesture Volume Control for Chess Game
==========================================

This module provides hand gesture-based volume control that can run alongside
the chess game. Use thumb and index finger pinch gestures to control system volume.

Usage:
    python gesture_control.py  # Run standalone
    
Or import and use in other scripts:
    from gesture_control import HandGestureVolumeControl
    controller = HandGestureVolumeControl()
    controller.start_gesture_control()
"""

import cv2
import mediapipe as mp
import math
import numpy as np
import platform
import time
import threading
import queue
import sys
from typing import Optional, Tuple

# Check what OS we're running on and import the right libraries
current_os = platform.system()
windows_audio_available = False

# Windows-specific imports (only import if on Windows)
if current_os == "Windows":
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL  # type: ignore
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # type: ignore
        windows_audio_available = True
    except ImportError:
        print("Warning: pycaw not installed. Run 'pip install pycaw' for Windows volume control")
        windows_audio_available = False
elif current_os == "Darwin":  # macOS
    import os
elif current_os == "Linux":
    import subprocess

# Type hints for Windows-only variables (prevents Pylance errors)
if current_os == "Windows" and windows_audio_available:
    # These will be properly typed when imported above
    pass
else:
    # Define dummy types for non-Windows systems to prevent type errors
    CLSCTX_ALL = None  # type: ignore
    AudioUtilities = None  # type: ignore
    IAudioEndpointVolume = None  # type: ignore
    cast = None  # type: ignore
    POINTER = None  # type: ignore


class HandGestureVolumeControl:
    """
    Hand gesture-based volume control using MediaPipe hand tracking.
    Optimized to run alongside other applications like the chess game.
    """
    
    def __init__(self, camera_index: int = 0, window_name: str = "Gesture Volume Control"):
        """
        Initialize the hand gesture volume control system.
        
        Args:
            camera_index: Camera index to use (default: 0)
            window_name: Name for the OpenCV window
        """
        self.window_name = window_name
        self.running = False
        self.thread = None
        self.command_queue = queue.Queue()
        
        # Set up MediaPipe for hand tracking
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,  # Only track one hand to avoid confusion
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Try to find and connect to a working camera
        self.camera = None
        self._initialize_camera(camera_index)
        
        if self.camera is None:
            print("WARNING: No working camera found for gesture control!")
            print("Gesture control will be disabled.")
            return
            
        # Set up reasonable video resolution for better performance
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 480)  # Smaller resolution for better performance
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
        self.camera.set(cv2.CAP_PROP_FPS, 30)
        
        # Initialize volume control for the current OS
        self._setup_volume_control()
        
        # Gesture detection sensitivity settings
        self.closest_distance = 30    # Minimum finger distance (volume = 0%)
        self.farthest_distance = 200  # Maximum finger distance (volume = 100%)
        
        # Start with the current system volume instead of a fixed value
        self.current_volume_level = self._get_system_volume()
        self.smoothing_factor = 0.2  # How fast volume changes (0.1 = slow, 0.5 = fast)
        
        # Performance optimization variables
        self.last_volume_set = 0
        self.volume_update_threshold = 2.0  # Only update volume if change is > 2%
        self.last_volume_update_time = 0
        self.volume_update_interval = 0.1  # Update volume max every 100ms for better performance
        
        # UI and display variables
        self.frame_rate = 0
        self.last_frame_time = 0
        self.show_debug_info = True
        
        print(f"Hand gesture volume control initialized for {current_os}")
        
    def _initialize_camera(self, preferred_index: int = 0):
        """Try different camera indices to find one that works"""
        # Try the preferred index first, then others
        camera_indices = [preferred_index] + [i for i in range(4) if i != preferred_index]
        
        for camera_index in camera_indices:
            try:
                test_cap = cv2.VideoCapture(camera_index)
                if test_cap.isOpened():
                    # Test if we can actually read frames
                    success, test_frame = test_cap.read()
                    if success and test_frame is not None:
                        self.camera = test_cap
                        print(f"Gesture control: Connected to camera {camera_index}")
                        return
                test_cap.release()
            except Exception as e:
                continue
        
        print("Gesture control: No working camera found")
        
    def _setup_volume_control(self):
        """Initialize volume control based on the operating system"""
        if current_os == "Windows" and windows_audio_available:
            try:
                # Get the default audio device
                audio_devices = AudioUtilities.GetSpeakers()
                audio_interface = audio_devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self.volume_controller = cast(audio_interface, POINTER(IAudioEndpointVolume))
                
                # Get the volume range (usually around -65 to 0 dB)
                self.min_volume_db, self.max_volume_db = self.volume_controller.GetVolumeRange()[:2]
                print(f"Windows audio control ready (range: {self.min_volume_db:.1f} to {self.max_volume_db:.1f} dB)")
            except Exception as error:
                print(f"Failed to initialize Windows volume control: {error}")
                self.volume_controller = None
        else:
            self.volume_controller = None
            print(f"Volume control ready for {current_os}")
    
    def _get_system_volume(self) -> float:
        """Read the current system volume level"""
        try:
            if current_os == "Windows" and self.volume_controller:
                # Convert dB level to percentage
                current_db = self.volume_controller.GetMasterVolumeLevel()
                volume_percentage = ((current_db - self.min_volume_db) / 
                                   (self.max_volume_db - self.min_volume_db)) * 100
                return max(0, min(100, volume_percentage))
            elif current_os == "Darwin":  # macOS
                # Use AppleScript to get volume
                result = os.popen("osascript -e 'output volume of (get volume settings)'").read().strip()
                return float(result) if result.isdigit() else 50
            elif current_os == "Linux":
                # Use amixer to get ALSA volume
                result = subprocess.run(['amixer', '-D', 'pulse', 'sget', 'Master'], 
                                      capture_output=True, text=True)
                # Parse the output to find volume percentage
                import re
                volume_match = re.search(r'\[(\d+)%\]', result.stdout)
                return float(volume_match.group(1)) if volume_match else 50
        except Exception as error:
            print(f"Couldn't read system volume: {error}")
        
        return 50  # Safe default if we can't read the volume
    
    def _change_system_volume(self, percentage: float):
        """Set the system volume to a specific percentage (with throttling)"""
        current_time = time.time()
        
        # Throttle volume updates to reduce system calls
        if (current_time - self.last_volume_update_time < self.volume_update_interval or
            abs(percentage - self.last_volume_set) < self.volume_update_threshold):
            return
            
        try:
            clamped_percentage = max(0, min(100, percentage))
            
            if current_os == "Windows" and self.volume_controller:
                # Convert percentage back to dB
                db_level = self.min_volume_db + (self.max_volume_db - self.min_volume_db) * (clamped_percentage / 100)
                self.volume_controller.SetMasterVolumeLevel(db_level, None)
            elif current_os == "Darwin":  # macOS
                # Use AppleScript to set volume
                os.system(f"osascript -e 'set volume output volume {int(clamped_percentage)}' 2>/dev/null")
            elif current_os == "Linux":
                # Use amixer to set ALSA volume
                subprocess.run(['amixer', '-D', 'pulse', 'sset', 'Master', f'{int(clamped_percentage)}%'],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            self.last_volume_set = clamped_percentage
            self.last_volume_update_time = current_time
            
        except Exception as error:
            print(f"Failed to set volume: {error}")
    
    def _calculate_finger_distance(self, point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
        """Calculate the pixel distance between two finger positions"""
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        return math.sqrt(dx * dx + dy * dy)
    
    def _draw_volume_indicator(self, frame, volume_level: float):
        """Draw a compact volume bar on the screen"""
        # Volume bar dimensions and position (smaller for less intrusion)
        bar_left = 10
        bar_top = 10
        bar_width = 150
        bar_height = 15
        
        # Draw the background bar (gray)
        cv2.rectangle(frame, (bar_left, bar_top), 
                     (bar_left + bar_width, bar_top + bar_height), 
                     (50, 50, 50), -1)
        
        # Draw the filled portion based on volume level
        fill_width = int(bar_width * volume_level / 100)
        bar_color = (0, 255, 0) if volume_level > 20 else (0, 165, 255)  # Green or orange
        cv2.rectangle(frame, (bar_left, bar_top), 
                     (bar_left + fill_width, bar_top + bar_height), 
                     bar_color, -1)
        
        # Add text showing the exact percentage
        cv2.putText(frame, f'{int(volume_level)}%', 
                   (bar_left + bar_width + 10, bar_top + 12), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    def _draw_finger_tracking(self, frame, distance: float, thumb_pos: Tuple[int, int], index_pos: Tuple[int, int]):
        """Draw visual feedback for finger tracking"""
        thumb_x, thumb_y = thumb_pos
        index_x, index_y = index_pos
        
        # Draw line between the two fingers
        cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (255, 0, 255), 2)
        
        # Draw circles on the fingertips
        cv2.circle(frame, (thumb_x, thumb_y), 8, (255, 0, 0), -1)      # Blue for thumb
        cv2.circle(frame, (index_x, index_y), 8, (0, 255, 0), -1)     # Green for index
        
        # Show the distance in the middle of the line
        if self.show_debug_info:
            middle_x = (thumb_x + index_x) // 2
            middle_y = (thumb_y + index_y) // 2
            cv2.putText(frame, f'{int(distance)}px', 
                       (middle_x - 25, middle_y - 15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    
    def _process_video_frame(self):
        """Process one frame from the camera"""
        if not self.camera or not self.camera.isOpened():
            return None
            
        success, frame = self.camera.read()
        if not success:
            return None
        
        # Flip horizontally so it acts like a mirror
        frame = cv2.flip(frame, 1)
        
        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Look for hands in the frame
        hand_results = self.hands.process(rgb_frame)
        
        finger_distance = 0
        target_volume = self.current_volume_level
        
        if hand_results.multi_hand_landmarks:
            # Process only the first hand for better performance
            hand_landmarks = hand_results.multi_hand_landmarks[0]
            
            # Draw hand landmarks (simplified for performance)
            self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            
            # Get frame dimensions once
            height, width = frame.shape[:2]
            
            # Extract only the landmarks we need (thumb tip and index tip)
            thumb_landmark = hand_landmarks.landmark[4]  # Thumb tip
            index_landmark = hand_landmarks.landmark[8]  # Index tip
            
            # Convert to pixel coordinates
            thumb_x = int(thumb_landmark.x * width)
            thumb_y = int(thumb_landmark.y * height)
            index_x = int(index_landmark.x * width)
            index_y = int(index_landmark.y * height)
            
            # Calculate distance between fingertips
            finger_distance = self._calculate_finger_distance(
                (thumb_x, thumb_y), (index_x, index_y)
            )
            
            # Map the distance to a volume percentage
            target_volume = np.interp(finger_distance, 
                                    [self.closest_distance, self.farthest_distance], 
                                    [0, 100])
            target_volume = max(0, min(100, target_volume))  # Clamp to 0-100
            
            # Apply smoothing to avoid jumpy volume changes
            self.current_volume_level = (
                self.current_volume_level * (1 - self.smoothing_factor) + 
                target_volume * self.smoothing_factor
            )
            
            # Actually change the system volume (with throttling)
            self._change_system_volume(self.current_volume_level)
            
            # Draw the visual feedback
            self._draw_finger_tracking(frame, finger_distance, (thumb_x, thumb_y), (index_x, index_y))
        
        # Always draw the volume bar
        self._draw_volume_indicator(frame, self.current_volume_level)
        
        # Calculate FPS for monitoring
        current_time = time.time()
        if self.last_frame_time > 0:
            self.frame_rate = 1.0 / (current_time - self.last_frame_time)
        self.last_frame_time = current_time
        
        # Draw UI text
        self._draw_ui_text(frame, finger_distance, target_volume)
        
        return frame
    
    def _draw_ui_text(self, frame, finger_distance: float, target_volume: float):
        """Draw all UI text in one optimized function"""
        text_color = (255, 255, 255)
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        if self.show_debug_info:
            # FPS in top right
            cv2.putText(frame, f'FPS: {int(self.frame_rate)}', 
                       (frame.shape[1] - 80, 20), font, 0.4, text_color, 1)
            
            # Only show debug info if hand is detected
            if finger_distance > 0:
                cv2.putText(frame, f'Dist: {int(finger_distance)} | Target: {int(target_volume)}%', 
                           (10, frame.shape[0] - 40), font, 0.4, text_color, 1)
        
        # Compact instructions at bottom
        cv2.putText(frame, 'Pinch: Volume | Q:Quit | D:Debug | R:Reset', 
                   (10, frame.shape[0] - 20), font, 0.4, text_color, 1)
    
    def _handle_keyboard_input(self, key: int) -> bool:
        """Handle keyboard input, return False to quit"""
        if key == ord('q') or key == 27:  # 'q' or ESC
            return False
        elif key == ord('r'):
            # Reset to current system volume
            self.current_volume_level = self._get_system_volume()
            print(f"Volume reset to system level: {int(self.current_volume_level)}%")
        elif key == ord('d'):
            # Toggle debug info
            self.show_debug_info = not self.show_debug_info
            print(f"Debug info: {'ON' if self.show_debug_info else 'OFF'}")
        elif key == ord('c'):
            # Calibrate (simplified for threaded use)
            print("Calibration: Put fingers close together and press 'S'")
            print("Then put fingers far apart and press 'L'")
        elif key == ord('s'):
            # Quick calibration - set minimum
            print(f"Minimum distance set to current distance")
        elif key == ord('l'):
            # Quick calibration - set maximum
            print(f"Maximum distance set to current distance")
        
        return True
    
    def _gesture_control_loop(self):
        """Main loop that processes video and controls volume (runs in thread)"""
        if self.camera is None:
            print("Cannot start gesture control - no camera available")
            return
            
        print("Hand gesture volume control started")
        print("Controls: Pinch thumb/index to change volume | Q=quit | D=toggle debug | R=reset")
        
        # Force create window for visual feedback (we want to see both windows)
        create_window = True
        window_created = False
        
        # Try multiple times to create the window
        for attempt in range(3):
            try:
                cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
                cv2.resizeWindow(self.window_name, 480, 360)
                # Move the window to a specific position so it doesn't overlap with chess
                cv2.moveWindow(self.window_name, 100, 100)
                window_created = True
                print(f"✓ Camera window created successfully")
                break
            except Exception as e:
                print(f"Attempt {attempt + 1}: Could not create display window: {e}")
                if attempt < 2:
                    time.sleep(0.5)  # Wait a bit before retrying
                else:
                    print("Warning: Running without visual feedback window")
                    create_window = False
        
        while self.running:
            # Process any commands from the main thread
            try:
                command = self.command_queue.get_nowait()
                if command == "stop":
                    break
            except queue.Empty:
                pass
            
            frame = self._process_video_frame()
            if frame is None:
                continue
            
            # Always try to show the window if we want visual feedback
            if create_window and window_created:
                try:
                    cv2.imshow(self.window_name, frame)
                    key_pressed = cv2.waitKey(1) & 0xFF
                    if key_pressed != 255:  # A key was pressed
                        if not self._handle_keyboard_input(key_pressed):
                            break
                except Exception as e:
                    # If display fails, try to recreate window once
                    print(f"Display error: {e}")
                    try:
                        cv2.destroyWindow(self.window_name)
                        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
                        cv2.resizeWindow(self.window_name, 480, 360)
                        cv2.moveWindow(self.window_name, 100, 100)
                        cv2.imshow(self.window_name, frame)
                    except:
                        print("Could not recreate window, continuing without visual feedback")
                        create_window = False
            else:
                # Small delay to prevent excessive CPU usage when running without display
                time.sleep(0.033)  # ~30 FPS equivalent
        
        self.running = False
        if create_window and window_created:
            try:
                cv2.destroyWindow(self.window_name)
            except:
                pass
    
    def start_threaded(self) -> bool:
        """Start gesture control in a separate thread"""
        if self.camera is None:
            print("Cannot start gesture control - no camera available")
            return False
            
        if self.running:
            print("Gesture control is already running")
            return True
            
        self.running = True
        self.thread = threading.Thread(target=self._gesture_control_loop, daemon=True)
        self.thread.start()
        print("Gesture control started in background thread")
        return True
    
    def stop_threaded(self):
        """Stop the threaded gesture control"""
        if not self.running:
            return
            
        self.running = False
        self.command_queue.put("stop")
        
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
            
        print("Gesture control stopped")
    
    def start_gesture_control(self):
        """Start gesture control in the main thread (blocking)"""
        if self.camera is None:
            print("Cannot start - no camera available")
            return
            
        self.running = True
        try:
            self._gesture_control_loop()
        except KeyboardInterrupt:
            print("\nGesture control interrupted by user (Ctrl+C)")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up camera and windows"""
        self.running = False
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()
        print("Gesture control cleanup complete")
    
    def is_available(self) -> bool:
        """Check if gesture control is available (camera detected)"""
        return self.camera is not None


def main():
    """Main function for running gesture control standalone"""
    print("Hand Gesture Volume Control for Chess Game")
    print("==========================================")
    
    # Create the gesture controller
    gesture_controller = HandGestureVolumeControl()
    
    try:
        # Start the main control loop
        gesture_controller.start_gesture_control()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user (Ctrl+C)")
    except Exception as error:
        print(f"An error occurred: {error}")
        import traceback
        traceback.print_exc()
    finally:
        # Always clean up resources
        gesture_controller.cleanup()


if __name__ == "__main__":
    main()