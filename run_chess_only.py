#!/usr/bin/env python3
"""
Chess Game (No Auto Gesture Control)
====================================

This version of the chess game doesn't automatically start gesture control.
Use this when you want to run gesture control separately.
"""

import sys
import os
import pygame
from pygame.locals import QUIT, MOUSEBUTTONDOWN

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run chess game without auto gesture control"""
    print("🎮 Chess Game (Standalone)")
    print("=========================")
    print("This is the chess game without automatic gesture control.")
    print("If you want volume control, run 'python run_camera_only.py' in another terminal.")
    print()
    
    try:
        pygame.init()
        pygame.mixer.init()
        
        from utils import setup_window, create_piece_surfaces, initialize_sounds
        from models import ChessGame
        from ui import draw_board, draw_sidebar, draw_score_screen
        from ai import ChessAI
        from constants import FPS
        import threading
        import math
        
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
        AI_MOVE_COMPLETE = pygame.USEREVENT + 1
        
        print("✅ Chess game initialized successfully!")
        print("🎯 Use the game window to play chess")
        print()
        
        # Import the game mode selection function
        from main import draw_mode_selection
        
        # Game mode selection
        selecting_mode = True
        while selecting_mode:
            btn_classic, btn_ai = draw_mode_selection(window, font)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if btn_classic.collidepoint(mouse_pos):
                        game_mode = "classic"
                        game = ChessGame()
                        selecting_mode = False
                        print("🎮 Classic mode selected (Human vs Human)")
                    elif btn_ai.collidepoint(mouse_pos):
                        game_mode = "ai"
                        game = ChessGame()
                        ai_player = ChessAI(depth=ai_depth)
                        selecting_mode = False
                        print("🤖 AI mode selected (Human vs Computer)")
            
            pygame.display.update()
            clock.tick(FPS)
        
        # Main game loop (simplified version)
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == AI_MOVE_COMPLETE:
                    # Handle AI move completion
                    ai_move = event.ai_move
                    if ai_move and game:
                        game.make_move(ai_move)
                        if sounds:
                            sounds['move'].play()
                # Add other event handling here...
            
            # Clear screen
            from constants import PANEL_BG
            window.fill(PANEL_BG)
            
            # Draw the game components
            if game:
                draw_board(window, game, pieces)
                if show_score_screen:
                    draw_score_screen(window, game, pieces, mouse_pos=mouse_pos)
                else:
                    draw_sidebar(window, game, pieces, mouse_pos=mouse_pos)
            
            # Update display
            pygame.display.update()
            clock.tick(FPS)
        
        print("👋 Game ended")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("  source .venv/bin/activate")
        print("  pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            pygame.quit()
        except:
            pass
    
    return 0

if __name__ == "__main__":
    sys.exit(main())