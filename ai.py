import random
import copy
from typing import Tuple, List, Optional

class ChessAI:
    def __init__(self, depth=3):
        self.depth = depth
        self.piece_values = {
            'p': 100, 'n': 320, 'b': 330, 'r': 500, 'q': 900, 'k': 20000
        }
        
        # Positional bonus tables for better AI play
        self.pawn_table = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5,  5, 10, 25, 25, 10,  5,  5],
            [0,  0,  0, 20, 20,  0,  0,  0],
            [5, -5,-10,  0,  0,-10, -5,  5],
            [5, 10, 10,-20,-20, 10, 10,  5],
            [0,  0,  0,  0,  0,  0,  0,  0]
        ]
        
        self.knight_table = [
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 15, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-30,-40,-50]
        ]
        
        self.bishop_table = [
            [-20,-10,-10,-10,-10,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5, 10, 10,  5,  0,-10],
            [-10,  5,  5, 10, 10,  5,  5,-10],
            [-10,  0, 10, 10, 10, 10,  0,-10],
            [-10, 10, 10, 10, 10, 10, 10,-10],
            [-10,  5,  0,  0,  0,  0,  5,-10],
            [-20,-10,-10,-10,-10,-10,-10,-20]
        ]
        
        self.rook_table = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [5, 10, 10, 10, 10, 10, 10,  5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [-5,  0,  0,  0,  0,  0,  0, -5],
            [0,  0,  0,  5,  5,  0,  0,  0]
        ]
        
        self.queen_table = [
            [-20,-10,-10, -5, -5,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5,  5,  5,  5,  0,-10],
            [-5,  0,  5,  5,  5,  5,  0, -5],
            [0,  0,  5,  5,  5,  5,  0, -5],
            [-10,  5,  5,  5,  5,  5,  0,-10],
            [-10,  0,  5,  0,  0,  0,  0,-10],
            [-20,-10,-10, -5, -5,-10,-10,-20]
        ]
        
        self.king_table = [
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-30,-40,-40,-50,-50,-40,-40,-30],
            [-20,-30,-30,-40,-40,-30,-30,-20],
            [-10,-20,-20,-20,-20,-20,-20,-10],
            [20, 20,  0,  0,  0,  0, 20, 20],
            [20, 30, 10,  0,  0, 10, 30, 20]
        ]

    def get_best_move(self, game) -> Optional[Tuple[int, int, int, int]]:
        """
        Get the best move using Minimax with Alpha-Beta pruning
        Returns tuple: (from_row, from_col, to_row, to_col)
        """
        # Get all possible moves for current player (black/AI)
        possible_moves = self.get_all_possible_moves(game)
        
        if not possible_moves:
            return None
            
        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        # Shuffle moves for variety in play
        random.shuffle(possible_moves)
        
        for move in possible_moves:
            from_row, from_col, to_row, to_col = move
            
            # Make the move
            captured_piece = self.make_temporary_move(game, from_row, from_col, to_row, to_col)
            
            # Evaluate the position after this move
            move_value = self.minimax(game, self.depth - 1, alpha, beta, True)  # True = maximizing (white's turn next)
            
            # Undo the move
            self.undo_temporary_move(game, from_row, from_col, to_row, to_col, captured_piece)
            
            if move_value > best_value:
                best_value = move_value
                best_move = move
                
            alpha = max(alpha, move_value)
            if beta <= alpha:
                break  # Alpha-beta pruning
                
        return best_move

    def minimax(self, game, depth: int, alpha: float, beta: float, maximizing_player: bool) -> float:
        """
        Minimax algorithm with alpha-beta pruning
        """
        if depth == 0 or game.game_over:
            return self.evaluate_position(game)
        
        if maximizing_player:  # White's turn
            max_eval = float('-inf')
            possible_moves = self.get_all_possible_moves(game)
            
            for move in possible_moves:
                from_row, from_col, to_row, to_col = move
                captured_piece = self.make_temporary_move(game, from_row, from_col, to_row, to_col)
                
                eval_score = self.minimax(game, depth - 1, alpha, beta, False)
                
                self.undo_temporary_move(game, from_row, from_col, to_row, to_col, captured_piece)
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break  # Beta cutoff
                    
            return max_eval
        else:  # Black's turn (AI)
            min_eval = float('inf')
            possible_moves = self.get_all_possible_moves(game)
            
            for move in possible_moves:
                from_row, from_col, to_row, to_col = move
                captured_piece = self.make_temporary_move(game, from_row, from_col, to_row, to_col)
                
                eval_score = self.minimax(game, depth - 1, alpha, beta, True)
                
                self.undo_temporary_move(game, from_row, from_col, to_row, to_col, captured_piece)
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break  # Alpha cutoff
                    
            return min_eval

    def get_all_possible_moves(self, game) -> List[Tuple[int, int, int, int]]:
        """Get all possible moves for the current player"""
        moves = []
        current_color = game.turn
        
        for row in range(8):
            for col in range(8):
                piece = game.board[row][col]
                if piece and piece[0] == current_color:
                    valid_moves = game.get_valid_moves(row, col)
                    for to_row, to_col in valid_moves:
                        moves.append((row, col, to_row, to_col))
        
        return moves

    def make_temporary_move(self, game, from_row: int, from_col: int, to_row: int, to_col: int):
        """Make a temporary move and return captured piece"""
        captured_piece = game.board[to_row][to_col]
        
        # Store original state
        original_turn = game.turn
        
        # Make the move
        piece = game.board[from_row][from_col]
        game.board[to_row][to_col] = piece
        game.board[from_row][from_col] = ''
        
        # Switch turns
        game.turn = 'w' if game.turn == 'b' else 'b'
        
        return captured_piece

    def undo_temporary_move(self, game, from_row: int, from_col: int, to_row: int, to_col: int, captured_piece):
        """Undo a temporary move"""
        # Move piece back
        piece = game.board[to_row][to_col]
        game.board[from_row][from_col] = piece
        game.board[to_row][to_col] = captured_piece
        
        # Switch turns back
        game.turn = 'w' if game.turn == 'b' else 'b'

    def evaluate_position(self, game) -> float:
        """
        Evaluate the current position
        Positive values favor white, negative values favor black
        """
        if game.game_over:
            if game.winner == 'w':
                return 9999  # White wins
            elif game.winner == 'b':
                return -9999  # Black wins
            else:
                return 0  # Draw
        
        score = 0
        
        for row in range(8):
            for col in range(8):
                piece = game.board[row][col]
                if piece:
                    piece_color = piece[0]
                    piece_type = piece[1]
                    
                    # Basic piece value
                    piece_value = self.piece_values.get(piece_type, 0)
                    
                    # Add positional bonus
                    positional_bonus = self.get_positional_bonus(piece_type, row, col, piece_color)
                    
                    total_value = piece_value + positional_bonus
                    
                    if piece_color == 'w':
                        score += total_value
                    else:
                        score -= total_value
        
        # Add mobility (number of possible moves)
        white_moves = len(self.get_moves_for_color(game, 'w'))
        black_moves = len(self.get_moves_for_color(game, 'b'))
        score += (white_moves - black_moves) * 10
        
        # Add king safety bonus
        score += self.evaluate_king_safety(game, 'w') - self.evaluate_king_safety(game, 'b')
        
        return score

    def get_positional_bonus(self, piece_type: str, row: int, col: int, color: str) -> float:
        """Get positional bonus for a piece"""
        # Flip the table for black pieces
        if color == 'b':
            row = 7 - row
            
        if piece_type == 'p':
            return self.pawn_table[row][col]
        elif piece_type == 'n':
            return self.knight_table[row][col]
        elif piece_type == 'b':
            return self.bishop_table[row][col]
        elif piece_type == 'r':
            return self.rook_table[row][col]
        elif piece_type == 'q':
            return self.queen_table[row][col]
        elif piece_type == 'k':
            return self.king_table[row][col]
        
        return 0

    def get_moves_for_color(self, game, color: str) -> List[Tuple[int, int, int, int]]:
        """Get all possible moves for a specific color"""
        moves = []
        original_turn = game.turn
        game.turn = color
        
        for row in range(8):
            for col in range(8):
                piece = game.board[row][col]
                if piece and piece[0] == color:
                    valid_moves = game.get_valid_moves(row, col)
                    for to_row, to_col in valid_moves:
                        moves.append((row, col, to_row, to_col))
        
        game.turn = original_turn
        return moves

    def evaluate_king_safety(self, game, color: str) -> float:
        """Evaluate king safety"""
        king_pos = game.find_king_position(color)
        if not king_pos:
            return -1000  # King not found (should not happen)
        
        safety_score = 0
        king_row, king_col = king_pos
        
        # Check for pieces defending the king
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = king_row + dr, king_col + dc
                if 0 <= r < 8 and 0 <= c < 8:
                    piece = game.board[r][c]
                    if piece and piece[0] == color:
                        safety_score += 10  # Friendly piece near king
        
        # Penalty for exposed king
        if game.is_king_in_check(color):
            safety_score -= 50
            
        return safety_score