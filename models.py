import copy
from constants import SQUARE_SIZE
from animations import Animation, ParticleSystem, CheckmateAnimation
import chess
import chess.engine

class ChessGame:
    def __init__(self, sounds, game_mode="2V2", stockfish_path="stockfish"):
        self.sounds = sounds
        self.game_mode = game_mode  # "2V2" or "AI"
        self.stockfish_path = stockfish_path
        self.engine = None
        self.reset_game()
        if self.game_mode == "AI":
            self.start_engine()

    def start_engine(self):
        try:
            self.engine = chess.engine.SimpleEngine.popen_uci(self.stockfish_path)
        except Exception as e:
            print("Could not start Stockfish:", e)
            self.engine = None

    def close_engine(self):
        if self.engine:
            self.engine.quit()
            self.engine = None

    def get_chess_board(self):
        # Convert your board to FEN
        rows = []
        for row in self.board:
            fen_row = ""
            empty = 0
            for cell in row:
                if cell == "":
                    empty += 1
                else:
                    if empty > 0:
                        fen_row += str(empty)
                        empty = 0
                    piece = cell[1]
                    color = cell[0]
                    symbol = piece.upper() if color == "w" else piece.lower()
                    fen_row += symbol
            if empty > 0:
                fen_row += str(empty)
            rows.append(fen_row)
        fen = "/".join(rows)
        fen += " " + ("w" if self.turn == "w" else "b") + " - - 0 1"
        return chess.Board(fen)

    def make_ai_move(self, time_limit=0.1):
        if not self.engine:
            self.start_engine()
        if not self.engine:
            print("AI move unavailable: Stockfish engine could not be started.\n"
                  "Please ensure the Stockfish binary is present, named 'stockfish', and executable in the project directory.\n"
                  "See the README or setup instructions for help.")
            return
        board = self.get_chess_board()
        try:
            result = self.engine.play(board, chess.engine.Limit(time=time_limit))
            move = result.move
            # Convert move to your coordinates
            start_col = ord(str(move)[0]) - ord('a')
            start_row = 8 - int(str(move)[1])
            end_col = ord(str(move)[2]) - ord('a')
            end_row = 8 - int(str(move)[3])
            self.selected_piece = (start_row, start_col)
            self.move_piece(end_row, end_col)
        except Exception as e:
            print(f"Error during AI move: {e}\n"
                  "Check that Stockfish is working and compatible with your system.")
            return

    def reset_game(self):
        # Initialize board with starting position
        self.board = [
            ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr']
        ]
        
        self.turn = 'w'  # White starts
        self.selected_piece = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None
        self.captured_pieces = {'w': [], 'b': []}
        self.scores = {'w': 0, 'b': 0}
        self.move_history = []
        self.check = {'w': False, 'b': False}
        self.castling_rights = {
            'w': {'king_side': True, 'queen_side': True},
            'b': {'king_side': True, 'queen_side': True}
        }
        self.en_passant_target = None
        self.halfmove_clock = 0  # For 50-move rule
        self.fullmove_number = 1
        self.last_move = None
        
        # Stats tracking
        self.stats = {
            'w': {'captures': 0, 'checks': 0, 'moves': 0},
            'b': {'captures': 0, 'checks': 0, 'moves': 0}
        }
        
        # Animation and effects
        self.current_animation = None
        self.animating_piece = None
        self.particle_systems = []
        
        # Checkmate animation
        self.checkmate_animation = None
        self.showing_checkmate = False
        
        # Player names
        self.player_names = {'w': 'Player 1', 'b': 'Player 2'}
        
        # Game states
        self.game_states = []  # For undo functionality
        self.save_game_state()  # Save initial state
        
        # Play start sound
        self.play_sound("game_start")
    
    def save_game_state(self):
        # Create a deep copy of the current state
        state = {
            'board': copy.deepcopy(self.board),
            'turn': self.turn,
            'captured_pieces': copy.deepcopy(self.captured_pieces),
            'scores': copy.deepcopy(self.scores),
            'move_history': copy.deepcopy(self.move_history),
            'check': copy.deepcopy(self.check),
            'castling_rights': copy.deepcopy(self.castling_rights),
            'en_passant_target': self.en_passant_target,
            'halfmove_clock': self.halfmove_clock,
            'fullmove_number': self.fullmove_number,
            'stats': copy.deepcopy(self.stats)
        }
        self.game_states.append(state)
        
        # Limit history size to prevent memory issues
        if len(self.game_states) > 50:
            self.game_states.pop(0)
    
    def undo_move(self):
        if len(self.game_states) > 1:  # Keep at least the initial state
            self.game_states.pop()  # Remove current state
            prev_state = self.game_states[-1]
            
            # Restore previous state
            self.board = prev_state['board']
            self.turn = prev_state['turn']
            self.captured_pieces = prev_state['captured_pieces']
            self.scores = prev_state['scores']
            self.move_history = prev_state['move_history']
            self.check = prev_state['check']
            self.castling_rights = prev_state['castling_rights']
            self.en_passant_target = prev_state['en_passant_target']
            self.halfmove_clock = prev_state['halfmove_clock']
            self.fullmove_number = prev_state['fullmove_number']
            self.stats = prev_state['stats']
            
            # Clear selection and animations
            self.selected_piece = None
            self.valid_moves = []
            self.current_animation = None
            self.checkmate_animation = None
            
            # Set last move for highlighting
            self.last_move = self.move_history[-1] if self.move_history else None
            
            # Update game over status
            self.game_over = False
            self.winner = None
            self.showing_checkmate = False
            
            return True
        return False
    
    def find_king_position(self, color):
        """Find the position of the king for the given color"""
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == color + 'k':
                    return (row, col)
        return None  # Should not happen in a valid game
    
    def trigger_checkmate_animation(self):
        """Start the checkmate animation"""
        # Find the losing king's position
        color = self.turn  # The current player is in checkmate
        king_pos = self.find_king_position(color)
        
        if king_pos:
            # Create the checkmate animation
            self.checkmate_animation = CheckmateAnimation(king_pos, SQUARE_SIZE)
            self.showing_checkmate = True
            
            # Play checkmate sound
            self.play_sound("game_end")
    
    def is_checkmate(self):
        """
        Check if the current player is in checkmate.
        A player is in checkmate if they're in check and have no legal moves.
        """
        color = self.turn  # Current player's color
        
        # If not in check, can't be checkmate
        if not self.is_king_in_check(color):
            return False
        
        # Check if any move can get out of check
        for start_row in range(8):
            for start_col in range(8):
                piece = self.board[start_row][start_col]
                if piece and piece[0] == color:
                    valid_moves = self.get_valid_moves(start_row, start_col)
                    if valid_moves:
                        return False
        
        # No valid moves to get out of check
        return True
    
    def is_stalemate(self):
        """
        Check if the current player is in stalemate.
        A player is in stalemate if not in check but has no legal moves.
        """
        color = self.turn  # Current player's color
        
        # If in check, not stalemate
        if self.is_king_in_check(color):
            return False
        
        # Check if any legal move exists
        for start_row in range(8):
            for start_col in range(8):
                piece = self.board[start_row][start_col]
                if piece and piece[0] == color:
                    valid_moves = self.get_valid_moves(start_row, start_col)
                    if valid_moves:
                        return False
        
        # No legal moves but not in check = stalemate
        return True
    
    def play_sound(self, sound_name):
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except:
                pass  # Silently fail if sound can't be played
    
    def select_piece(self, row, col):
        if not self.game_over and 0 <= row < 8 and 0 <= col < 8:
            piece = self.board[row][col]
            
            # If selecting a piece of the current player's color
            if piece and piece[0] == self.turn:
                self.selected_piece = (row, col)
                self.valid_moves = self.get_valid_moves(row, col)
                self.play_sound("select")
                return True
            
            # If a piece is already selected and clicking on a valid move
            elif self.selected_piece and (row, col) in self.valid_moves:
                return self.move_piece(row, col)
            
            # Invalid selection
            else:
                if self.selected_piece:  # Deselect if clicking elsewhere
                    self.selected_piece = None
                    self.valid_moves = []
                    self.play_sound("invalid")
                return False
        
        return False
    
    def move_piece(self, row, col):
        if self.selected_piece and (row, col) in self.valid_moves:
            start_row, start_col = self.selected_piece
            piece = self.board[start_row][start_col]
            
            # Create animation
            start_pos = (start_col * SQUARE_SIZE, start_row * SQUARE_SIZE)
            end_pos = (col * SQUARE_SIZE, row * SQUARE_SIZE)
            self.current_animation = Animation(start_pos, end_pos)
            self.animating_piece = piece
            
            # Track if a capture occurred
            capture = False
            
            # If capturing a piece
            if self.board[row][col]:
                captured = self.board[row][col]
                self.captured_pieces[self.turn].append(captured)
                self.update_score(captured)
                capture = True
                
                try:
                    # Add particle effect - safely handle any exceptions
                    from constants import LIGHT_SQUARE, DARK_SQUARE
                    color = LIGHT_SQUARE if captured[0] == 'w' else DARK_SQUARE
                    
                    # Create particle effect
                    particle_pos = (col * SQUARE_SIZE + SQUARE_SIZE//2, row * SQUARE_SIZE + SQUARE_SIZE//2)
                    particle_system = ParticleSystem(particle_pos, color)
                    self.particle_systems.append(particle_system)
                except Exception as e:
                    print(f"Error creating particle effect: {e}")
                    # Continue game even if particle effect fails
                    pass
            
            # Handle castling
            castling = False
            if piece[1] == 'k' and abs(start_col - col) > 1:
                castling = True
                # Move the rook too
                if col > start_col:  # King-side castle
                    self.board[row][col-1] = self.board[row][7]  # Move rook
                    self.board[row][7] = ''  # Remove rook from starting position
                else:  # Queen-side castle
                    self.board[row][col+1] = self.board[row][0]  # Move rook
                    self.board[row][0] = ''  # Remove rook from starting position
            
            # Handle en passant capture
            en_passant_capture = False
            if piece[1] == 'p' and start_col != col and not self.board[row][col]:
                # En passant capture
                self.board[start_row][col] = ''  # Remove the captured pawn
                captured = 'bp' if self.turn == 'w' else 'wp'
                self.captured_pieces[self.turn].append(captured)
                self.update_score(captured)
                capture = True
                en_passant_capture = True
                
                try:
                    # Add particle effect for en passant capture
                    from constants import LIGHT_SQUARE, DARK_SQUARE
                    color = LIGHT_SQUARE if captured[0] == 'w' else DARK_SQUARE
                    
                    # Create particle effect at the captured pawn's position
                    particle_pos = (col * SQUARE_SIZE + SQUARE_SIZE//2, start_row * SQUARE_SIZE + SQUARE_SIZE//2)
                    particle_system = ParticleSystem(particle_pos, color)
                    self.particle_systems.append(particle_system)
                except Exception as e:
                    print(f"Error creating en passant particle effect: {e}")
                    # Continue game even if particle effect fails
                    pass
            
            # Update en passant target square
            self.en_passant_target = None
            if piece[1] == 'p' and abs(start_row - row) == 2:
                # Set en passant target for next move
                self.en_passant_target = (row, col)
            
            # Update castling rights
            if piece[1] == 'k':
                self.castling_rights[self.turn]['king_side'] = False
                self.castling_rights[self.turn]['queen_side'] = False
            elif piece[1] == 'r':
                if start_col == 0:  # Queen-side rook
                    self.castling_rights[self.turn]['queen_side'] = False
                elif start_col == 7:  # King-side rook
                    self.castling_rights[self.turn]['king_side'] = False
            
            # Move the piece
            self.board[row][col] = piece
            self.board[start_row][start_col] = ''
            
            # Check for pawn promotion (simplified - always promotes to queen)
            promotion = False
            if piece[1] == 'p' and (row == 0 or row == 7):
                self.board[row][col] = piece[0] + 'q'  # Promote to queen
                promotion = True
                self.play_sound("promote")
            
            # Record move in algebraic notation
            move_notation = self.get_move_notation(start_row, start_col, row, col, capture, castling, promotion, en_passant_capture)
            
            # Update move history
            self.move_history.append((start_row, start_col, row, col, piece, move_notation))
            self.last_move = (start_row, start_col, row, col)
            
            # Update half-move clock (for 50-move rule)
            if piece[1] == 'p' or capture:
                self.halfmove_clock = 0
            else:
                self.halfmove_clock += 1
            
            # Update full-move number
            if self.turn == 'b':
                self.fullmove_number += 1
            
            # Update statistics
            self.stats[self.turn]['moves'] += 1
            if capture:
                self.stats[self.turn]['captures'] += 1
            
            # Play appropriate sound
            if castling:
                self.play_sound("castle")
            elif capture:
                self.play_sound("capture")
            else:
                self.play_sound("move")
            
            # Switch turns
            self.turn = 'b' if self.turn == 'w' else 'w'
            
            # Check for checks and checkmate
            self.check = {'w': False, 'b': False}
            if self.is_king_in_check('w'):
                self.check['w'] = True
                self.stats['b' if self.turn == 'w' else 'w']['checks'] += 1
                self.play_sound("check")
            
            if self.is_king_in_check('b'):
                self.check['b'] = True
                self.stats['w' if self.turn == 'b' else 'b']['checks'] += 1
                self.play_sound("check")
            
            # Check for checkmate or stalemate
            if self.is_checkmate():
                self.game_over = True
                self.winner = 'w' if self.turn == 'b' else 'b'
                # Trigger checkmate animation
                self.trigger_checkmate_animation()
            elif self.is_stalemate():
                self.game_over = True
                self.play_sound("game_end")
            
            # Save game state for undo
            self.save_game_state()
            
            # Clear selection
            self.selected_piece = None
            self.valid_moves = []
            return True
        
        return False
    
    def get_move_notation(self, start_row, start_col, end_row, end_col, capture, castling, promotion, en_passant):
        if castling:
            return "O-O" if end_col > start_col else "O-O-O"
        
        piece = self.board[end_row][end_col]
        piece_letter = piece[1].upper() if piece[1] != 'p' else ""
        capture_symbol = "x" if capture else ""
        from_square = chr(97 + start_col) + str(8 - start_row)
        to_square = chr(97 + end_col) + str(8 - end_row)
        
        # Add promoted piece
        promotion_suffix = "=Q" if promotion else ""
        
        # Add en passant
        ep_suffix = " e.p." if en_passant else ""
        
        # Check if we need to disambiguate (e.g., if two knights could move to the same square)
        disambig = ""
        if piece[1] != 'p' and piece[1] != 'k':  # Pawns and kings don't need disambiguation
            # Check for other pieces of same type that could move to the same square
            for r in range(8):
                for c in range(8):
                    if (r, c) != (start_row, start_col) and self.board[r][c] == piece:
                        other_piece_moves = self.get_valid_moves(r, c, check_check=False)
                        if (end_row, end_col) in other_piece_moves:
                            # Need disambiguation
                            if c != start_col:
                                disambig = chr(97 + start_col)  # Use file for disambiguation
                            else:
                                disambig = str(8 - start_row)  # Use rank for disambiguation
        
        notation = piece_letter + disambig + capture_symbol + to_square + promotion_suffix + ep_suffix
        
        # Add + for check, # for checkmate
        check_suffix = ""
        if self.is_king_in_check(opponent := 'b' if piece[0] == 'w' else 'w'):
            check_suffix = "#" if self.is_checkmate() else "+"
        
        return notation + check_suffix
    
    def update_score(self, captured_piece):
        # Piece values
        piece_values = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0}
        piece_type = captured_piece[1]
        self.scores[self.turn] += piece_values[piece_type]
    
    def get_valid_moves(self, row, col, check_check=True):
        piece = self.board[row][col]
        if not piece:
            return []
        
        piece_type = piece[1]
        color = piece[0]
        moves = []
        
        # Get all potential moves based on piece type
        if piece_type == 'p':  # Pawn
            moves = self.get_pawn_moves(row, col)
        elif piece_type == 'r':  # Rook
            moves = self.get_rook_moves(row, col)
        elif piece_type == 'n':  # Knight
            moves = self.get_knight_moves(row, col)
        elif piece_type == 'b':  # Bishop
            moves = self.get_bishop_moves(row, col)
        elif piece_type == 'q':  # Queen
            moves = self.get_queen_moves(row, col)
        elif piece_type == 'k':  # King
            moves = self.get_king_moves(row, col)
        
        # Filter moves that would put or leave the king in check
        if check_check:
            valid_moves = []
            for move in moves:
                if not self.would_move_cause_check(row, col, move[0], move[1], color):
                    valid_moves.append(move)
            return valid_moves
        
        return moves
    
    def get_pawn_moves(self, row, col):
        moves = []
        piece = self.board[row][col]
        color = piece[0]
        
        # Direction of pawn movement (white moves up, black moves down)
        direction = -1 if color == 'w' else 1
        
        # Forward one square
        if 0 <= row + direction < 8 and not self.board[row + direction][col]:
            moves.append((row + direction, col))
            
            # First move can be two squares
            if (row == 6 and color == 'w' or row == 1 and color == 'b') and not self.board[row + 2*direction][col]:
                moves.append((row + 2*direction, col))
        
        # Captures (diagonally)
        for dc in [-1, 1]:
            if 0 <= row + direction < 8 and 0 <= col + dc < 8:
                # Normal capture
                if self.board[row + direction][col + dc] and self.board[row + direction][col + dc][0] != color:
                    moves.append((row + direction, col + dc))
                
                # En passant capture
                if self.en_passant_target and (row + direction, col + dc) == self.en_passant_target:
                    moves.append((row + direction, col + dc))
        
        return moves
    
    def get_rook_moves(self, row, col):
        moves = []
        piece = self.board[row][col]
        color = piece[0]
        
        # Rook can move horizontally and vertically
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                r, c = row + dr * i, col + dc * i
                if not (0 <= r < 8 and 0 <= c < 8):
                    break
                
                if not self.board[r][c]:  # Empty square
                    moves.append((r, c))
                else:  # Occupied square
                    if self.board[r][c][0] != color:  # Opponent's piece
                        moves.append((r, c))
                    break  # Can't move further in this direction
        
        return moves
    
    def get_knight_moves(self, row, col):
        moves = []
        piece = self.board[row][col]
        color = piece[0]
        
        # Knight moves in L-shape
        knight_moves = [
            (2, 1), (1, 2), (-1, 2), (-2, 1),
            (-2, -1), (-1, -2), (1, -2), (2, -1)
        ]
        
        for dr, dc in knight_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if not self.board[r][c] or self.board[r][c][0] != color:
                    moves.append((r, c))
        
        return moves
    
    def get_bishop_moves(self, row, col):
        moves = []
        piece = self.board[row][col]
        color = piece[0]
        
        # Bishop moves diagonally
        directions = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
        
        for dr, dc in directions:
            for i in range(1, 8):
                r, c = row + dr * i, col + dc * i
                if not (0 <= r < 8 and 0 <= c < 8):
                    break
                
                if not self.board[r][c]:  # Empty square
                    moves.append((r, c))
                else:  # Occupied square
                    if self.board[r][c][0] != color:  # Opponent's piece
                        moves.append((r, c))
                    break  # Can't move further in this direction
        
        return moves
    
    def get_queen_moves(self, row, col):
        # Queen combines rook and bishop movements
        return self.get_rook_moves(row, col) + self.get_bishop_moves(row, col)
    
    def get_king_moves(self, row, col):
        moves = []
        piece = self.board[row][col]
        color = piece[0]
        
        # King moves one square in any direction
        king_moves = [
            (0, 1), (1, 0), (0, -1), (-1, 0),
            (1, 1), (1, -1), (-1, -1), (-1, 1)
        ]
        
        for dr, dc in king_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8:
                if not self.board[r][c] or self.board[r][c][0] != color:
                    moves.append((r, c))
        
        # Castling
        if not self.is_king_in_check(color):
            # King-side castling
            if self.castling_rights[color]['king_side']:
                if not self.board[row][col+1] and not self.board[row][col+2]:
                    if not self.would_square_be_in_check(row, col+1, color) and not self.would_square_be_in_check(row, col+2, color):
                        moves.append((row, col+2))
            
            # Queen-side castling
            if self.castling_rights[color]['queen_side']:
                if not self.board[row][col-1] and not self.board[row][col-2] and not self.board[row][col-3]:
                    if not self.would_square_be_in_check(row, col-1, color) and not self.would_square_be_in_check(row, col-2, color):
                        moves.append((row, col-2))
        
        return moves
    
    def would_square_be_in_check(self, row, col, color):
        """Check if a square would be under attack by opponent pieces"""
        opponent = 'b' if color == 'w' else 'w'
        
        # Check for attacks by pawns
        pawn_directions = [(-1, -1), (-1, 1)] if color == 'w' else [(1, -1), (1, 1)]
        for dr, dc in pawn_directions:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == opponent + 'p':
                return True
        
        # Check for attacks by knights
        knight_moves = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]
        for dr, dc in knight_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == opponent + 'n':
                return True
        
        # Check for attacks by kings (for adjacent squares)
        king_moves = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, -1), (-1, 1)]
        for dr, dc in king_moves:
            r, c = row + dr, col + dc
            if 0 <= r < 8 and 0 <= c < 8 and self.board[r][c] == opponent + 'k':
                return True
        
        # Check for attacks by bishops, rooks, and queens along lines
        # Diagonal directions (bishop, queen)
        for dr, dc in [(1, 1), (1, -1), (-1, -1), (-1, 1)]:
            for i in range(1, 8):
                r, c = row + dr * i, col + dc * i
                if not (0 <= r < 8 and 0 <= c < 8):
                    break
                
                if self.board[r][c]:
                    if self.board[r][c][0] == opponent and (self.board[r][c][1] == 'b' or self.board[r][c][1] == 'q'):
                        return True
                    break
        
        # Straight directions (rook, queen)
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            for i in range(1, 8):
                r, c = row + dr * i, col + dc * i
                if not (0 <= r < 8 and 0 <= c < 8):
                    break
                
                if self.board[r][c]:
                    if self.board[r][c][0] == opponent and (self.board[r][c][1] == 'r' or self.board[r][c][1] == 'q'):
                        return True
                    break
        
        return False
    
    def is_king_in_check(self, color):
        """Check if the king of the given color is in check"""
        # Find the king
        king_pos = None
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == color + 'k':
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        
        if not king_pos:
            return False  # No king found (shouldn't happen in a real game)
        
        return self.would_square_be_in_check(king_pos[0], king_pos[1], color)
    
    def would_move_cause_check(self, from_row, from_col, to_row, to_col, color):
        """Check if moving a piece would leave or put the king in check"""
        # Make a temporary move
        temp_board = [row[:] for row in self.board]
        temp_piece = temp_board[from_row][from_col]
        temp_board[to_row][to_col] = temp_piece
        temp_board[from_row][from_col] = ''
        
        # Find the king
        king_pos = None
        for r in range(8):
            for c in range(8):
                if temp_board[r][c] == color + 'k':
                    king_pos = (r, c)
                    break
            if king_pos:
                break
        
        if not king_pos:
            return False  # No king found
        
        # Check if king would be in check
        opponent = 'b' if color == 'w' else 'w'
        king_row, king_col = king_pos
        
        # Check for attacks by pawns
        pawn_directions = [(-1, -1), (-1, 1)] if color == 'w' else [(1, -1), (1, 1)]
        for dr, dc in pawn_directions:
            r, c = king_row + dr, king_col + dc
            if 0 <= r < 8 and 0 <= c < 8 and temp_board[r][c] == opponent + 'p':
                return True
        
        # Check for attacks by knights
        knight_moves = [(2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]
        for dr, dc in knight_moves:
            r, c = king_row + dr, king_col + dc
            if 0 <= r < 8 and 0 <= c < 8 and temp_board[r][c] == opponent + 'n':
                return True
        
        # Check for attacks by kings
        king_moves = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, -1), (-1, 1)]
        for dr, dc in king_moves:
            r, c = king_row + dr, king_col + dc
            if 0 <= r < 8 and 0 <= c < 8 and temp_board[r][c] == opponent + 'k':
                return True
        
        # Check for attacks by bishops, rooks, and queens
        # Diagonal directions (bishop, queen)
        for dr, dc in [(1, 1), (1, -1), (-1, -1), (-1, 1)]:
            for i in range(1, 8):
                r, c = king_row + dr * i, king_col + dc * i
                if not (0 <= r < 8 and 0 <= c < 8):
                    break
                
                if temp_board[r][c]:
                    if temp_board[r][c][0] == opponent and (temp_board[r][c][1] == 'b' or temp_board[r][c][1] == 'q'):
                        return True
                    break
        
        # Straight directions (rook, queen)
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            for i in range(1, 8):
                r, c = king_row + dr * i, king_col + dc * i
                if not (0 <= r < 8 and 0 <= c < 8):
                    break
                
                if temp_board[r][c]:
                    if temp_board[r][c][0] == opponent and (temp_board[r][c][1] == 'r' or temp_board[r][c][1] == 'q'):
                        return True
                    break
        
        return False