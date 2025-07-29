import pygame
import sys
import threading
from pygame.locals import *

from constants import FPS
from models import ChessGame # Ensure ChessGame.copy() is implemented here
from ui import draw_board, draw_sidebar, draw_score_screen
from utils import setup_window, create_piece_surfaces, initialize_sounds
from ai import ChessAI

def draw_mode_selection(window, font):
    """Draw a clean and elegant game mode selection screen"""
    window.fill((28, 32, 44))

    # Gradient background
    for y in range(window.get_height()):
        alpha = y / window.get_height()
        color = (
            int(28 + (42 - 28) * alpha),
            int(32 + (48 - 32) * alpha),
            int(44 + (68 - 44) * alpha)
        )
        pygame.draw.line(window, color, (0, y), (window.get_width(), y))

    # Fonts
    title_font = pygame.font.SysFont("segoeui", 56, bold=True)
    button_font = pygame.font.SysFont("segoeui", 32, bold=True)

    # Title
    title_text = "Chess Masters"
    title_surface = title_font.render(title_text, True, (245, 245, 245))
    title_x = window.get_width() // 2 - title_surface.get_width() // 2
    window.blit(title_surface, (title_x, 60))

    # Button setup
    btn_width, btn_height = 360, 85
    center_x = window.get_width() // 2
    btn_classic = pygame.Rect(center_x - btn_width // 2, 200, btn_width, btn_height)
    btn_ai = pygame.Rect(center_x - btn_width // 2, 320, btn_width, btn_height)
    mouse_pos = pygame.mouse.get_pos()

    def draw_button(rect, color, text, icon_char):
        is_hover = rect.collidepoint(mouse_pos)
        base_color = tuple(min(255, c + 30) if is_hover else c for c in color)

        # Shadow
        shadow_rect = rect.move(0, 4)
        shadow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 60), shadow_surf.get_rect(), border_radius=14)
        window.blit(shadow_surf, shadow_rect)

        # Button background
        pygame.draw.rect(window, base_color, rect, border_radius=14)
        pygame.draw.rect(window, (255, 255, 255), rect, width=2, border_radius=14)

        # Icon + text
        icon_font = pygame.font.SysFont("segoeui", 36)
        icon_surface = icon_font.render(icon_char, True, (255, 255, 255))
        text_surface = button_font.render(text, True, (255, 255, 255))

        icon_x = rect.x + 25
        icon_y = rect.centery - icon_surface.get_height() // 2
        text_x = icon_x + icon_surface.get_width() + 20
        text_y = rect.centery - text_surface.get_height() // 2

        window.blit(icon_surface, (icon_x, icon_y))
        window.blit(text_surface, (text_x, text_y))

    # Draw buttons
    draw_button(btn_classic, (65, 105, 225), "Classic Duel", "♔")
    draw_button(btn_ai, (34, 139, 34), "AI Opponent", "🤖")

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
    
    # Set up the window
    window = setup_window()
    clock = pygame.time.Clock()
    
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
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                if game and hasattr(game, 'close_engine'):
                    game.close_engine()
                running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_r:
                    # Reset game and stop any ongoing AI thinking
                    game.reset_game()
                    show_score_screen = False
                    ai_thinking = False
                    if ai_thread and ai_thread.is_alive():
                        # In a more advanced AI, you might add a way to signal
                        # the thread to stop calculation early (e.g., via a shared flag).
                        # For now, we just let it finish or clear the reference.
                        ai_thread = None 
                if event.key == K_s:
                    show_score_screen = not show_score_screen
                if event.key == K_u:
                    # Undo move and stop any ongoing AI thinking
                    if game.undo_move():
                        game.play_sound("move")
                        ai_thinking = False
                        if ai_thread and ai_thread.is_alive():
                            # Same as reset, a stop flag for AI would be ideal.
                            ai_thread = None
                        # If in AI mode and it's now human's turn, undo one more move
                        if game_mode == "AI" and game.turn == 'b': # 'b' for black (AI)
                            game.undo_move()
            
            # Handle mouse clicks for human player
            if event.type == MOUSEBUTTONDOWN and not show_score_screen and not ai_thinking:
                if event.button == 1:  # Left click
                    x, y = event.pos
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
            draw_score_screen(window, game, pieces)
        else:
            draw_sidebar(window, game, pieces)
            
        # Show AI thinking indicator if AI is active
        if ai_thinking:
            thinking_font = pygame.font.SysFont("segoeui", 24, bold=True)
            # You can make this text more dynamic, e.g., "AI thinking..." then "AI thinking.." etc.
            thinking_text = thinking_font.render("AI is thinking...", True, (255, 255, 0)) # Yellow text
            # Position this text appropriately, perhaps in the sidebar area
            window.blit(thinking_text, (650, 100)) # Adjust coordinates as needed for your UI
        
        # Update display
        pygame.display.update()
        clock.tick(FPS)

    # Ensure engine (if any) is closed gracefully when exiting the application
    if game and hasattr(game, 'close_engine'):
        game.close_engine()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()