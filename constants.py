import pygame

# Constants
BOARD_SIZE = 8
SQUARE_SIZE = 80
WIDTH = HEIGHT = BOARD_SIZE * SQUARE_SIZE
WINDOW_WIDTH = WIDTH + 350  # Extra space for sideboard
WINDOW_HEIGHT = HEIGHT
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT = (100, 249, 83, 150)  # Transparent green
LIGHT_HIGHLIGHT = (124, 252, 0, 150)  # Light green for highlighting moves
TEXT_COLOR = (25, 25, 25)
SCORE_BG = (20, 30, 40)
PANEL_BG = (40, 44, 52)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
BLUE_ACCENT = (66, 139, 202)
RED_ACCENT = (217, 83, 79)
GREEN_ACCENT = (92, 184, 92)
MOVE_INDICATOR = (255, 255, 0, 120)  # Yellow with transparency
DARK_OVERLAY = (0, 0, 0, 180)  # Semi-transparent black

# Sound effects
SOUNDS = {
    "move": None,
    "capture": None,
    "check": None,
    "promote": None,
    "castle": None,
    "game_start": None,
    "game_end": None,
    "select": None,
    "invalid": None
}