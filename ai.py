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
        # King table for endgame (when fewer pieces are on the board)
        self.king_table_endgame = [
            [-50,-40,-30,-20,-20,-30,-40,-50],
            [-30,-20,-10,  0,  0,-10,-20,-30],
            [-30,-10, 20, 30, 30, 20,-10,-30],
            [-30,-10, 30, 40, 40, 30,-10,-30],
            [-30,-10, 30, 40, 40, 30,-10,-30],
            [-30,-10, 20, 30, 30, 20,-10,-30],
            [-30,-20,-10,  0,  0,-10,-20,-30],
            [-50,-40,-30,-20,-20,-30,-40,-50]
        ]


    def get_best_move(self, game_copy) -> Optional[Tuple[int, int, int, int]]:
        """
        Get the best move using Minimax with Alpha-Beta pruning
        Operates on 'game_copy', which is a deep copy of the actual game state.
        Returns tuple: (from_row, from_col, to_row, to_col)
        """
        # Ensure 'game_copy' is a valid ChessGame object
        if not hasattr(game_copy, 'board') or not hasattr(game_copy, 'turn'):
            print("Error: game_copy object is not a valid ChessGame instance.")
            return None

        # Get all possible moves for current player (black/AI)
        # It's important that get_all_possible_moves also operates on game_copy
        possible_moves = self.get_all_possible_moves(game_copy)
        
        if not possible_moves:
            return None
            
        best_move = None
        # Initialize best_value based on AI's turn (black is minimizing in our minimax structure)
        # So we're looking for the move that leads to the lowest score (most negative for black)
        best_value = float('inf') 
        alpha = float('-inf')
        beta = float('inf')
        
        # Shuffle moves for variety in play and to avoid always picking the same move
        # if multiple moves lead to the same evaluation.
        random.shuffle(possible_moves)
        
        for move_info in possible_moves:
            from_row, from_col, to_row, to_col, promotion_piece = move_info # Now includes promotion piece
            
            # Create a temporary state for the move and capture
            # We will use this to restore the game_copy's state
            temp_state = self._store_temp_state(game_copy)
            
            # Make the move on the game_copy
            # Pass promotion_piece if it's a pawn move to the 8th rank
            self._make_move_on_copy(game_copy, from_row, from_col, to_row, to_col, promotion_piece)
            
            # Evaluate the position after this move.
            # The AI (black) is the minimizing player at the top level search.
            # So, after AI makes a move, it's White's turn, which is maximizing.
            move_value = self.minimax(game_copy, self.depth - 1, alpha, beta, True)  # True = maximizing (white's turn next)
            
            # Undo the move to restore game_copy to its state before the loop iteration
            self._restore_temp_state(game_copy, temp_state)
            
            # Since AI is minimizing (Black), we want the move that results in the lowest score
            if move_value < best_value:
                best_value = move_value
                best_move = (from_row, from_col, to_row, to_col) # Only return the move coordinates
            
            beta = min(beta, move_value) # AI is minimizing, so update beta
            if beta <= alpha:
                break  # Alpha-beta pruning
                
        return best_move

    def minimax(self, game_copy, depth: int, alpha: float, beta: float, maximizing_player: bool) -> float:
        """
        Minimax algorithm with alpha-beta pruning
        Operates on 'game_copy'
        """
        # Base case: depth is 0 or game is over
        if depth == 0 or game_copy.game_over:
            return self.evaluate_position(game_copy)
        
        # Get all possible moves for the current player in the search tree
        possible_moves = self.get_all_possible_moves(game_copy)

        # Handle checkmate/stalemate scenarios if no moves are found
        if not possible_moves:
            if game_copy.is_king_in_check(game_copy.turn):
                # Checkmate: current player is in check and has no legal moves
                return float('-inf') if maximizing_player else float('inf') # Lose for current player
            else:
                # Stalemate: current player is not in check but has no legal moves
                return 0 # Draw
        
        if maximizing_player:  # White's turn (evaluates towards positive infinity)
            max_eval = float('-inf')
            
            for move_info in possible_moves:
                from_row, from_col, to_row, to_col, promotion_piece = move_info
                
                temp_state = self._store_temp_state(game_copy) # Store state before making move
                self._make_move_on_copy(game_copy, from_row, from_col, to_row, to_col, promotion_piece)
                
                eval_score = self.minimax(game_copy, depth - 1, alpha, beta, False) # Next is minimizing player
                
                self._restore_temp_state(game_copy, temp_state) # Restore state after evaluation
                
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                
                if beta <= alpha:
                    break  # Beta cutoff
                    
            return max_eval
        else:  # Black's turn (AI, evaluates towards negative infinity)
            min_eval = float('inf')
            
            for move_info in possible_moves:
                from_row, from_col, to_row, to_col, promotion_piece = move_info
                
                temp_state = self._store_temp_state(game_copy) # Store state before making move
                self._make_move_on_copy(game_copy, from_row, from_col, to_row, to_col, promotion_piece)
                
                eval_score = self.minimax(game_copy, depth - 1, alpha, beta, True) # Next is maximizing player
                
                self._restore_temp_state(game_copy, temp_state) # Restore state after evaluation
                
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                
                if beta <= alpha:
                    break  # Alpha cutoff
                    
            return min_eval

    def get_all_possible_moves(self, game_copy) -> List[Tuple[int, int, int, int, Optional[str]]]:
        """
        Get all possible legal moves for the current player in game_copy.
        Returns a list of tuples: (from_row, from_col, to_row, to_col, promotion_piece)
        """
        moves = []
        current_color = game_copy.turn
        
        for row in range(8):
            for col in range(8):
                piece_info = game_copy.board[row][col] # piece_info should be like "wp", "bn", etc.
                if piece_info and piece_info[0] == current_color:
                    # Temporarily set selected_piece on the game_copy for get_valid_moves
                    original_selected_piece = game_copy.selected_piece
                    original_valid_moves = game_copy.valid_moves # Store current valid_moves
                    
                    game_copy.selected_piece = (row, col)
                    
                    try:
                        valid_destinations = game_copy.get_valid_moves(row, col) # This uses game_copy.selected_piece internally
                        
                        for to_row, to_col in valid_destinations:
                            # Handle pawn promotion: if a pawn reaches the last rank, add all promotion options
                            is_pawn_promotion = False
                            if piece_info[1] == 'p': # Check if it's a pawn
                                if (current_color == 'w' and to_row == 0) or \
                                   (current_color == 'b' and to_row == 7):
                                    is_pawn_promotion = True
                                    for promo_type in ['q', 'r', 'b', 'n']: # Queen, Rook, Bishop, Knight
                                        moves.append((row, col, to_row, to_col, promo_type))
                            
                            if not is_pawn_promotion:
                                moves.append((row, col, to_row, to_col, None)) # No promotion
                                
                    except (IndexError, AttributeError, TypeError) as e:
                        # Skip this piece if there's an error getting valid moves
                        # This can happen if a 'Piece' object is expected but None is encountered
                        # Or if get_valid_moves has an issue with the temp state
                        # print(f"Warning: Error getting moves for piece at ({row}, {col}) with color {current_color}: {e}")
                        continue
                    finally:
                        # Restore original state of selected_piece and valid_moves
                        game_copy.selected_piece = original_selected_piece
                        game_copy.valid_moves = original_valid_moves # Restore valid_moves

        return moves

    def _store_temp_state(self, game_copy):
        """
        Stores necessary parts of the game_copy's state before a temporary move.
        This is a more robust way than just returning the captured piece.
        """
        return {
            'board': copy.deepcopy(game_copy.board), # Deep copy the board
            'turn': game_copy.turn,
            'en_passant_target': game_copy.en_passant_target,
            'castling_rights': copy.deepcopy(game_copy.castling_rights),
            'halfmove_clock': game_copy.halfmove_clock,
            'fullmove_number': game_copy.fullmove_number,
            'last_move': game_copy.last_move if hasattr(game_copy, 'last_move') else None # Store last_move if it exists
        }

    def _restore_temp_state(self, game_copy, temp_state):
        """
        Restores the game_copy's state from the stored temporary state.
        """
        game_copy.board = temp_state['board']
        game_copy.turn = temp_state['turn']
        game_copy.en_passant_target = temp_state['en_passant_target']
        game_copy.castling_rights = temp_state['castling_rights']
        game_copy.halfmove_clock = temp_state['halfmove_clock']
        game_copy.fullmove_number = temp_state['fullmove_number']
        if hasattr(game_copy, 'last_move'):
            game_copy.last_move = temp_state['last_move']

    def _make_move_on_copy(self, game_copy, from_row: int, from_col: int, to_row: int, to_col: int, promotion_piece: Optional[str]):
        """
        Makes a move directly on the 'game_copy' board and updates its state.
        Handles captures, pawn promotion, castling, and en passant.
        This replaces make_temporary_move and part of undo_temporary_move.
        This method needs to mirror the logic in your ChessGame.move_piece.
        """
        piece_moved = game_copy.board[from_row][from_col]
        if not piece_moved:
            return # Should not happen if get_all_possible_moves is correct

        piece_type = piece_moved[1]
        piece_color = piece_moved[0]
        
        # Reset en passant target
        game_copy.en_passant_target = None
        
        # Handle pawn specific moves:
        # 1. En Passant Capture
        if piece_type == 'p' and (to_row, to_col) == game_copy.en_passant_target:
            # Determine captured pawn's position
            captured_pawn_row = from_row if piece_color == 'b' else to_row + 1 # if black pawn moved down, capture row is one above to_row
            captured_pawn_col = to_col
            game_copy.board[captured_pawn_row][captured_pawn_col] = '' # Remove captured pawn
        
        # 2. Pawn Promotion
        if piece_type == 'p' and (to_row == 0 or to_row == 7): # Reached promotion rank
            # Promote the pawn (promotion_piece should be passed, default to queen)
            game_copy.board[to_row][to_col] = piece_color + (promotion_piece if promotion_piece else 'q')
            game_copy.board[from_row][from_col] = ''
            return # Move handled
            
        # 3. Two-square pawn advance (set en passant target)
        if piece_type == 'p' and abs(from_row - to_row) == 2:
            game_copy.en_passant_target = (from_row + (1 if piece_color == 'w' else -1), to_col)

        # Handle Castling
        if piece_type == 'k' and abs(from_col - to_col) == 2: # King moved two squares
            # Determine if it's kingside or queenside castling
            if to_col > from_col: # Kingside
                rook_from_col, rook_to_col = 7, 5
            else: # Queenside
                rook_from_col, rook_to_col = 0, 3
            
            # Move the rook
            rook_piece = game_copy.board[from_row][rook_from_col]
            game_copy.board[from_row][rook_to_col] = rook_piece
            game_copy.board[from_row][rook_from_col] = ''

        # Normal piece move (including captures)
        game_copy.board[to_row][to_col] = piece_moved
        game_copy.board[from_row][from_col] = ''

        # Update castling rights (simple approach)
        if piece_type == 'k':
            game_copy.castling_rights[piece_color + 'K'] = False
            game_copy.castling_rights[piece_color + 'Q'] = False
        elif piece_type == 'r':
            if from_col == 0: # Queenside rook
                game_copy.castling_rights[piece_color + 'Q'] = False
            elif from_col == 7: # Kingside rook
                game_copy.castling_rights[piece_color + 'K'] = False
        # If a rook is captured on its original square, castling rights might also change
        # This is more complex and depends on how your `move_piece` handles it.
        # For simplicity, if a piece is moved *to* a rook's starting square, disable that castling.
        if (to_row, to_col) == (0, 0): game_copy.castling_rights['bQ'] = False
        if (to_row, to_col) == (0, 7): game_copy.castling_rights['bK'] = False
        if (to_row, to_col) == (7, 0): game_copy.castling_rights['wQ'] = False
        if (to_row, to_col) == (7, 7): game_copy.castling_rights['wK'] = False


        # Update halfmove clock (for fifty-move rule and draws)
        if game_copy.board[to_row][to_col] != '' or piece_type == 'p': # Capture or pawn move resets halfmove clock
            game_copy.halfmove_clock = 0
        else:
            game_copy.halfmove_clock += 1

        # Update fullmove number
        if piece_color == 'b':
            game_copy.fullmove_number += 1

        # Switch turn
        game_copy.turn = 'w' if game_copy.turn == 'b' else 'b'

        # Check for game over conditions (checkmate/stalemate) after the move
        # This requires `is_king_in_check` and `get_all_legal_moves` for the *new* turn.
        # It's better to delegate this to the ChessGame class if possible.
        # For now, we'll keep it simple for the AI's internal logic.
        
        # NOTE: The check for checkmate/stalemate needs to be robust here.
        # You need a function in ChessGame (or logic here) to determine if the *current*
        # player (whose turn it now is) has any legal moves.
        # If game_copy.get_all_possible_moves(game_copy) for the new turn returns empty,
        # then it's either stalemate or checkmate.
        
        # This part of the logic might be redundant if your evaluate_position
        # already handles `game.game_over`. But it's good for ensuring the
        # internal game_copy state correctly reflects game_over.

        # Temporarily check for game_over and winner after the move
        opponent_color = 'b' if piece_color == 'w' else 'w'
        if game_copy.is_king_in_check(game_copy.turn):
            # Check if current player (whose turn it is) has any legal moves to get out of check
            # This requires a function like `game_copy.get_all_legal_moves_considering_check()`
            # For simplicity, if get_all_possible_moves for the current player is empty
            # and they are in check, it's a checkmate.
            if not self.get_all_possible_moves(game_copy): # Recursive call to get moves for the new turn
                game_copy.game_over = True
                game_copy.winner = opponent_color # The player who just moved is the winner
        elif not self.get_all_possible_moves(game_copy):
            # Stalemate: Current player is not in check but has no legal moves
            game_copy.game_over = True
            game_copy.winner = 'draw'
        
        # Check fifty-move rule
        if game_copy.halfmove_clock >= 100: # 50 full moves = 100 half moves
            game_copy.game_over = True
            game_copy.winner = 'draw'


    def evaluate_position(self, game_copy) -> float:
        """
        Evaluate the current position.
        Positive values favor white, negative values favor black.
        """
        if game_copy.game_over:
            if game_copy.winner == 'w':
                return 1000000  # White wins, large positive score
            elif game_copy.winner == 'b':
                return -1000000  # Black wins, large negative score
            else:
                return 0  # Draw
        
        score = 0
        
        # Determine if we are in endgame phase (simple heuristic: less than 4 minor/major pieces each)
        num_major_minor_pieces = 0
        for row in range(8):
            for col in range(8):
                piece_info = game_copy.board[row][col]
                if piece_info:
                    piece_type = piece_info[1]
                    if piece_type in ['n', 'b', 'r', 'q']:
                        num_major_minor_pieces += 1
        
        is_endgame = num_major_minor_pieces < 8 # Heuristic: if less than 8 rooks/queens/knights/bishops

        for row in range(8):
            for col in range(8):
                piece_info = game_copy.board[row][col]
                if piece_info:
                    piece_color = piece_info[0]
                    piece_type = piece_info[1]
                    
                    # Basic piece value
                    piece_value = self.piece_values.get(piece_type, 0)
                    
                    # Add positional bonus
                    # Use different king table for endgame
                    current_king_table = self.king_table_endgame if is_endgame else self.king_table
                    positional_bonus = self.get_positional_bonus(piece_type, row, col, piece_color, current_king_table)
                    
                    total_value = piece_value + positional_bonus
                    
                    if piece_color == 'w':
                        score += total_value
                    else: # Black
                        score -= total_value
        
        # Add mobility (number of possible moves) - promotes active pieces
        # Ensure get_moves_for_color correctly uses game_copy
        try:
            # Temporarily change game_copy.turn to get moves for each side
            original_turn = game_copy.turn 
            game_copy.turn = 'w'
            white_moves = len(self.get_all_possible_moves(game_copy))
            
            game_copy.turn = 'b'
            black_moves = len(self.get_all_possible_moves(game_copy))
            game_copy.turn = original_turn # Restore original turn
            
            score += (white_moves - black_moves) * 10 # White mobility is good, black mobility is bad
        except Exception as e:
            # print(f"Error calculating mobility: {e}") # Suppress for performance, but useful for debug
            pass
        
        # Add king safety bonus
        try:
            # Need to pass the correct game_copy for the current state being evaluated
            score += self.evaluate_king_safety(game_copy, 'w') - self.evaluate_king_safety(game_copy, 'b')
        except Exception as e:
            # print(f"Error evaluating king safety: {e}") # Suppress for performance, but useful for debug
            pass
        
        return score

    def get_positional_bonus(self, piece_type: str, row: int, col: int, color: str, king_table_override=None) -> float:
        """Get positional bonus for a piece"""
        # Flip the table for black pieces
        if color == 'b':
            row_idx = 7 - row
            col_idx = 7 - col # Also flip column for symmetry (e.g. knight on b8 and g8 are symmetric)
        else:
            row_idx = row
            col_idx = col
            
        if piece_type == 'p':
            return self.pawn_table[row_idx][col_idx]
        elif piece_type == 'n':
            return self.knight_table[row_idx][col_idx]
        elif piece_type == 'b':
            return self.bishop_table[row_idx][col_idx]
        elif piece_type == 'r':
            return self.rook_table[row_idx][col_idx]
        elif piece_type == 'q':
            return self.queen_table[row_idx][col_idx]
        elif piece_type == 'k':
            # Use override if provided (for endgame king table)
            return (king_table_override if king_table_override else self.king_table)[row_idx][col_idx]
        
        return 0

    def evaluate_king_safety(self, game_copy, color: str) -> float:
        """
        Evaluate king safety for a given color.
        Assumes game_copy has a find_king_position and is_king_in_check method.
        """
        try:
            king_pos = game_copy.find_king_position(color)
            if not king_pos:
                return -100000  # King not found (this would indicate a severe error or game over)
            
            safety_score = 0
            king_row, king_col = king_pos
            
            # Bonus for pieces defending the king (pawns and pieces on adjacent squares)
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    r, c = king_row + dr, king_col + dc
                    if 0 <= r < 8 and 0 <= c < 8:
                        piece_info = game_copy.board[r][c]
                        if piece_info and piece_info[0] == color:
                            # Higher bonus for pawns defending, as they are crucial for king safety
                            if piece_info[1] == 'p':
                                safety_score += 15
                            else:
                                safety_score += 5  # Other friendly pieces near king
            
            # Penalty for king being in check
            if game_copy.is_king_in_check(color):
                safety_score -= 100 # Significant penalty for being in check
            
            # Further penalties based on exposed king position (e.g., no pawn shield)
            # This would require more sophisticated logic, checking pawns in front of the king.
            # For example: check if the pawn in front of the king on ranks 1 or 6 is missing or moved.
            
            return safety_score
        except Exception as e:
            # print(f"Error evaluating king safety for {color}: {e}") # Suppress for performance
            return 0