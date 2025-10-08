# Chess Game with Hand Gesture Volume Control

A chess game enhanced with hand gesture volume control using computer vision. Control your system volume by pinching your thumb and index finger while playing chess!

## Features

- **Classic Chess Game**: Full-featured chess game with a clean interface
- **AI Opponent**: Play against an AI with adjustable difficulty
- **Hand Gesture Volume Control**: Control system volume using thumb and index finger pinch gestures
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Threaded Operation**: Gesture control runs independently alongside the chess game

## Installation

### 1. Clone or Download the Project
```bash
cd /Users/juhayerislam/Desktop/Chess
```

### 2. Set Up Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### Dependencies Installed:
- `pygame` - For the chess game interface
- `opencv-python` - For camera access and image processing
- `mediapipe` - For hand tracking and gesture recognition
- `numpy` - For mathematical operations
- `pycaw` & `comtypes` - For Windows audio control (Windows only)

## Usage

### Option 1: Launcher Script (Recommended)
```bash
# Start both chess game and gesture control
python launcher.py

# Start only the chess game
python launcher.py --no-gesture

# Start only gesture control
python launcher.py --gesture-only
```

### Option 2: Individual Components
```bash
# Start chess game with integrated gesture control
python main.py

# Start gesture control standalone
python gesture_control.py
```

## Hand Gesture Controls

### Volume Control:
- **Pinch Close**: Thumb and index finger close together = Lower volume
- **Pinch Far**: Thumb and index finger far apart = Higher volume
- **Smooth Control**: Volume changes smoothly based on finger distance

### Keyboard Controls (Gesture Control Window):
- **Q**: Quit gesture control
- **R**: Reset volume to current system level
- **D**: Toggle debug information display
- **C/S/L**: Calibration mode (advanced users)

## Troubleshooting

### Camera Issues
```bash
# Check if camera is detected
python -c "import cv2; print('Camera 0:', cv2.VideoCapture(0).isOpened())"
```

### Missing Dependencies
```bash
# Install missing packages
pip install opencv-python mediapipe numpy

# On macOS, you might need:
brew install python-tk
```

### Permission Issues (macOS)
- Go to System Preferences → Security & Privacy → Privacy → Camera
- Allow Python/Terminal to access the camera

### Volume Control Not Working
- **Windows**: Install `pip install pycaw comtypes`
- **macOS**: Should work out of the box
- **Linux**: Ensure `amixer` is installed: `sudo apt install alsa-utils`

## Performance Tips

### For Better Performance:
1. **Close other camera applications** (Zoom, Skype, etc.)
2. **Good lighting** improves hand tracking accuracy
3. **Position hand 1-2 feet from camera** for best detection
4. **Single hand use** - algorithm tracks one hand for better performance

### System Requirements:
- **Camera**: Any USB or built-in camera
- **Python**: 3.8 or newer
- **RAM**: 4GB minimum (8GB recommended)
- **CPU**: Modern dual-core processor

## File Structure

```
Chess/
├── main.py                 # Main chess game with integrated gesture control
├── gesture_control.py      # Standalone gesture control module
├── launcher.py            # Launcher script for both components
├── requirements.txt       # Python dependencies
├── models.py             # Chess game logic
├── ui.py                 # User interface
├── ai.py                 # Chess AI
├── constants.py          # Game constants
├── utils.py              # Utility functions
├── animations.py         # Game animations
└── Images/               # Chess piece images
    ├── Black Pieces/
    └── White Pieces/
```

## How It Works

### Hand Tracking Technology:
1. **MediaPipe**: Google's hand tracking solution detects 21 hand landmarks
2. **OpenCV**: Processes camera feed and displays visual feedback
3. **Distance Calculation**: Measures pixel distance between thumb tip and index finger tip
4. **Volume Mapping**: Maps finger distance to system volume (0-100%)
5. **Smoothing**: Applies smoothing algorithm to prevent jittery volume changes

### Threading Architecture:
- **Main Thread**: Runs the chess game (pygame)
- **Background Thread**: Runs gesture control (OpenCV + MediaPipe)
- **Thread Communication**: Safe cleanup and coordination between threads

### Cross-Platform Audio:
- **Windows**: Uses `pycaw` library for direct audio API access
- **macOS**: Uses AppleScript commands via `osascript`
- **Linux**: Uses ALSA `amixer` commands

## Customization

### Gesture Sensitivity:
Edit `gesture_control.py`:
```python
self.closest_distance = 30     # Minimum distance (volume 0%)
self.farthest_distance = 200   # Maximum distance (volume 100%)
self.smoothing_factor = 0.2    # Volume change speed
```

### Camera Settings:
```python
self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 480)   # Resolution
self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
self.camera.set(cv2.CAP_PROP_FPS, 30)           # Frame rate
```

## Contributing

Feel free to contribute improvements:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Feel free to use, modify, and distribute.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Ensure all dependencies are properly installed
3. Verify camera permissions and functionality
4. Check that your system audio controls are working normally