try:
    import pygame
except ModuleNotFoundError:
    print("Error: pygame is not installed. Please install required packages with: \n\n    python3 -m venv .venv\n    source .venv/bin/activate\n    pip install -r requirements.txt\n\nThen run: python3 main.py")
    raise

import sys
import threading
import socket
import select
import math
from pygame.locals import *

from constants import FPS, WIDTH
from models import ChessGame # Ensure ChessGame.copy() is implemented here
from ui import draw_board, draw_sidebar, draw_score_screen
from utils import setup_window, create_piece_surfaces, initialize_sounds
from ai import ChessAI

def draw_mode_selection(window, font):
    """Draw a sophisticated and modern game mode selection screen"""
    # Rich dark background with subtle pattern
    window.fill((15, 23, 42))  # Deep navy blue
    
    # Create a subtle geometric pattern background
    pattern_color = (25, 35, 55)
    for x in range(0, window.get_width(), 60):
        for y in range(0, window.get_height(), 60):
            if (x // 60 + y // 60) % 2 == 0:
                pygame.draw.rect(window, pattern_color, (x, y, 30, 30))
    
    # Animated gradient overlay
    time_offset = pygame.time.get_ticks() * 0.001
    for y in range(window.get_height()):
        alpha = 0.3 + 0.1 * math.sin(time_offset + y * 0.01)
        gradient_intensity = y / window.get_height()
        color = (
            int(15 + (35 - 15) * gradient_intensity * alpha),
            int(23 + (45 - 23) * gradient_intensity * alpha), 
            int(42 + (75 - 42) * gradient_intensity * alpha)
        )
        pygame.draw.line(window, color, (0, y), (window.get_width(), y))
    
    # Elegant typography
    title_font = pygame.font.SysFont("georgia", 72, bold=True)  # Serif font for elegance
    subtitle_font = pygame.font.SysFont("segoeui", 24)
    button_font = pygame.font.SysFont("segoeui", 28, bold=True)
    
    # Main title with shadow effect
    title_text = "Chess Game"
    title_shadow = title_font.render(title_text, True, (0, 0, 0))
    title_surface = title_font.render(title_text, True, (220, 220, 235))
    
    title_x = window.get_width() // 2 - title_surface.get_width() // 2
    window.blit(title_shadow, (title_x + 3, 63))  # Shadow offset
    window.blit(title_surface, (title_x, 60))
    
    # Elegant subtitle
    subtitle_text = "Choose Your Battle"
    subtitle_surface = subtitle_font.render(subtitle_text, True, (160, 170, 190))
    subtitle_x = window.get_width() // 2 - subtitle_surface.get_width() // 2
    window.blit(subtitle_surface, (subtitle_x, 140))
    
    # Decorative line under title
    line_width = 200
    line_x = window.get_width() // 2 - line_width // 2
    pygame.draw.rect(window, (100, 120, 150), (line_x, 170, line_width, 2))
    
    # Modern button design
    btn_width, btn_height = 380, 90
    center_x = window.get_width() // 2
    spacing = 40
    
    btn_classic = pygame.Rect(center_x - btn_width // 2, 220, btn_width, btn_height)
    btn_ai = pygame.Rect(center_x - btn_width // 2, 220 + btn_height + spacing, btn_width, btn_height)
    mouse_pos = pygame.mouse.get_pos()

    def draw_modern_button(rect, primary_color, secondary_color, text, description):
        is_hover = rect.collidepoint(mouse_pos)
        
        # Hover animation effect
        hover_scale = 1.05 if is_hover else 1.0
        hover_offset = -2 if is_hover else 0
        
        # Calculate scaled rect
        scaled_width = int(rect.width * hover_scale)
        scaled_height = int(rect.height * hover_scale)
        scaled_x = rect.centerx - scaled_width // 2
        scaled_y = rect.centery - scaled_height // 2 + hover_offset
        scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
        
        # Drop shadow (more prominent on hover)
        shadow_offset = 8 if is_hover else 5
        shadow_alpha = 80 if is_hover else 50
        shadow_rect = scaled_rect.move(shadow_offset, shadow_offset)
        shadow_surf = pygame.Surface((scaled_rect.width, scaled_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, shadow_alpha), shadow_surf.get_rect(), border_radius=15)
        window.blit(shadow_surf, shadow_rect)
        
        # Gradient background
        for i in range(scaled_rect.height):
            gradient_ratio = i / scaled_rect.height
            color = (
                int(primary_color[0] * (1 - gradient_ratio) + secondary_color[0] * gradient_ratio),
                int(primary_color[1] * (1 - gradient_ratio) + secondary_color[1] * gradient_ratio),
                int(primary_color[2] * (1 - gradient_ratio) + secondary_color[2] * gradient_ratio)
            )
            pygame.draw.line(window, color, 
                           (scaled_rect.x, scaled_rect.y + i), 
                           (scaled_rect.right, scaled_rect.y + i))
        
        # Border with glow effect
        border_color = (255, 255, 255, 150) if is_hover else (200, 200, 200, 100)
        pygame.draw.rect(window, border_color[:3], scaled_rect, width=2, border_radius=15)
        
        # Inner highlight
        highlight_rect = pygame.Rect(scaled_rect.x + 2, scaled_rect.y + 2, 
                                   scaled_rect.width - 4, scaled_rect.height // 3)
        highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surf, (255, 255, 255, 30), highlight_surf.get_rect(), border_radius=12)
        window.blit(highlight_surf, highlight_rect)
        
        # Button text
        text_surface = button_font.render(text, True, (255, 255, 255))
        text_x = scaled_rect.centerx - text_surface.get_width() // 2
        text_y = scaled_rect.centery - text_surface.get_height() // 2 - 8
        
        # Text shadow
        text_shadow = button_font.render(text, True, (0, 0, 0))
        window.blit(text_shadow, (text_x + 1, text_y + 1))
        window.blit(text_surface, (text_x, text_y))
        
        # Description text
        desc_font = pygame.font.SysFont("segoeui", 16)
        desc_surface = desc_font.render(description, True, (200, 210, 220))
        desc_x = scaled_rect.centerx - desc_surface.get_width() // 2
        desc_y = text_y + text_surface.get_height() + 5
        window.blit(desc_surface, (desc_x, desc_y))
    
    # Draw buttons with sophisticated styling
    draw_modern_button(btn_classic, (45, 85, 155), (25, 65, 135), 
                      "Player vs Player", "Challenge a friend in classic chess")
    
    draw_modern_button(btn_ai, (155, 85, 45), (135, 65, 25), 
                      "Player vs Computer", "Test your skills against AI")
    
    # Decorative chess piece images in corners with gentle animation
    piece_images = []
    piece_files = [
        "Images/Black Pieces/queen.png",      # Top-left: Black Queen
        "Images/White Pieces/King(1).png",    # Top-right: White King
        "Images/Black Pieces/king.png",       # Bottom-left: Black King
        "Images/White Pieces/Queen(1).png"    # Bottom-right: White Queen
    ]
    
    # Load and scale the piece images
    for piece_file in piece_files:
        try:
            piece_img = pygame.image.load(piece_file)
            # Scale down for corner decoration (80x80 pixels)
            piece_img = pygame.transform.smoothscale(piece_img, (80, 80))
            # Convert with alpha to preserve transparency
            piece_img = piece_img.convert_alpha()
            piece_images.append(piece_img)
        except Exception as e:
            print(f"Could not load piece image {piece_file}: {e}")
            # Fallback to None, will use text pieces
            piece_images.append(None)
    
    positions = [(50, 50), (window.get_width() - 130, 50), 
                (50, window.get_height() - 130), (window.get_width() - 130, window.get_height() - 130)]
    
    # Gentle floating animation for pieces
    float_offset = math.sin(time_offset * 2) * 3
    
    for i, (piece_img, pos) in enumerate(zip(piece_images, positions)):
        # Each piece has a slightly different animation phase
        individual_offset = math.sin(time_offset * 2 + i * 0.5) * 2
        animated_y = pos[1] + individual_offset
        
        if piece_img is not None:
            # Create a subtle glow effect for the image
            glow_surf = pygame.Surface((piece_img.get_width() + 10, piece_img.get_height() + 10), pygame.SRCALPHA)
            glow_color = (100, 120, 160, 30)  # Subtle blue glow with transparency
            pygame.draw.ellipse(glow_surf, glow_color, glow_surf.get_rect())
            
            # Draw glow first (slightly offset)
            window.blit(glow_surf, (pos[0] - 5, animated_y - 5))
            
            # Draw the actual piece image
            window.blit(piece_img, (pos[0], animated_y))
        else:
            # Fallback to text pieces if image loading failed
            piece_font = pygame.font.SysFont("segoeui", 48)
            fallback_pieces = ["♛", "♔", "♚", "♕"]
            piece_char = fallback_pieces[i]
            
            # Create a subtle glow effect
            piece_glow = piece_font.render(piece_char, True, (100, 120, 160))
            piece_surface = piece_font.render(piece_char, True, (60, 80, 120))
            
            # Draw glow (slightly larger and offset)
            window.blit(piece_glow, (pos[0] - 1, animated_y - 1))
            window.blit(piece_surface, (pos[0], animated_y))
    
    # Add subtle animated sparkles around the title
    sparkle_count = 8
    for i in range(sparkle_count):
        angle = (time_offset + i * (2 * math.pi / sparkle_count)) % (2 * math.pi)
        radius = 150 + 20 * math.sin(time_offset * 3 + i)
        sparkle_x = title_x + title_surface.get_width() // 2 + radius * math.cos(angle)
        sparkle_y = 80 + radius * 0.3 * math.sin(angle)
        
        # Only draw sparkles that are within reasonable bounds
        if 0 < sparkle_x < window.get_width() and 0 < sparkle_y < window.get_height():
            sparkle_size = int(2 + math.sin(time_offset * 4 + i) * 1)
            sparkle_alpha = int(100 + 50 * math.sin(time_offset * 2 + i))
            sparkle_color = (200, 220, 255, min(255, max(0, sparkle_alpha)))
            
            sparkle_surf = pygame.Surface((sparkle_size * 2, sparkle_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(sparkle_surf, sparkle_color[:3], (sparkle_size, sparkle_size), sparkle_size)
            window.blit(sparkle_surf, (sparkle_x - sparkle_size, sparkle_y - sparkle_size))
    
    # Subtle footer
    footer_font = pygame.font.SysFont("segoeui", 14)
    footer_text = "Use ESC to quit • Classic chess rules apply"
    footer_surface = footer_font.render(footer_text, True, (80, 90, 110))
    footer_x = window.get_width() // 2 - footer_surface.get_width() // 2
    window.blit(footer_surface, (footer_x, window.get_height() - 40))

    pygame.display.update()
    return btn_classic, btn_ai


# NEW: Function to be run in a separate thread for AI move calculation.
# This function will post an event back to the main thread when done.
def ai_move_thread(ai_player, game_copy, ai_move_event):
    """
    Calculates the AI's best move on a copy of the game state
    and posts an event to the main thread when done.
    """
    # The AI now works on game_copy, NOT the original 'game' object
    ai_move = ai_player.get_best_move(game_copy)
    ai_move_event.post(pygame.event.Event(pygame.USEREVENT + 1, {"ai_move": ai_move}))


def main():
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()
    
    # Try to initialize gesture control (optional)
    gesture_controller = None
    try:
        from gesture_control import HandGestureVolumeControl
        # Enable UDP sending from gesture process so it can talk to this game
        gesture_controller = HandGestureVolumeControl(window_name="Volume Control (Chess)", udp_enabled=True, udp_host="127.0.0.1", udp_port=5006)
        
        if gesture_controller.is_available():
            # Start gesture control in background thread
            if gesture_controller.start_threaded():
                print("✓ Hand gesture volume control started")
                print("  Use thumb and index finger pinch gestures to control volume")
            else:
                print("⚠ Could not start gesture control")
                gesture_controller = None
        else:
            print("⚠ Gesture control unavailable - no camera detected")
            gesture_controller = None
    except ImportError:
        print("ℹ Gesture control not available - install opencv-python and mediapipe to enable")
        gesture_controller = None
    except Exception as e:
        print(f"⚠ Gesture control initialization failed: {e}")
        gesture_controller = None

    # --- UDP listener for gesture commands ---
    GESTURE_UDP_PORT = 5006
    GESTURE_EVENT = pygame.USEREVENT + 2

    def udp_listener(stop_event):
        """Listen for UDP gesture commands and post pygame events."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(False)
        try:
            sock.bind(("127.0.0.1", GESTURE_UDP_PORT))
        except Exception as e:
            print(f"Failed to bind gesture UDP socket: {e}")
            return

        while not stop_event.is_set():
            # Use select to poll the socket without blocking
            rlist, _, _ = select.select([sock], [], [], 0.05)
            if sock in rlist:
                try:
                    data, addr = sock.recvfrom(1024)
                    cmd = data.decode('utf-8').strip()
                    # Post a pygame event with the gesture command
                    pygame.event.post(pygame.event.Event(GESTURE_EVENT, {"cmd": cmd}))
                    # Send ACK back to the sender
                    try:
                        sock.sendto(f"ACK:{cmd}".encode('utf-8'), addr)
                    except Exception:
                        pass
                except Exception:
                    continue

    udp_stop = threading.Event()
    udp_thread = threading.Thread(target=udp_listener, args=(udp_stop,), daemon=True)
    udp_thread.start()
    
    # Set up the window
    window = setup_window()
    clock = pygame.time.Clock()
    
    # Track current window dimensions
    current_window_width = window.get_width()
    current_window_height = window.get_height()
    
    # Initialize sounds
    sounds = initialize_sounds()
    
    # Create piece images
    pieces = create_piece_surfaces()
    
    # Game state variables
    show_score_screen = False
    game = None
    game_mode = None
    ai_player = None
    ai_depth = 3
    font = pygame.font.SysFont("segoeui", 36, bold=True)
    
    # Custom event for AI move completion
    AI_MOVE_COMPLETE = pygame.USEREVENT + 1 # Define this custom event ID
    
    # --- Game mode selection screen ---
    # Game mode selection
    selecting_mode = True
    while selecting_mode:
        btn_classic, btn_ai = draw_mode_selection(window, font)
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if btn_classic.collidepoint(event.pos):
                    game_mode = "2V2"
                    ai_player = None
                    selecting_mode = False
                elif btn_ai.collidepoint(event.pos):
                    game_mode = "AI"
                    ai_depth = 2  # Fixed AI depth for "AI Opponent"
                    ai_player = ChessAI(depth=ai_depth)
                    selecting_mode = False
        clock.tick(60)
    
    # Initialize game state with selected mode
    game = ChessGame(sounds, game_mode=game_mode)
    
    # Main game loop
    running = True
    ai_thinking = False
    ai_thread = None # Reference to the AI thread
    button_rects = {}  # Store button rectangles for click detection
    stats_return_button = None  # Store stats return button rectangle
    
    while running:
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                if game and hasattr(game, 'close_engine'):
                    game.close_engine()
                running = False
            if event.type == VIDEORESIZE:
                # Handle window resize
                from constants import MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT
                new_width = max(event.w, MIN_WINDOW_WIDTH)
                new_height = max(event.h, MIN_WINDOW_HEIGHT)
                window = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
                current_window_width = new_width
                current_window_height = new_height
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_s:
                    show_score_screen = not show_score_screen

            # Handle gesture UDP events
            if event.type == GESTURE_EVENT and not show_score_screen and not ai_thinking:
                cmd = getattr(event, 'cmd', None)
                if cmd:
                    # Track last gesture for UI feedback
                    try:
                        game.last_gesture_cmd = (cmd, pygame.time.get_ticks())
                    except Exception:
                        pass
                    # Map gesture commands to game actions
                    # Cursor stored on game as gesture_cursor (row, col)
                    if not hasattr(game, 'gesture_cursor') or game.gesture_cursor is None:
                        game.gesture_cursor = (0, 0)

                    row, col = game.gesture_cursor

                    if cmd.startswith('cursor:'):
                        try:
                            rc = cmd.split(':',1)[1]
                            r_s,c_s = rc.split(',')
                            row = max(0, min(7, int(r_s)))
                            col = max(0, min(7, int(c_s)))
                            game.gesture_cursor = (row, col)
                        except Exception:
                            pass
                    elif cmd == 'move_left':
                        col = max(0, col - 1)
                    elif cmd == 'move_right':
                        col = min(7, col + 1)
                    elif cmd == 'move_up':
                        row = max(0, row - 1)
                    elif cmd == 'move_down':
                        row = min(7, row + 1)
                    elif cmd == 'select':
                        # Debounce selects to avoid repeated toggles
                        now_ms = pygame.time.get_ticks()
                        last = getattr(game, 'last_select_ms', 0)
                        if now_ms - last > 300:
                            moved = game.select_piece(row, col)
                            game.last_select_ms = now_ms
                            # If in AI mode and human moved, trigger AI
                            if game_mode == 'AI' and moved and not game.game_over and game.turn == 'b':
                                ai_thinking = True
                                ai_thread = threading.Thread(target=ai_move_thread, args=(ai_player, game.copy(), pygame.event))
                                ai_thread.start()
                    elif cmd == 'confirm':
                        if game.selected_piece:
                            to_row, to_col = row, col
                            game.move_piece(to_row, to_col)
                    elif cmd == 'confirm':
                        # Confirm (drop) - try to move to cursor
                        if game.selected_piece:
                            to_row, to_col = row, col
                            game.move_piece(to_row, to_col)
                    elif cmd == 'cancel':
                        game.selected_piece = None
                        game.valid_moves = []

                    game.gesture_cursor = (row, col)
            
            # Handle mouse clicks for human player and UI buttons
            if event.type == MOUSEBUTTONDOWN and not show_score_screen and not ai_thinking:
                if event.button == 1:  # Left click
                    x, y = event.pos
                    
                    # Check if click is on any UI button
                    if button_rects:
                        if button_rects.get('restart') and button_rects['restart'].collidepoint(x, y):
                            # Restart game
                            game.reset_game()
                            show_score_screen = False
                            ai_thinking = False
                            if ai_thread and ai_thread.is_alive():
                                ai_thread = None
                            continue
                        elif button_rects.get('undo') and button_rects['undo'].collidepoint(x, y):
                            # Undo move
                            game.undo_move()
                            if ai_thread and ai_thread.is_alive():
                                ai_thread = None
                            # If in AI mode and it's now human's turn, undo one more move
                            if game_mode == "AI" and game.turn == 'b': # 'b' for black (AI)
                                game.undo_move()
                            continue
                        elif button_rects.get('stats') and button_rects['stats'].collidepoint(x, y):
                            # Toggle stats screen
                            show_score_screen = not show_score_screen
                            continue
                        elif button_rects.get('quit') and button_rects['quit'].collidepoint(x, y):
                            # Quit game
                            running = False
                            continue
                    
                    # Only process clicks on the board area (assuming 8x8 squares, 80 pixels each)
                    if x < 8 * 80 and y < 8 * 80:  # Adjust based on your BOARD_WIDTH/HEIGHT and SQUARE_SIZE
                        col = x // 80  
                        row = y // 80  
                        moved = game.select_piece(row, col) # This attempts to select a piece or make a move
                        
                        # If in AI mode and human just made a valid move, trigger AI's turn
                        if game_mode == "AI" and moved and not game.game_over and game.turn == 'b':
                            ai_thinking = True
                            # Start AI calculation in a separate thread
                            # Pass a deep copy of the game object to the AI thread
                            ai_thread = threading.Thread(target=ai_move_thread, args=(ai_player, game.copy(), pygame.event))
                            ai_thread.start()
            
            # Handle mouse clicks on stats page
            if event.type == MOUSEBUTTONDOWN and show_score_screen:
                if event.button == 1:  # Left click
                    x, y = event.pos
                    # Check if click is on return button
                    if stats_return_button and stats_return_button.collidepoint(x, y):
                        show_score_screen = False
                        continue
            
            # NEW: Handle the custom event when AI move calculation is complete
            if event.type == AI_MOVE_COMPLETE:
                ai_move = event.ai_move # The calculated move from the AI thread
                if ai_move:
                    from_row, from_col, to_row, to_col = ai_move
                    
                    # Apply the AI's move to the actual game board (game object)
                    # Your game.select_piece and game.move_piece should handle this.
                    # This simulates the human clicking the AI's selected piece, then its destination.
                    game.selected_piece = (from_row, from_col)
                    game.valid_moves = game.get_valid_moves(from_row, from_col) # Recalculate valid moves for visual
                    game.move_piece(to_row, to_col) # This actually executes the move on the main game board
                
                ai_thinking = False # AI is no longer thinking
                ai_thread = None # Clear the thread reference
                
        # Clear screen
        from constants import PANEL_BG # Assuming PANEL_BG is defined in constants
        window.fill(PANEL_BG)
        
        # Draw the game components
        draw_board(window, game, pieces)
        if show_score_screen:
            stats_return_button = draw_score_screen(window, game, pieces, mouse_pos=mouse_pos)
        else:
            button_rects = draw_sidebar(window, game, pieces, mouse_pos=mouse_pos)
        
        # Update display
        pygame.display.update()
        clock.tick(FPS)

    # Ensure engine (if any) is closed gracefully when exiting the application
    if game and hasattr(game, 'close_engine'):
        game.close_engine()
    
    # Clean up gesture control
    if gesture_controller:
        try:
            gesture_controller.stop_threaded()
            gesture_controller.cleanup()
        except Exception as e:
            print(f"Error cleaning up gesture control: {e}")
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()