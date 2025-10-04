import pygame
import os
import time
from constants import SQUARE_SIZE, WHITE, BLACK

# Font setup with fallbacks
def get_font(size, bold=False):
    try:
        # Try to use a modern, digital-looking font
        return pygame.font.Font("fonts/Orbitron-Regular.ttf" if not bold else "fonts/Orbitron-Bold.ttf", size)
    except:
        try:
            # Fall back to a sans-serif system font
            return pygame.font.SysFont("Arial", size, bold=bold)
        except:
            # Last resort
            return pygame.font.Font(None, size)

# Initialize sound system
def initialize_sounds():
    from constants import SOUNDS
    
    try:
        os.makedirs("sounds", exist_ok=True)
        # Initialize sound files here if they exist
        # Example:
        # SOUNDS["move"] = pygame.mixer.Sound("sounds/move.wav")
        # SOUNDS["capture"] = pygame.mixer.Sound("sounds/capture.wav")
        # SOUNDS["check"] = pygame.mixer.Sound("sounds/check.wav")
        # SOUNDS["checkmate"] = pygame.mixer.Sound("sounds/checkmate.wav")
    except:
        pass  # No sound support
    
    return SOUNDS

# Create piece images, loading both black and white pieces from image files
def create_piece_surfaces():
    pieces = {}
    
    # Define piece mappings
    piece_types = {'p': 'pawn', 'r': 'rook', 'n': 'knight', 'b': 'bishop', 'q': 'queen', 'k': 'king'}
    
    # Load black pieces from image files
    for piece_code, piece_name in piece_types.items():
        try:
            # Construct path to the black piece image
            image_path = os.path.join("Images", "Black Pieces", f"{piece_name}.png")
            
            # Load and scale the image
            image = pygame.image.load(image_path)
            # Prefer per-pixel alpha so transparency is preserved
            try:
                image = image.convert_alpha()
            except Exception:
                image = image.convert()

            # Smooth scale to desired square size (preserves alpha if present)
            try:
                image = pygame.transform.smoothscale(image, (SQUARE_SIZE, SQUARE_SIZE))
            except Exception:
                image = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))

            # If the image has no alpha channel, try to treat the top-left pixel as transparent
            if image.get_flags() & pygame.SRCALPHA == 0:
                try:
                    bg_color = image.get_at((0, 0))
                    image.set_colorkey(bg_color)
                except Exception:
                    pass
            
            # Store in the pieces dictionary with the proper code
            pieces['b' + piece_code] = image
            
            print(f"Loaded black {piece_name} from {image_path}")
        except Exception as e:
            print(f"Failed to load black {piece_name}: {e}")
            # Fall back to generated piece if image loading fails
            pieces['b' + piece_code] = create_fallback_piece('b', piece_code)
    
    # Load white pieces from image files
    for piece_code, piece_name in piece_types.items():
        try:
            # Construct path to the white piece image
            image_path = os.path.join("Images", "White Pieces", f"{piece_name}(1).png")
            
            # Load and scale the image
            image = pygame.image.load(image_path)
            # Prefer per-pixel alpha so transparency is preserved
            try:
                image = image.convert_alpha()
            except Exception:
                image = image.convert()

            # Smooth scale to desired square size (preserves alpha if present)
            try:
                image = pygame.transform.smoothscale(image, (SQUARE_SIZE, SQUARE_SIZE))
            except Exception:
                image = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))

            # If the image has no alpha channel, try to treat the top-left pixel as transparent
            if image.get_flags() & pygame.SRCALPHA == 0:
                try:
                    bg_color = image.get_at((0, 0))
                    image.set_colorkey(bg_color)
                except Exception:
                    pass
            
            # Store in the pieces dictionary with the proper code
            pieces['w' + piece_code] = image
            
            print(f"Loaded white {piece_name} from {image_path}")
        except Exception as e:
            print(f"Failed to load white {piece_name}: {e}")
            # Fall back to generated piece if image loading fails
            pieces['w' + piece_code] = create_fallback_piece('w', piece_code)
    
    return pieces

# Helper function to create fallback pieces if image loading fails
def create_fallback_piece(color, piece_type):
    piece_symbols = {
        'p': '♟' if color == 'b' else '♙',
        'r': '♜' if color == 'b' else '♖',
        'n': '♞' if color == 'b' else '♘',
        'b': '♝' if color == 'b' else '♗',
        'q': '♛' if color == 'b' else '♕',
        'k': '♚' if color == 'b' else '♔'
    }
    
    symbol = piece_symbols.get(piece_type, '?')
    
    if color == 'w':
        color_val = WHITE
        base_color = (230, 230, 230)
        highlight_color = (255, 255, 255)
        shadow_color = (180, 180, 180)
    else:
        color_val = BLACK
        base_color = (50, 50, 50)
        highlight_color = (80, 80, 80)
        shadow_color = (20, 20, 20)
    
    # Create a surface with gradient for 3D effect
    surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
    
    # Create base circle with gradient
    radius = SQUARE_SIZE // 2 - 8
    center = (SQUARE_SIZE // 2, SQUARE_SIZE // 2)
    
    # Draw multiple circles with decreasing radius and varying colors for gradient
    for i in range(radius, 0, -2):
        factor = i / radius
        r = int(base_color[0] * factor + highlight_color[0] * (1 - factor))
        g = int(base_color[1] * factor + highlight_color[1] * (1 - factor))
        b = int(base_color[2] * factor + highlight_color[2] * (1 - factor))
        
        pygame.draw.circle(surface, (r, g, b), center, i)
    
    # Add a reflection highlight
    highlight_pos = (center[0] - radius//3, center[1] - radius//3)
    highlight_radius = radius // 3
    for i in range(highlight_radius, 0, -1):
        factor = i / highlight_radius
        alpha = int(150 * factor)
        highlight_surface = pygame.Surface((i*2, i*2), pygame.SRCALPHA)
        highlight_surface.fill((255, 255, 255, alpha))
        surface.blit(highlight_surface, (highlight_pos[0] - i, highlight_pos[1] - i))
    
    # Add symbol with shadow effect
    font_size = int(SQUARE_SIZE * 0.6)
    try:
        font = pygame.font.SysFont('Arial', font_size, bold=True)
    except:
        font = pygame.font.Font(None, font_size)
    
    # Shadow text (offset)
    shadow = font.render(symbol, True, shadow_color)
    shadow_rect = shadow.get_rect(center=(center[0] + 2, center[1] + 2))
    surface.blit(shadow, shadow_rect)
    
    # Main text
    text = font.render(symbol, True, color_val)
    text_rect = text.get_rect(center=center)
    surface.blit(text, text_rect)
    
    return surface

def setup_window():
    """Initialize the game window with icon"""
    from constants import WINDOW_WIDTH, WINDOW_HEIGHT, DARK_SQUARE, LIGHT_SQUARE, BLACK
    
    # Create resizable window
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Advanced Chess with AI")
    
    # Try to set an icon
    try:
        icon = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(icon, DARK_SQUARE, (0, 0, 16, 16))
        pygame.draw.rect(icon, DARK_SQUARE, (16, 16, 16, 16))
        pygame.draw.rect(icon, LIGHT_SQUARE, (16, 0, 16, 16))
        pygame.draw.rect(icon, LIGHT_SQUARE, (0, 16, 16, 16))
        # Draw a knight silhouette
        pygame.draw.polygon(icon, BLACK, [(8, 8), (24, 8), (24, 12), (20, 20), (12, 20), (8, 12)])
        pygame.display.set_icon(icon)
    except:
        pass  # Skip if setting icon fails
    
    return window

# AI-related utility functions
def format_move_for_display(move):
    """Convert a move tuple to readable chess notation"""
    if not move:
        return "No move"
    
    from_pos, to_pos = move
    from_col = chr(ord('a') + from_pos[1])
    from_row = str(8 - from_pos[0])
    to_col = chr(ord('a') + to_pos[1])
    to_row = str(8 - to_pos[0])
    
    return f"{from_col}{from_row} → {to_col}{to_row}"

def get_difficulty_color(difficulty):
    """Get color scheme for difficulty levels"""
    colors = {
        'Easy': {
            'bg': (34, 139, 34),      # Forest Green
            'hover': (50, 205, 50),   # Lime Green
            'text': WHITE
        },
        'Medium': {
            'bg': (255, 140, 0),      # Orange
            'hover': (255, 165, 0),   # Orange Red
            'text': WHITE
        },
        'Hard': {
            'bg': (220, 20, 20),      # Crimson
            'hover': (255, 69, 69),   # Red
            'text': WHITE
        },
        'Classic': {
            'bg': (70, 130, 180),     # Steel Blue
            'hover': (100, 149, 237), # Cornflower Blue
            'text': WHITE
        }
    }
    return colors.get(difficulty, colors['Classic'])

def create_gradient_surface(width, height, color1, color2, vertical=True):
    """Create a gradient surface between two colors"""
    surface = pygame.Surface((width, height))
    
    if vertical:
        for y in range(height):
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))
    else:
        for x in range(width):
            ratio = x / width
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), (x, 0), (x, height))
    
    return surface

def draw_thinking_animation(surface, rect, progress):
    """Draw an animated thinking indicator for AI"""
    from constants import WHITE, BLACK
    
    # Clear the area
    pygame.draw.rect(surface, (240, 240, 240), rect)
    pygame.draw.rect(surface, BLACK, rect, 2)
    
    # Draw dots with pulsing animation
    dot_count = 3
    dot_radius = 6
    spacing = 20
    
    center_x = rect.centerx
    center_y = rect.centery
    
    start_x = center_x - (dot_count - 1) * spacing // 2
    
    for i in range(dot_count):
        x = start_x + i * spacing
        
        # Create pulsing effect
        phase = (progress + i * 0.3) % 1.0
        alpha = int(100 + 155 * abs(0.5 - phase) * 2)
        radius = dot_radius + int(2 * abs(0.5 - phase) * 2)
        
        # Draw dot with alpha
        dot_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(dot_surface, (*BLACK, alpha), (radius, radius), radius)
        surface.blit(dot_surface, (x - radius, center_y - radius))

def play_sound(sound_name):
    """Play a sound effect if available"""
    from constants import SOUNDS
    
    try:
        if sound_name in SOUNDS and SOUNDS[sound_name]:
            SOUNDS[sound_name].play()
    except:
        pass  # Ignore sound errors

def create_button_surface(width, height, text, font, colors, is_hovered=False):
    """Create a styled button surface with gradient and effects"""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Choose colors based on hover state
    bg_color = colors['hover'] if is_hovered else colors['bg']
    text_color = colors['text']
    
    # Create gradient background
    gradient = create_gradient_surface(width, height, bg_color, 
                                     tuple(max(0, c - 30) for c in bg_color))
    surface.blit(gradient, (0, 0))
    
    # Add border
    border_color = tuple(min(255, c + 50) for c in bg_color)
    pygame.draw.rect(surface, border_color, (0, 0, width, height), 3)
    
    # Add subtle inner shadow
    shadow_color = tuple(max(0, c - 40) for c in bg_color)
    pygame.draw.rect(surface, shadow_color, (2, 2, width - 4, height - 4), 1)
    
    # Render text with shadow
    text_surface = font.render(text, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(width // 2 + 1, height // 2 + 1))
    surface.blit(text_surface, text_rect)
    
    # Render main text
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(width // 2, height // 2))
    surface.blit(text_surface, text_rect)
    
    return surface

def get_piece_value(piece_type):
    """Get the standard point value of a piece"""
    values = {
        'p': 100,    # Pawn
        'n': 320,    # Knight
        'b': 330,    # Bishop
        'r': 500,    # Rook
        'q': 900,    # Queen
        'k': 20000   # King
    }
    return values.get(piece_type.lower(), 0)

def position_to_algebraic(row, col):
    """Convert board position to algebraic notation (e.g., (0,0) -> 'a8')"""
    return chr(ord('a') + col) + str(8 - row)

def algebraic_to_position(algebraic):
    """Convert algebraic notation to board position (e.g., 'a8' -> (0,0))"""
    if len(algebraic) != 2:
        return None
    
    col = ord(algebraic[0].lower()) - ord('a')
    row = 8 - int(algebraic[1])
    
    if 0 <= row < 8 and 0 <= col < 8:
        return (row, col)
    return None

class Timer:
    """Simple timer utility for measuring AI thinking time"""
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        self.start_time = time.time()
        self.end_time = None
    
    def stop(self):
        if self.start_time:
            self.end_time = time.time()
            return self.get_elapsed()
        return 0
    
    def get_elapsed(self):
        if self.start_time:
            end = self.end_time or time.time()
            return end - self.start_time
        return 0
    
    def format_time(self):
        elapsed = self.get_elapsed()
        if elapsed < 1:
            return f"{elapsed*1000:.0f}ms"
        else:
            return f"{elapsed:.1f}s"

def create_status_text(text, font, color=None):
    """Create formatted status text surface"""
    if color is None:
        color = BLACK
    
    # Create text with slight shadow for better readability
    shadow = font.render(text, True, (128, 128, 128))
    main_text = font.render(text, True, color)
    
    # Create surface large enough for both
    width = max(shadow.get_width(), main_text.get_width()) + 2
    height = max(shadow.get_height(), main_text.get_height()) + 2
    
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Blit shadow first (offset by 1 pixel)
    surface.blit(shadow, (1, 1))
    # Blit main text
    surface.blit(main_text, (0, 0))
    
    return surface