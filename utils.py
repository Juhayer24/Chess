import pygame
import os
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
            image = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
            
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
            image = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
            
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
    
    # Create window
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Advanced Chess")
    
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