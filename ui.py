import pygame
import math
from constants import (
    WIDTH, HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT, BOARD_SIZE, SQUARE_SIZE,
    LIGHT_SQUARE, DARK_SQUARE, HIGHLIGHT, LIGHT_HIGHLIGHT, MOVE_INDICATOR,
    RED_ACCENT, BLUE_ACCENT, WHITE, BLACK, DARK_OVERLAY, SCORE_BG, PANEL_BG
)
from utils import get_font

def draw_professional_button(window, rect, text, is_hovered=False, button_type="primary"):
    """Draw a professional-looking button with gradient and hover effects"""
    # Define color schemes for different button types
    color_schemes = {
        "primary": {
            "bg": (52, 73, 94),      # Professional blue-gray
            "bg_hover": (41, 128, 185),  # Brighter blue on hover
            "border": (34, 49, 63),   # Darker border
            "text": WHITE
        },
        "danger": {
            "bg": (192, 57, 43),      # Professional red
            "bg_hover": (231, 76, 60), # Brighter red on hover
            "border": (169, 50, 38),   # Darker border
            "text": WHITE
        },
        "success": {
            "bg": (39, 174, 96),      # Professional green
            "bg_hover": (46, 204, 113), # Brighter green on hover
            "border": (34, 153, 84),   # Darker border
            "text": WHITE
        }
    }
    
    scheme = color_schemes.get(button_type, color_schemes["primary"])
    bg_color = scheme["bg_hover"] if is_hovered else scheme["bg"]
    
    # Draw button with gradient effect
    # Main button background
    pygame.draw.rect(window, bg_color, rect, border_radius=8)
    
    # Add subtle gradient effect
    gradient_surface = pygame.Surface((rect.width, rect.height // 2), pygame.SRCALPHA)
    gradient_color = (*bg_color[:3], 60)  # Semi-transparent version
    pygame.draw.rect(gradient_surface, gradient_color, (0, 0, rect.width, rect.height // 2), border_radius=8)
    window.blit(gradient_surface, (rect.x, rect.y))
    
    # Draw border
    pygame.draw.rect(window, scheme["border"], rect, 2, border_radius=8)
    
    # Add inner highlight for 3D effect
    if not is_hovered:
        inner_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height - 4)
        highlight_color = (*bg_color[:3], 40)
        highlight_surface = pygame.Surface((inner_rect.width, 2), pygame.SRCALPHA)
        highlight_surface.fill((*WHITE[:3], 60))
        window.blit(highlight_surface, (inner_rect.x, inner_rect.y))
    
    # Draw button text
    font = pygame.font.SysFont("segoeui", 16, bold=True)
    text_surface = font.render(text, True, scheme["text"])
    text_rect = text_surface.get_rect(center=rect.center)
    window.blit(text_surface, text_rect)
    
    return rect  # Return rect for click detection

def draw_board(window, game, pieces):
    # Draw chess board with 3D effect
    board_surface = pygame.Surface((WIDTH, HEIGHT))
    
    # Draw board background
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            # Create 3D effect with slightly different shades
            if (row + col) % 2 == 0:  # Light square
                pygame.draw.rect(board_surface, LIGHT_SQUARE, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                # Add subtle gradient
                for i in range(5):
                    shade = (240 - i*5, 217 - i*3, 181 - i*3)
                    pygame.draw.rect(board_surface, shade, 
                                     (col * SQUARE_SIZE + i, row * SQUARE_SIZE + i, 
                                      SQUARE_SIZE - i*2, SQUARE_SIZE - i*2), 1)
            else:  # Dark square
                pygame.draw.rect(board_surface, DARK_SQUARE, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                # Add subtle gradient
                for i in range(5):
                    shade = (181 - i*5, 136 - i*3, 99 - i*3)
                    pygame.draw.rect(board_surface, shade, 
                                     (col * SQUARE_SIZE + i, row * SQUARE_SIZE + i, 
                                      SQUARE_SIZE - i*2, SQUARE_SIZE - i*2), 1)
            
            # Draw coordinates in small corner of squares
            if row == 7:  # Bottom row - show file (column) labels
                font = pygame.font.SysFont('Arial', 12)
                label = font.render(chr(97 + col), True, (0, 0, 0) if (row + col) % 2 == 0 else (255, 255, 255))
                board_surface.blit(label, (col * SQUARE_SIZE + SQUARE_SIZE - 12, row * SQUARE_SIZE + SQUARE_SIZE - 12))
            
            if col == 0:  # Leftmost column - show rank (row) labels
                font = pygame.font.SysFont('Arial', 12)
                label = font.render(str(8 - row), True, (0, 0, 0) if (row + col) % 2 == 0 else (255, 255, 255))
                board_surface.blit(label, (col * SQUARE_SIZE + 3, row * SQUARE_SIZE + 3))
            
            # Highlight last move
            if game.last_move:
                from_row, from_col, to_row, to_col = game.last_move
                if (row, col) == (from_row, from_col) or (row, col) == (to_row, to_col):
                    highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    highlight.fill(MOVE_INDICATOR)
                    board_surface.blit(highlight, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            
            # Highlight king in check
            piece = game.board[row][col]
            if piece and piece[1] == 'k' and game.check[piece[0]]:
                highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                highlight.fill((255, 0, 0, 100))  # Red with transparency
                board_surface.blit(highlight, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            
            # Highlight selected piece
            if game.selected_piece and game.selected_piece == (row, col):
                highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                highlight.fill(HIGHLIGHT)
                board_surface.blit(highlight, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            
            # Highlight valid moves
            if (row, col) in game.valid_moves:
                highlight = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                
                # If square is empty, show dot, otherwise show capture highlight
                if not game.board[row][col]:
                    # Show dot in center
                    pygame.draw.circle(highlight, LIGHT_HIGHLIGHT, 
                                      (SQUARE_SIZE // 2, SQUARE_SIZE // 2), 
                                      SQUARE_SIZE // 6)
                else:
                    # Show border for captures
                    pygame.draw.rect(highlight, LIGHT_HIGHLIGHT, 
                                    (0, 0, SQUARE_SIZE, SQUARE_SIZE), 4)
                
                board_surface.blit(highlight, (col * SQUARE_SIZE, row * SQUARE_SIZE))
    
    # Add border around the board
    pygame.draw.rect(board_surface, (30, 30, 30), (0, 0, WIDTH, HEIGHT), 2)
    
    # Draw pieces on the board
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = game.board[row][col]
            if piece:
                # Skip drawing the piece being animated
                if game.current_animation and game.selected_piece == (row, col):
                    continue
                
                # Draw the piece
                board_surface.blit(pieces[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))
    
    # Draw animation if active
    if game.current_animation:
        pos = game.current_animation.update()
        
        if game.current_animation.complete:
            game.current_animation = None
        else:
            # Draw the animated piece
            board_surface.blit(pieces[game.animating_piece], (int(pos[0]), int(pos[1])))
    
    # Draw particle effects
    for ps in game.particle_systems[:]:
        ps.update()
        if not ps.alive:
            game.particle_systems.remove(ps)
        else:
            ps.draw(board_surface)
    
    # Add drop shadow effect to the board
    shadow_offset = 5
    shadow = pygame.Surface((WIDTH, HEIGHT))
    shadow.fill((0, 0, 0))
    window.blit(shadow, (shadow_offset, shadow_offset))
    
    # Blit the board to the window
    window.blit(board_surface, (0, 0))

def draw_sidebar(window, game, pieces, sidebar_scroll=0, mouse_pos=None):
    # Get current window dimensions
    window_width = window.get_width()
    window_height = window.get_height()
    
    # Calculate sidebar dimensions
    sidebar_width = window_width - WIDTH
    sidebar_rect = pygame.Rect(WIDTH, 0, sidebar_width, window_height)
    pygame.draw.rect(window, PANEL_BG, sidebar_rect)
    
    # Add some depth with a gradient
    for i in range(5):
        pygame.draw.rect(window, (40 + i*2, 44 + i*2, 52 + i*2), 
                        (WIDTH + i, i, sidebar_width - i*2, window_height - i*2), 1)
    
    title_font = get_font(28, bold=True)
    font_large = get_font(22)
    font = get_font(18)
    font_small = get_font(14)
    
    # Title bar
    title_rect = pygame.Rect(WIDTH, 0, sidebar_width, 50)
    pygame.draw.rect(window, (30, 34, 42), title_rect)
    title_text = title_font.render("CHESS", True, WHITE)
    window.blit(title_text, (WIDTH + sidebar_width // 2 - title_text.get_width() // 2, 10))
    
    # Current turn indicator with glow effect
    turn_label = font_large.render("CURRENT TURN", True, WHITE)
    window.blit(turn_label, (WIDTH + 20, 70))
    
    turn_rect = pygame.Rect(WIDTH + 20, 100, sidebar_width - 40, 40)
    turn_color = BLUE_ACCENT if game.turn == 'w' else (50, 50, 50)
    
    # Add glow effect if in check
    if game.check[game.turn]:
        # Pulsating glow
        glow_intensity = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 0.5
        glow_color = (255, 0, 0, int(100 * glow_intensity))
        glow_surf = pygame.Surface((turn_rect.width + 20, turn_rect.height + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, glow_color, (0, 0, turn_rect.width + 20, turn_rect.height + 20), border_radius=10)
        window.blit(glow_surf, (turn_rect.x - 10, turn_rect.y - 10))
    
    pygame.draw.rect(window, turn_color, turn_rect, border_radius=5)
    
    for i in range(3):  # Add 3D effect
        pygame.draw.rect(window, (turn_color[0] - i*10, turn_color[1] - i*10, turn_color[2] - i*10), 
                        (turn_rect.x, turn_rect.y, turn_rect.width, turn_rect.height), 
                        1, border_radius=5)
    
    # CHANGED LINE: Use 'White' and 'Black' directly instead of player_names
    turn_text = font_large.render(f"{'White' if game.turn == 'w' else 'Black'}'s Turn", True, WHITE)
    window.blit(turn_text, (turn_rect.centerx - turn_text.get_width() // 2, turn_rect.centery - turn_text.get_height() // 2))
    
    if game.check[game.turn]:
        check_text = font.render("CHECK!", True, RED_ACCENT)
        window.blit(check_text, (turn_rect.centerx - check_text.get_width() // 2, turn_rect.bottom + 5))
    
    # Score panel
    score_label = font_large.render("SCORE", True, WHITE)
    window.blit(score_label, (WIDTH + 20, 160))
    
    score_rect = pygame.Rect(WIDTH + 20, 190, sidebar_width - 40, 60)
    pygame.draw.rect(window, (50, 54, 62), score_rect, border_radius=5)
    
    # White score
    white_score_rect = pygame.Rect(score_rect.x + 10, score_rect.y + 10, (score_rect.width - 30) // 2, score_rect.height - 20)
    pygame.draw.rect(window, BLUE_ACCENT, white_score_rect, border_radius=5)
    white_score_text = font_large.render(str(game.scores['w']), True, WHITE)
    window.blit(white_score_text, (white_score_rect.centerx - white_score_text.get_width() // 2, 
                                 white_score_rect.centery - white_score_text.get_height() // 2))
    white_label = font_small.render("WHITE", True, WHITE)
    window.blit(white_label, (white_score_rect.centerx - white_label.get_width() // 2, white_score_rect.y - 20))
    
    # Black score
    black_score_rect = pygame.Rect(white_score_rect.right + 10, score_rect.y + 10, white_score_rect.width, white_score_rect.height)
    pygame.draw.rect(window, (50, 50, 50), black_score_rect, border_radius=5)
    black_score_text = font_large.render(str(game.scores['b']), True, WHITE)
    window.blit(black_score_text, (black_score_rect.centerx - black_score_text.get_width() // 2, 
                                 black_score_rect.centery - black_score_text.get_height() // 2))
    black_label = font_small.render("BLACK", True, WHITE)
    window.blit(black_label, (black_score_rect.centerx - black_label.get_width() // 2, black_score_rect.y - 20))
    
    # Captured pieces
    captures_label = font_large.render("CAPTURED PIECES", True, WHITE)
    window.blit(captures_label, (WIDTH + 20, 270))
    
    # White captures
    white_captures_rect = pygame.Rect(WIDTH + 20, 300, sidebar_width - 40, 50)
    pygame.draw.rect(window, (50, 54, 62), white_captures_rect, border_radius=5)
    
    white_label = font_small.render("WHITE CAPTURED:", True, WHITE)
    window.blit(white_label, (white_captures_rect.x + 10, white_captures_rect.y + 5))
    
    # Display black pieces captured by white
    for i, piece in enumerate(game.captured_pieces['w']):
        piece_symbol = pieces[piece]
        small_piece = pygame.transform.scale(piece_symbol, (30, 30))
        window.blit(small_piece, (white_captures_rect.x + 10 + i * 35, white_captures_rect.y + 20))
    
    # Black captures
    black_captures_rect = pygame.Rect(WIDTH + 20, 360, sidebar_width - 40, 50)
    pygame.draw.rect(window, (50, 54, 62), black_captures_rect, border_radius=5)
    
    black_label = font_small.render("BLACK CAPTURED:", True, WHITE)
    window.blit(black_label, (black_captures_rect.x + 10, black_captures_rect.y + 5))
    
    # Display white pieces captured by black
    for i, piece in enumerate(game.captured_pieces['b']):
        piece_symbol = pieces[piece]
        small_piece = pygame.transform.scale(piece_symbol, (30, 30))
        window.blit(small_piece, (black_captures_rect.x + 10 + i * 35, black_captures_rect.y + 20))
    
    # Move history
    history_label = font_large.render("LAST MOVES", True, WHITE)
    window.blit(history_label, (WIDTH + 20, 430))
    
    history_rect = pygame.Rect(WIDTH + 20, 460, sidebar_width - 40, 150)
    pygame.draw.rect(window, (50, 54, 62), history_rect, border_radius=5)
    
    # Show last 5 moves (or fewer if not that many)
    move_history = game.move_history[-5:] if game.move_history else []
    for i, move in enumerate(reversed(move_history)):
        _, _, _, _, _, notation = move
        
        # Alternate background for better readability
        move_rect = pygame.Rect(history_rect.x + 5, history_rect.y + 5 + i * 28, history_rect.width - 10, 25)
        if i % 2 == 0:
            pygame.draw.rect(window, (60, 64, 72), move_rect, border_radius=3)
        
        move_num = len(game.move_history) - len(move_history) + i + 1
        num_text = font_small.render(f"{move_num}.", True, WHITE)
        window.blit(num_text, (move_rect.x + 5, move_rect.centery - num_text.get_height() // 2))
        
        notation_text = font_small.render(notation, True, WHITE)
        window.blit(notation_text, (move_rect.x + 40, move_rect.centery - notation_text.get_height() // 2))
    
    # Game status and controls
    status_y = min(630, window_height - 150)  # Adjust position based on window height
    if game.game_over:
        status_rect = pygame.Rect(WIDTH + 20, status_y, sidebar_width - 40, 50)
        
        # CHANGED: Use 'WHITE' and 'BLACK' directly instead of using player_names
        if game.winner:
            status_color = BLUE_ACCENT if game.winner == 'w' else (50, 50, 50)
            status_text = f"{'WHITE' if game.winner == 'w' else 'BLACK'} WINS!"
        else:
            status_color = (150, 150, 150)
            status_text = "DRAW"
        
        # Pulsating effect
        intensity = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.25 + 0.5
        adjusted_color = tuple(int(c * intensity) for c in status_color[:3])
        
        pygame.draw.rect(window, adjusted_color, status_rect, border_radius=5)
        
        game_over_text = font_large.render("GAME OVER", True, WHITE)
        window.blit(game_over_text, (status_rect.centerx - game_over_text.get_width() // 2, 
                                  status_rect.y + 5))
        
        winner_text = font.render(status_text, True, WHITE)
        window.blit(winner_text, (status_rect.centerx - winner_text.get_width() // 2, 
                               status_rect.y + 25))
    
    # Controls Section with Buttons
    controls_y = min(window_height - 120, status_y + 70)  # Position controls at bottom or after status
    
    # Action Buttons
    button_width = (sidebar_width - 60) // 2  # Two buttons per row with spacing
    button_height = 35
    button_spacing = 10
    
    # First row of buttons
    restart_rect = pygame.Rect(WIDTH + 20, controls_y, button_width, button_height)
    undo_rect = pygame.Rect(WIDTH + 30 + button_width, controls_y, button_width, button_height)
    
    # Second row of buttons  
    stats_rect = pygame.Rect(WIDTH + 20, controls_y + button_height + button_spacing, button_width, button_height)
    quit_rect = pygame.Rect(WIDTH + 30 + button_width, controls_y + button_height + button_spacing, button_width, button_height)
    
    # Check for hover states
    mouse_x, mouse_y = mouse_pos if mouse_pos else (0, 0)
    restart_hovered = restart_rect.collidepoint(mouse_x, mouse_y)
    undo_hovered = undo_rect.collidepoint(mouse_x, mouse_y)
    stats_hovered = stats_rect.collidepoint(mouse_x, mouse_y)
    quit_hovered = quit_rect.collidepoint(mouse_x, mouse_y)
    
    # Draw buttons with professional styling
    draw_professional_button(window, restart_rect, "NEW GAME", restart_hovered, "success")
    draw_professional_button(window, undo_rect, "UNDO", undo_hovered, "primary")
    draw_professional_button(window, stats_rect, "STATS", stats_hovered, "primary")
    draw_professional_button(window, quit_rect, "QUIT", quit_hovered, "danger")
    
    # Return button rectangles for click detection
    return {
        'restart': restart_rect,
        'undo': undo_rect,
        'stats': stats_rect,
        'quit': quit_rect
    }

def draw_score_screen(window, game, pieces, mouse_pos=None):
    # Get current window dimensions for responsive design
    window_width = window.get_width()
    window_height = window.get_height()
    
    # Create a dark overlay with transparency
    overlay = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
    overlay.fill(DARK_OVERLAY)
    window.blit(overlay, (0, 0))
    
    # Responsive panel sizing
    panel_width = min(window_width - 80, 900)
    panel_height = min(window_height - 80, 700)
    panel_x = (window_width - panel_width) // 2
    panel_y = (window_height - panel_height) // 2
    
    # Draw the panel with elegant design
    # Shadow effect
    shadow_rect = pygame.Rect(panel_x + 8, panel_y + 8, panel_width, panel_height)
    shadow_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, 100), shadow_surf.get_rect(), border_radius=20)
    window.blit(shadow_surf, shadow_rect)
    
    # Main panel background with gradient
    for i in range(panel_height):
        alpha = i / panel_height
        color = (
            int(SCORE_BG[0] + (SCORE_BG[0] * 0.3) * alpha),
            int(SCORE_BG[1] + (SCORE_BG[1] * 0.3) * alpha),
            int(SCORE_BG[2] + (SCORE_BG[2] * 0.3) * alpha)
        )
        pygame.draw.line(window, color, (panel_x, panel_y + i), (panel_x + panel_width, panel_y + i))
    
    # Panel border
    pygame.draw.rect(window, (70, 80, 90), (panel_x, panel_y, panel_width, panel_height), 3, border_radius=20)
    
    # Responsive font sizes
    title_size = max(24, min(36, panel_width // 25))
    heading_size = max(18, min(24, panel_width // 35))
    subheading_size = max(16, min(20, panel_width // 40))
    text_size = max(14, min(18, panel_width // 50))
    small_size = max(12, min(14, panel_width // 60))
    
    title_font = get_font(title_size, bold=True)
    heading_font = get_font(heading_size, bold=True)
    subheading_font = get_font(subheading_size, bold=True)
    font = get_font(text_size)
    small_font = get_font(small_size)
    
    # Title bar with gradient
    title_height = 60
    title_rect = pygame.Rect(panel_x, panel_y, panel_width, title_height)
    for i in range(title_height):
        alpha = i / title_height
        color = (
            int(15 + (25 - 15) * alpha),
            int(25 + (35 - 25) * alpha),
            int(40 + (50 - 40) * alpha)
        )
        pygame.draw.line(window, color, (panel_x, panel_y + i), (panel_x + panel_width, panel_y + i))
    
    pygame.draw.rect(window, (70, 80, 90), title_rect, 2, border_top_left_radius=20, border_top_right_radius=20)
    
    # Title with professional styling and icons
    title_text = title_font.render("📊 GAME STATISTICS", True, WHITE)
    title_shadow = title_font.render("📊 GAME STATISTICS", True, (0, 0, 0))
    window.blit(title_shadow, (title_rect.centerx - title_text.get_width() // 2 + 2, title_rect.centery - title_text.get_height() // 2 + 2))
    window.blit(title_text, (title_rect.centerx - title_text.get_width() // 2, title_rect.centery - title_text.get_height() // 2))
    
    # Content area
    content_y = panel_y + title_height + 20
    content_height = panel_height - title_height - 80  # Leave space for return button
    
    # Game status section
    status_height = 80
    status_y = content_y
    
    # Status background
    status_rect = pygame.Rect(panel_x + 20, status_y, panel_width - 40, status_height)
    pygame.draw.rect(window, (35, 45, 55), status_rect, border_radius=10)
    pygame.draw.rect(window, (60, 70, 80), status_rect, 2, border_radius=10)
    
    # Game status text with enhanced styling
    if game.game_over:
        if hasattr(game, 'winner') and game.winner:
            if game.winner == 'w':
                status_text = "👑 WHITE VICTORIOUS!"
                status_color = BLUE_ACCENT
            elif game.winner == 'b':
                status_text = "👑 BLACK VICTORIOUS!"
                status_color = (80, 80, 80)
            else:
                status_text = "🤝 HONORABLE DRAW"
                status_color = (150, 150, 150)
        else:
            status_text = "🤝 HONORABLE DRAW"
            status_color = (150, 150, 150)
    else:
        current_player = 'WHITE' if game.turn == 'w' else 'BLACK'
        status_text = f"⚡ {current_player}'S MOVE"
        status_color = BLUE_ACCENT if game.turn == 'w' else (150, 150, 150)
        
        if hasattr(game, 'check') and game.check[game.turn]:
            status_text += " - ⚠️ IN CHECK!"
            status_color = RED_ACCENT
    
    status_surface = heading_font.render(status_text, True, status_color)
    window.blit(status_surface, (status_rect.centerx - status_surface.get_width() // 2, status_rect.centery - status_surface.get_height() // 2))
    
    # Player comparison section
    comparison_y = status_y + status_height + 20
    comparison_height = 200
    
    # Player boxes
    box_width = (panel_width - 80) // 2
    white_box = pygame.Rect(panel_x + 20, comparison_y, box_width, comparison_height)
    black_box = pygame.Rect(panel_x + 40 + box_width, comparison_y, box_width, comparison_height)
    
    for box, color, label, theme_color in [(white_box, 'w', "⚪ WHITE PLAYER", (50, 120, 200)), (black_box, 'b', "⚫ BLACK PLAYER", (60, 60, 60))]:
        # Box background with improved gradient
        for i in range(comparison_height):
            alpha = i / comparison_height
            bg_color = (
                int(theme_color[0] * (0.2 + 0.3 * alpha)),
                int(theme_color[1] * (0.2 + 0.3 * alpha)),
                int(theme_color[2] * (0.2 + 0.3 * alpha))
            )
            pygame.draw.line(window, bg_color, (box.x, box.y + i), (box.right, box.y + i))
        
        # Enhanced box border with subtle glow effect
        pygame.draw.rect(window, theme_color, box, 3, border_radius=12)
        inner_border = pygame.Rect(box.x + 1, box.y + 1, box.width - 2, box.height - 2)
        pygame.draw.rect(window, (*theme_color[:3], 100), inner_border, 1, border_radius=11)
        
        # Enhanced player label with icon
        label_surface = subheading_font.render(label, True, WHITE)
        label_bg = pygame.Rect(box.x + 12, box.y + 12, box.width - 24, 32)
        pygame.draw.rect(window, theme_color, label_bg, border_radius=6)
        window.blit(label_surface, (label_bg.centerx - label_surface.get_width() // 2, label_bg.centery - label_surface.get_height() // 2))
        
        # Score with icon
        if hasattr(game, 'scores'):
            score_text = f"🎯 Score: {game.scores[color]}"
        else:
            score_text = "🎯 Score: 0"
        score_surface = font.render(score_text, True, WHITE)
        window.blit(score_surface, (box.x + 18, box.y + 55))
        
        # Enhanced stats with icons
        if hasattr(game, 'stats'):
            stats_data = [
                ("🔥 Moves", game.stats[color].get('moves', 0)),
                ("⚔️ Captures", game.stats[color].get('captures', 0)),
                ("⚠️ Checks", game.stats[color].get('checks', 0))
            ]
        else:
            stats_data = [("🔥 Moves", 0), ("⚔️ Captures", 0), ("⚠️ Checks", 0)]
        
        for i, (stat_name, stat_value) in enumerate(stats_data):
            stat_text = f"{stat_name}: {stat_value}"
            stat_surface = small_font.render(stat_text, True, WHITE)
            window.blit(stat_surface, (box.x + 18, box.y + 85 + i * 22))
        
        # Enhanced remaining pieces display
        pieces_text = small_font.render("🏰 Army:", True, WHITE)
        window.blit(pieces_text, (box.x + 18, box.y + 155))
        
        # Count pieces
        piece_counts = {'p': 0, 'r': 0, 'n': 0, 'b': 0, 'q': 0, 'k': 0}
        for row in game.board:
            for piece in row:
                if piece and piece[0] == color:
                    piece_counts[piece[1]] += 1
        
        # Enhanced piece counts display
        piece_display = f"♙{piece_counts['p']} ♖{piece_counts['r']} ♘{piece_counts['n']} ♗{piece_counts['b']} ♕{piece_counts['q']}"
        pieces_surface = small_font.render(piece_display, True, WHITE)
        window.blit(pieces_surface, (box.x + 18, box.y + 175))
    
    # Enhanced Move history section
    history_y = comparison_y + comparison_height + 20
    history_height = content_height - (history_y - content_y) - 20
    
    if history_height > 60:  # Only show if there's enough space
        history_rect = pygame.Rect(panel_x + 20, history_y, panel_width - 40, history_height)
        
        # History background with subtle gradient
        for i in range(history_height):
            alpha = i / history_height
            bg_color = (
                int(25 + (35 - 25) * alpha),
                int(35 + (45 - 35) * alpha),
                int(45 + (55 - 45) * alpha)
            )
            pygame.draw.line(window, bg_color, (history_rect.x, history_rect.y + i), (history_rect.right, history_rect.y + i))
        
        pygame.draw.rect(window, (70, 80, 90), history_rect, 2, border_radius=12)
        
        # Enhanced history title with icon
        history_title = subheading_font.render("📋 MOVE HISTORY", True, WHITE)
        window.blit(history_title, (history_rect.x + 18, history_rect.y + 12))
        
        # Enhanced move list
        if hasattr(game, 'move_history') and game.move_history:
            moves_area = pygame.Rect(history_rect.x + 18, history_rect.y + 45, history_rect.width - 36, history_rect.height - 55)
            max_moves = min(len(game.move_history), (moves_area.height - 10) // 20)
            recent_moves = game.move_history[-max_moves:] if max_moves > 0 else []
            
            for i, move in enumerate(recent_moves):
                if len(move) >= 6:
                    move_num = len(game.move_history) - len(recent_moves) + i + 1
                    _, _, _, _, piece, notation = move
                    move_color = piece[0] if piece else 'w'
                    
                    # Enhanced alternating row backgrounds
                    move_y = moves_area.y + i * 20
                    row_rect = pygame.Rect(moves_area.x - 3, move_y - 1, moves_area.width + 6, 18)
                    if i % 2 == 1:
                        pygame.draw.rect(window, (35, 45, 55), row_rect, border_radius=4)
                    else:
                        pygame.draw.rect(window, (40, 50, 60), row_rect, border_radius=4)
                    
                    # Move text with better formatting
                    move_icon = "⚪" if move_color == 'w' else "⚫"
                    move_text = f"{move_icon} {move_num}. {notation}"
                    text_color = BLUE_ACCENT if move_color == 'w' else (200, 200, 200)
                    move_surface = small_font.render(move_text, True, text_color)
                    window.blit(move_surface, (moves_area.x + 8, move_y + 1))
        else:
            no_moves_text = font.render("🎮 No moves recorded yet", True, (140, 140, 140))
            window.blit(no_moves_text, (history_rect.x + 18, history_rect.y + 50))
    
    # Return button with professional styling
    button_width = min(250, panel_width - 100)
    button_height = 45
    button_x = panel_x + (panel_width - button_width) // 2
    button_y = panel_y + panel_height - 65
    
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    # Check for hover state
    mouse_x, mouse_y = mouse_pos if mouse_pos else (0, 0)
    is_hovered = button_rect.collidepoint(mouse_x, mouse_y)
    
    # Draw professional return button
    draw_professional_button(window, button_rect, "← RETURN TO GAME", is_hovered, "primary")
    
    return button_rect  # Return button rectangle for click detection