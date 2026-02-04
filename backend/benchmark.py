import ai_engine as ai
import numpy as np
import time

# CONFIGURATION
GAMES_TO_PLAY = 20
PLAYER_1_DEPTH = 1  # The "Dumb" Player (Red)
PLAYER_2_DEPTH = 4  # The "Smart" Player (Yellow)

def play_match(game_id):
    board = ai.create_board()
    game_over = False
    turn = ai.PLAYER # Player 1 starts
    
    # Statistics
    moves_count = 0
    start_time = time.time()
    
    while not game_over:
        if turn == ai.PLAYER:
            # Player 1 (Red) - Low Depth
            col, score = ai.minimax(board, PLAYER_1_DEPTH, -float('inf'), float('inf'), True)
            piece = ai.PLAYER
        else:
            # Player 2 (Yellow) - High Depth
            col, score = ai.minimax(board, PLAYER_2_DEPTH, -float('inf'), float('inf'), True)
            piece = ai.AI

        if col is None: # Draw or Error
            return "Draw", moves_count
            
        row = ai.get_next_open_row(board, int(col))
        ai.drop_piece(board, row, int(col), piece)
        moves_count += 1
        
        if ai.winning_move(board, piece):
            return ("Player 1 (Red)" if piece == ai.PLAYER else "Player 2 (Yellow)"), moves_count
            
        # Switch turns
        turn = ai.PLAYER if turn == ai.AI else ai.AI
        
        # Check for draw (full board)
        if len(ai.get_valid_locations(board)) == 0:
            return "Draw", moves_count

print(f"--- STARTING BENCHMARK: {GAMES_TO_PLAY} GAMES ---")
print(f"Player 1 (Red) Depth: {PLAYER_1_DEPTH}")
print(f"Player 2 (Yellow) Depth: {PLAYER_2_DEPTH}")
print("-" * 40)

p1_wins = 0
p2_wins = 0
draws = 0
total_moves = 0

for i in range(GAMES_TO_PLAY):
    winner, moves = play_match(i+1)
    total_moves += moves
    
    if "Red" in winner: p1_wins += 1
    elif "Yellow" in winner: p2_wins += 1
    else: draws += 1
    
    # Progress Bar
    print(f"Game {i+1}/{GAMES_TO_PLAY}: Winner = {winner} ({moves} moves)")

print("\n" + "="*40)
print("FINAL RESULTS")
print("="*40)
print(f"Player 1 (Depth {PLAYER_1_DEPTH}) Wins: {p1_wins} ({(p1_wins/GAMES_TO_PLAY)*100}%)")
print(f"Player 2 (Depth {PLAYER_2_DEPTH}) Wins: {p2_wins} ({(p2_wins/GAMES_TO_PLAY)*100}%)")
print(f"Draws: {draws}")
print(f"Avg Moves per Game: {total_moves/GAMES_TO_PLAY}")
print("="*40)