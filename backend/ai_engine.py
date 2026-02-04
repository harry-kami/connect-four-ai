import numpy as np
import math

# --- CONSTANTS ---
ROWS = 6
COLS = 7
PLAYER = 1      # The Human (Red)
AI = 2          # The Computer (Yellow)
EMPTY = 0
WINDOW_LENGTH = 4

# --- BOARD HELPER FUNCTIONS ---

def create_board():
    """Creates a 6x7 matrix of zeros using NumPy."""
    return np.zeros((ROWS, COLS))

def is_valid_location(board, col):
    """Checks if the top row of the selected column is empty."""
    return board[ROWS-1][col] == 0

def get_next_open_row(board, col):
    """Finds the first empty slot in the column (from bottom up)."""
    for r in range(ROWS):
        if board[r][col] == 0:
            return r

def drop_piece(board, row, col, piece):
    """Updates the board matrix with the player's piece."""
    board[row][col] = piece

def winning_move(board, piece):
    """
    Scans the board for 4 connected pieces (Horizontal, Vertical, Diagonal).
    Returns True if 'piece' has won.
    """
    # Check Horizontal
    for c in range(COLS-3):
        for r in range(ROWS):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    # Check Vertical
    for c in range(COLS):
        for r in range(ROWS-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
    # Check Positive Diagonals (/)
    for c in range(COLS-3):
        for r in range(ROWS-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True
    # Check Negative Diagonals (\)
    for c in range(COLS-3):
        for r in range(3, ROWS):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True
    return False

# --- HEURISTIC ENGINE (The "Gut Feeling") ---

def evaluate_window(window, piece):
    """
    Scores a specific 4-slot window based on piece count.
    Used to estimate the value of non-terminal states.
    """
    score = 0
    opp_piece = PLAYER if piece == AI else AI

    # --- OFFENSIVE SCORING ---
    if window.count(piece) == 4:
        score += 10000            # Win
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 10               # Strong threat
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 5                # Developing line

    # --- DEFENSIVE SCORING ---
    # CRITICAL: If opponent has 3 and an empty slot, we MUST block.
    # The penalty is huge (-8000) to force the AI to prioritize this over building its own +5 lines.
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 8000 

    return score

def score_position(board, piece):
    """
    Scans the entire board window-by-window and sums up the heuristic score.
    """
    score = 0
    
    # 1. Center Column Preference (Strategy)
    # Control of the center is vital in Connect 4. We give it raw bonus points.
    center_array = [int(i) for i in list(board[:, COLS//2])]
    center_count = center_array.count(piece)
    score += center_count * 6

    # 2. Score Horizontal Windows
    for r in range(ROWS):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLS-3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # 3. Score Vertical Windows
    for c in range(COLS):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROWS-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # 4. Score Positive Diagonals
    for r in range(ROWS-3):
        for c in range(COLS-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # 5. Score Negative Diagonals
    for r in range(ROWS-3):
        for c in range(COLS-3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

# --- OPTIMIZATION HELPERS ---

def get_valid_locations(board):
    """Returns a list of columns that are not full."""
    valid_locations = []
    for col in range(COLS):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

# --- THE MINIMAX ALGORITHM ---

def minimax(board, depth, alpha, beta, maximizingPlayer):
    """
    Recursive Minimax with Alpha-Beta Pruning.
    Optimized with Move Ordering (Center-First).
    """
    valid_locations = get_valid_locations(board)
    
    # Check for Terminal States (Win/Loss/Draw)
    is_terminal = winning_move(board, PLAYER) or winning_move(board, AI) or len(valid_locations) == 0
    
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI):
                return (None, 100000000000000) # AI Wins
            elif winning_move(board, PLAYER):
                return (None, -10000000000000) # Human Wins
            else: 
                return (None, 0) # Draw
        else: # Depth is zero (Heuristic evaluation)
            return (None, score_position(board, AI))

    # --- MOVE ORDERING OPTIMIZATION ---
    # We sort the possible moves so that the AI checks the CENTER columns first.
    # Center columns are statistically more likely to be "good" moves.
    # Finding a "good" move early allows Alpha-Beta to prune bad branches faster.
    center = COLS // 2
    # Sorts valid_locations based on distance from center (ascending)
    # Example order: [3, 2, 4, 1, 5, 0, 6]
    valid_locations.sort(key=lambda x: abs(x - center))

    if maximizingPlayer:
        value = -math.inf
        column = valid_locations[0]
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI)
            
            # Recurse
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            
            if new_score > value:
                value = new_score
                column = col
            
            # Alpha-Beta Pruning
            alpha = max(alpha, value)
            if alpha >= beta:
                break # Prune this branch
        return column, value

    else: # Minimizing Player (Simulating Human)
        value = math.inf
        column = valid_locations[0]
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER)
            
            # Recurse
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            
            if new_score < value:
                value = new_score
                column = col
            
            # Alpha-Beta Pruning
            beta = min(beta, value)
            if alpha >= beta:
                break # Prune this branch
        return column, value