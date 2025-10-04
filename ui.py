import pygame
import math
from constants import (
    WIDTH, HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT, BOARD_SIZE, SQUARE_SIZE,
    LIGHT_SQUARE, DARK_SQUARE, HIGHLIGHT, LIGHT_HIGHLIGHT, MOVE_INDICATOR,
    RED_ACCENT, BLUE_ACCENT, WHITE, BLACK, DARK_OVERLAY, SCORE_BG, PANEL_BG
)
from utils import get_font

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

def draw_sidebar(window, game, pieces, sidebar_scroll=0):
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
    
    # Controls
    controls_y = min(window_height - 90, status_y + 70)  # Position controls at bottom or after status
    controls_rect = pygame.Rect(WIDTH + 20, controls_y, sidebar_width - 40, 70)
    pygame.draw.rect(window, (30, 34, 42), controls_rect, border_radius=5)
    
    controls_text = font_small.render("CONTROLS", True, WHITE)
    window.blit(controls_text, (controls_rect.centerx - controls_text.get_width() // 2, controls_rect.y + 5))
    
    key_hints = ["R - Reset Game", "U - Undo Move", "S - Stats Screen", "ESC - Quit"]
    for i, hint in enumerate(key_hints):
        hint_text = font_small.render(hint, True, WHITE)
        x_pos = controls_rect.x + 20 + (i % 2) * ((controls_rect.width - 40) // 2)
        y_pos = controls_rect.y + 25 + (i // 2) * 20
        window.blit(hint_text, (x_pos, y_pos))

def draw_score_screen(window, game, pieces):
    # Create a dark overlay with transparency
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill(DARK_OVERLAY)
    window.blit(overlay, (0, 0))
    
    # Create the stats panel
    panel_width = min(WINDOW_WIDTH - 100, 800)
    panel_height = min(WINDOW_HEIGHT - 100, 600)
    panel_x = (WINDOW_WIDTH - panel_width) // 2
    panel_y = (WINDOW_HEIGHT - panel_height) // 2
    
    # Draw the panel with a 3D effect
    for i in range(5):
        pygame.draw.rect(window, (SCORE_BG[0] + i*3, SCORE_BG[1] + i*3, SCORE_BG[2] + i*3),
                        (panel_x - i, panel_y - i, panel_width + i*2, panel_height + i*2),
                        border_radius=15)
    
    pygame.draw.rect(window, SCORE_BG, (panel_x, panel_y, panel_width, panel_height), border_radius=15)
    
    # Add inner border for more depth
    pygame.draw.rect(window, (40, 50, 60), (panel_x, panel_y, panel_width, panel_height), 2, border_radius=15)
    
    # Add a title bar
    title_rect = pygame.Rect(panel_x, panel_y, panel_width, 60)
    pygame.draw.rect(window, (10, 20, 30), title_rect, border_top_left_radius=15, border_top_right_radius=15)
    
    # Fonts
    title_font = get_font(36, bold=True)
    heading_font = get_font(24, bold=True)
    subheading_font = get_font(20, bold=True)
    font = get_font(18)
    
    # Title
    title_text = title_font.render("GAME STATISTICS", True, WHITE)
    window.blit(title_text, (title_rect.centerx - title_text.get_width() // 2, title_rect.centery - title_text.get_height() // 2))
    
    # Game status
    status_y = panel_y + 80
    status_text = "Game in Progress" if not game.game_over else "Game Over"
    status = heading_font.render(status_text, True, WHITE)
    window.blit(status, (panel_x + panel_width // 2 - status.get_width() // 2, status_y))
    
    # CHANGED: Use 'White' and 'Black' directly 
    if game.game_over:
        if game.winner:
            result_text = f"{'White' if game.winner == 'w' else 'Black'} Wins!"
            result_color = BLUE_ACCENT if game.winner == 'w' else (80, 80, 80)
        else:
            result_text = "Draw"
            result_color = (150, 150, 150)
        
        result = heading_font.render(result_text, True, result_color)
        window.blit(result, (panel_x + panel_width // 2 - result.get_width() // 2, status_y + 40))
    else:
        # CHANGED: Use 'White' and 'Black' directly
        turn_text = f"{'White' if game.turn == 'w' else 'Black'}'s Turn"
        turn = heading_font.render(turn_text, True, BLUE_ACCENT if game.turn == 'w' else (80, 80, 80))
        window.blit(turn, (panel_x + panel_width // 2 - turn.get_width() // 2, status_y + 40))
        
        if game.check[game.turn]:
            check_text = subheading_font.render("In Check!", True, RED_ACCENT)
            window.blit(check_text, (panel_x + panel_width // 2 - check_text.get_width() // 2, status_y + 70))
    
    # Score and pieces
    scores_y = status_y + 100
    
    # Draw player comparison boxes
    box_width = (panel_width - 60) // 2
    white_box = pygame.Rect(panel_x + 20, scores_y, box_width, 250)
    black_box = pygame.Rect(panel_x + 40 + box_width, scores_y, box_width, 250)
    
    # Draw boxes with 3D effect
    for box, color, label in [(white_box, (40, 100, 180), "WHITE"), (black_box, (40, 40, 40), "BLACK")]:
        # Shadow
        shadow_rect = pygame.Rect(box.x + 5, box.y + 5, box.width, box.height)
        pygame.draw.rect(window, (0, 0, 0, 100), shadow_rect, border_radius=10)
        
        # Box
        pygame.draw.rect(window, color, box, border_radius=10)
        
        # Highlight top edge for 3D effect
        highlight_color = tuple(min(255, c + 40) for c in color)
        pygame.draw.line(window, highlight_color, (box.left + 5, box.top + 5), (box.right - 5, box.top + 5), 2)
        pygame.draw.line(window, highlight_color, (box.left + 5, box.top + 5), (box.left + 5, box.bottom - 5), 2)
        
        # Title for the box
        label_text = subheading_font.render(label, True, WHITE)
        window.blit(label_text, (box.centerx - label_text.get_width() // 2, box.y + 15))
    
    # Player stats
    for box, color in [(white_box, 'w'), (black_box, 'b')]:
        # Score
        score_text = heading_font.render(f"Score: {game.scores[color]}", True, WHITE)
        window.blit(score_text, (box.centerx - score_text.get_width() // 2, box.y + 50))
        
        # Stats
        stats = [
            f"Moves: {game.stats[color]['moves']}",
            f"Captures: {game.stats[color]['captures']}",
            f"Checks: {game.stats[color]['checks']}"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = font.render(stat, True, WHITE)
            window.blit(stat_text, (box.x + 20, box.y + 90 + i * 30))
        
        # Pieces remaining
        remaining = font.render("Remaining Pieces:", True, WHITE)
        window.blit(remaining, (box.x + 20, box.y + 180))
        
        # Count pieces
        piece_counts = {'p': 0, 'r': 0, 'n': 0, 'b': 0, 'q': 0, 'k': 0}
        for row in game.board:
            for piece in row:
                if piece and piece[0] == color:
                    piece_counts[piece[1]] += 1
        
        # Show piece counts with icons
        piece_types = [('p', 'Pawns'), ('n', 'Knights'), ('b', 'Bishops'), ('r', 'Rooks'), ('q', 'Queens')]
        for i, (piece_code, piece_name) in enumerate(piece_types):
            # Get piece image and scale down
            piece_img = pieces[color + piece_code]
            small_piece = pygame.transform.scale(piece_img, (25, 25))
            
            # Calculate position
            row, col = divmod(i, 3)
            piece_x = box.x + 20 + col * 80
            piece_y = box.y + 210 + row * 30
            
            # Draw piece icon and count
            window.blit(small_piece, (piece_x, piece_y))
            count_text = font.render(f"x{piece_counts[piece_code]}", True, WHITE)
            window.blit(count_text, (piece_x + 30, piece_y + 5))
    
    # Move history
    history_y = scores_y + 270
    history_text = subheading_font.render("MOVE HISTORY", True, WHITE)
    window.blit(history_text, (panel_x + panel_width // 2 - history_text.get_width() // 2, history_y))
    
    # Create a scrolling move history area
    history_rect = pygame.Rect(panel_x + 20, history_y + 30, panel_width - 40, 100)
    pygame.draw.rect(window, (30, 40, 50), history_rect, border_radius=5)
    
    # Show up to 6 moves in the history box
    max_visible_moves = 6
    move_history = game.move_history[-max_visible_moves:] if len(game.move_history) > max_visible_moves else game.move_history
    
    for i, move in enumerate(move_history):
        move_num = i + (len(game.move_history) - len(move_history)) + 1
        _, _, _, _, piece, notation = move
        color = piece[0]
        
        # Alternate background colors for better readability
        move_rect = pygame.Rect(history_rect.x + 5, history_rect.y + 5 + i * 15, history_rect.width - 10, 14)
        if i % 2 == 1:
            pygame.draw.rect(window, (40, 50, 60), move_rect, border_radius=2)
        
        # Draw move number
        num_text = font.render(f"{move_num}.", True, WHITE)
        window.blit(num_text, (move_rect.x + 5, move_rect.y))
        
        # Draw player indicator (white/black)
        # CHANGED: Use "W" for White and "B" for Black directly
        color_text = font.render("W" if color == 'w' else "B", True, BLUE_ACCENT if color == 'w' else (150, 150, 150))
        window.blit(color_text, (move_rect.x + 35, move_rect.y))
        
        # Draw notation
        notation_text = font.render(notation, True, WHITE)
        window.blit(notation_text, (move_rect.x + 55, move_rect.y))
    
    # Return button
    button_y = panel_y + panel_height - 50
    button_width = 200
    button_rect = pygame.Rect(panel_x + panel_width // 2 - button_width // 2, button_y, button_width, 30)
    
    # Button with 3D effect
    pygame.draw.rect(window, (60, 70, 80), button_rect, border_radius=5)
    pygame.draw.rect(window, (80, 90, 100), (button_rect.x, button_rect.y, button_rect.width, button_rect.height), 1, border_radius=5)
    
    # Button text
    button_text = font.render("RETURN TO GAME (S)", True, WHITE)
    window.blit(button_text, (button_rect.centerx - button_text.get_width() // 2, button_rect.centery - button_text.get_height() // 2))