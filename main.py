import pygame
import sys
from pygame.locals import *

from constants import FPS
from models import ChessGame
from ui import draw_board, draw_sidebar, draw_score_screen
from utils import setup_window, create_piece_surfaces, initialize_sounds

def main():
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()
    
    # Set up the window
    window = setup_window()
    clock = pygame.time.Clock()
    
    # Initialize sounds
    sounds = initialize_sounds()
    
    # Initialize game state
    game = ChessGame(sounds)
    
    # Create piece images
    pieces = create_piece_surfaces()
    
    # Game state variables
    show_score_screen = False
    
    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_r:
                    game.reset_game()
                    show_score_screen = False
                if event.key == K_s:
                    show_score_screen = not show_score_screen
                if event.key == K_u:
                    if game.undo_move():
                        game.play_sound("move")
            
            if event.type == MOUSEBUTTONDOWN and not show_score_screen:
                if event.button == 1:  # Left click
                    x, y = event.pos
                    
                    # Only process clicks on the board
                    if x < 8 * 80 and y < 8 * 80:  # WIDTH, HEIGHT
                        col = x // 80  # SQUARE_SIZE
                        row = y // 80  # SQUARE_SIZE
                        
                        game.select_piece(row, col)
        
        # Clear screen
        from constants import PANEL_BG
        window.fill(PANEL_BG)
        
        # Draw the game
        draw_board(window, game, pieces)
        
        if show_score_screen:
            draw_score_screen(window, game, pieces)
        else:
            draw_sidebar(window, game, pieces)
        
        # Update display
        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main()