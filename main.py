import pygame
import sys
from pygame.locals import *

from constants import FPS
from models import ChessGame
from ui import draw_board, draw_sidebar, draw_score_screen
from utils import setup_window, create_piece_surfaces, initialize_sounds
from ai import ChessAI

def draw_mode_selection(window, font):
    """Draw an elegant game mode selection screen"""
    # Dark sophisticated background
    window.fill((28, 32, 44))
    
    # Create gradient background
    for y in range(window.get_height()):
        alpha = y / window.get_height()
        color = (
            int(28 + (42 - 28) * alpha),
            int(32 + (48 - 32) * alpha), 
            int(44 + (68 - 44) * alpha)
        )
        pygame.draw.line(window, color, (0, y), (window.get_width(), y))
    
    # Load or create better fonts
    try:
        # Try to load nicer fonts if available
        title_font = pygame.font.Font(None, 56)
        subtitle_font = pygame.font.Font(None, 24)
        button_font = pygame.font.Font(None, 32)
    except:
        # Fallback to system fonts
        title_font = pygame.font.SysFont("segoeui", 56, bold=True)
        subtitle_font = pygame.font.SysFont("segoeui", 22)
        button_font = pygame.font.SysFont("segoeui", 28, bold=True)
    
    # Title with shadow effect
    title_text = "Chess Masters"
    title_shadow = title_font.render(title_text, True, (0, 0, 0))
    title_main = title_font.render(title_text, True, (245, 245, 245))
    
    title_x = window.get_width() // 2 - title_main.get_width() // 2
    window.blit(title_shadow, (title_x + 3, 63))
    window.blit(title_main, (title_x, 60))
    
    # Subtitle
    subtitle_text = "Choose your battle"
    subtitle = subtitle_font.render(subtitle_text, True, (180, 180, 180))
    subtitle_x = window.get_width() // 2 - subtitle.get_width() // 2
    window.blit(subtitle, (subtitle_x, 120))
    
    # Button dimensions and positions
    btn_width, btn_height = 380, 85
    center_x = window.get_width() // 2
    btn_classic = pygame.Rect(center_x - btn_width // 2, 180, btn_width, btn_height)
    btn_easy = pygame.Rect(center_x - btn_width // 2, 280, btn_width, btn_height)
    btn_medium = pygame.Rect(center_x - btn_width // 2, 380, btn_width, btn_height)
    btn_hard = pygame.Rect(center_x - btn_width // 2, 480, btn_width, btn_height)
    
    mouse_pos = pygame.mouse.get_pos()
    
    def draw_premium_button(rect, primary_color, accent_color, text, description, icon_char):
        """Draw a premium-styled button with hover effects"""
        is_hover = rect.collidepoint(mouse_pos)
        
        # Button shadow
        shadow_rect = rect.move(0, 4)
        shadow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 40), shadow_surf.get_rect(), border_radius=16)
        window.blit(shadow_surf, shadow_rect)
        
        # Button background with gradient
        if is_hover:
            base_color = tuple(min(255, c + 20) for c in primary_color)
        else:
            base_color = primary_color
            
        # Create gradient effect
        for i in range(rect.height):
            progress = i / rect.height
            color = tuple(int(base_color[j] * (1 - progress * 0.15)) for j in range(3))
            pygame.draw.rect(window, color, (rect.x, rect.y + i, rect.width, 1))
        
        # Border with accent color
        pygame.draw.rect(window, accent_color, rect, width=2, border_radius=16)
        
        # Inner highlight
        inner_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height - 4)
        pygame.draw.rect(window, tuple(min(255, c + 30) for c in base_color), 
                        inner_rect, width=1, border_radius=14)
        
        # Icon
        icon_font = pygame.font.SysFont("segoeui", 36)
        icon_surface = icon_font.render(icon_char, True, (255, 255, 255))
        icon_x = rect.x + 30
        icon_y = rect.centery - icon_surface.get_height() // 2
        window.blit(icon_surface, (icon_x, icon_y))
        
        # Main text
        text_surface = button_font.render(text, True, (255, 255, 255))
        text_x = rect.x + 85
        text_y = rect.centery - 15
        window.blit(text_surface, (text_x, text_y))
        
        # Description text
        desc_font = pygame.font.SysFont("segoeui", 18)
        desc_surface = desc_font.render(description, True, (200, 200, 200))
        desc_x = rect.x + 85
        desc_y = rect.centery + 8
        window.blit(desc_surface, (desc_x, desc_y))
        
        # Hover effect - subtle glow
        if is_hover:
            glow_surf = pygame.Surface((rect.width + 8, rect.height + 8), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*accent_color, 30), glow_surf.get_rect(), border_radius=20)
            window.blit(glow_surf, (rect.x - 4, rect.y - 4))
    
    # Draw buttons with premium styling
    draw_premium_button(
        btn_classic,
        primary_color=(65, 105, 225),  # Royal blue
        accent_color=(100, 149, 237),  # Cornflower blue
        text="Classic Duel",
        description="Human vs Human",
        icon_char="♔"
    )
    
    draw_premium_button(
        btn_easy,
        primary_color=(34, 139, 34),   # Forest green
        accent_color=(50, 205, 50),    # Lime green
        text="AI Easy",
        description="Beginner Level (Depth 2)",
        icon_char="🤖"
    )
    
    draw_premium_button(
        btn_medium,
        primary_color=(255, 140, 0),   # Dark orange
        accent_color=(255, 165, 0),    # Orange
        text="AI Medium",
        description="Intermediate Level (Depth 3)",
        icon_char="⚡"
    )
    
    draw_premium_button(
        btn_hard,
        primary_color=(220, 20, 60),   # Crimson
        accent_color=(255, 69, 0),     # Red orange
        text="AI Hard",
        description="Expert Level (Depth 4)",
        icon_char="🔥"
    )
    
    # Footer text
    footer_font = pygame.font.SysFont("segoeui", 16)
    footer_text = "Press ESC to exit • R to restart game • S for statistics • U to undo"
    footer_surface = footer_font.render(footer_text, True, (120, 120, 120))
    footer_x = window.get_width() // 2 - footer_surface.get_width() // 2
    window.blit(footer_surface, (footer_x, window.get_height() - 40))
    
    pygame.display.update()
    return btn_classic, btn_easy, btn_medium, btn_hard

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
    
    # --- Game mode selection screen ---
    selecting_mode = True
    while selecting_mode:
        btn_classic, btn_easy, btn_medium, btn_hard = draw_mode_selection(window, font)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if btn_classic.collidepoint(event.pos):
                    game_mode = "2V2"
                    ai_player = None
                    selecting_mode = False
                elif btn_easy.collidepoint(event.pos):
                    game_mode = "AI"
                    ai_depth = 2
                    ai_player = ChessAI(depth=ai_depth)
                    selecting_mode = False
                elif btn_medium.collidepoint(event.pos):
                    game_mode = "AI"
                    ai_depth = 3
                    ai_player = ChessAI(depth=ai_depth)
                    selecting_mode = False
                elif btn_hard.collidepoint(event.pos):
                    game_mode = "AI"
                    ai_depth = 4
                    ai_player = ChessAI(depth=ai_depth)
                    selecting_mode = False
        clock.tick(60)  # Smoother animation
    
    # Initialize game state with selected mode
    game = ChessGame(sounds, game_mode=game_mode)
    
    # Main game loop
    running = True
    ai_thinking = False
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                if game and hasattr(game, 'close_engine'):
                    game.close_engine()
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_r:
                    game.reset_game()
                    show_score_screen = False
                    ai_thinking = False
                if event.key == K_s:
                    show_score_screen = not show_score_screen
                if event.key == K_u:
                    if game.undo_move():
                        game.play_sound("move")
                        ai_thinking = False
                        # If in AI mode and it's now human's turn, undo one more move
                        if game_mode == "AI" and game.turn == 'b':
                            game.undo_move()
            if event.type == MOUSEBUTTONDOWN and not show_score_screen and not ai_thinking:
                if event.button == 1:  # Left click
                    x, y = event.pos
                    # Only process clicks on the board
                    if x < 8 * 80 and y < 8 * 80:  # WIDTH, HEIGHT
                        col = x // 80  # SQUARE_SIZE
                        row = y // 80  # SQUARE_SIZE
                        moved = game.select_piece(row, col)
                        
                        # If in AI mode and human just moved, trigger AI move
                        if game_mode == "AI" and moved and not game.game_over and game.turn == 'b':
                            ai_thinking = True

        # Handle AI move
        if game_mode == "AI" and ai_player and game.turn == 'b' and not game.game_over and ai_thinking:
            # Get AI move
            ai_move = ai_player.get_best_move(game)
            
            if ai_move:
                from_row, from_col, to_row, to_col = ai_move
                # Set the selected piece and make the move
                game.selected_piece = (from_row, from_col)
                game.valid_moves = game.get_valid_moves(from_row, from_col)
                game.move_piece(to_row, to_col)
            
            ai_thinking = False

        # Clear screen
        from constants import PANEL_BG
        window.fill(PANEL_BG)
        
        # Draw the game
        draw_board(window, game, pieces)
        if show_score_screen:
            draw_score_screen(window, game, pieces)
        else:
            draw_sidebar(window, game, pieces)
            
        # Show AI thinking indicator
        if ai_thinking:
            thinking_font = pygame.font.SysFont("segoeui", 24, bold=True)
            thinking_text = thinking_font.render("AI is thinking...", True, (255, 255, 0))
            window.blit(thinking_text, (650, 100))
        
        # Update display
        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()