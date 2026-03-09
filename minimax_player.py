#Zijie Zhang, Sep.24/2023

import numpy as np
import socket, pickle
from reversi import reversi

# Constants
CORNERS = [(0,0), (0, 7), (7, 0), (7, 7)]


def main():
    game_socket = socket.socket()
    game_socket.connect(('127.0.0.1', 33333))
    game = reversi()

    while True:

        #Receive play request from the server
        #turn : 1 --> you are playing as white | -1 --> you are playing as black
        #board : 8*8 numpy array
        data = game_socket.recv(4096)
        turn, board = pickle.loads(data)

        #Turn = 0 indicates game ended
        if turn == 0:
            game_socket.close()
            return
        
        #Debug info
        print(turn)
        print(board)



        # Minimax - Replace with your algorithm
        """NOTES:
            * 1 = white
            * -1 = black
        """       
        def find_available_moves(current_board: np.ndarray, turn: int) -> list:
            """Return a list of legal moves"""
            temp_board = reversi()
            temp_board.board = current_board
            
            # Find possible legal moves
            moves = []
            for a in range(8):
                for b in range(8):
                    if temp_board.step(a, b, turn, False) > 0:
                        moves.append((a, b)) # Append each possible move as tuple
            return moves
            
        def use_turn(current_board: np.ndarray, move: tuple, turn: int) -> np.ndarray:
            """Return new board copy after making a move"""
            game = reversi() # temp game instance
            
            game.board = np.copy(current_board) # Copy board
            
            # Make Move
            x, y = move
            game.step(x, y, turn, True)
            
            return game.board
            
        def board_score(current_board: np.ndarray, player: int) -> int:
            """Give a score to a board after a move is done"""
            # Score for corners
            corner_score = 0
            for x, y in CORNERS:
                if current_board[x, y] == player:
                    corner_score += 1
                elif current_board[x, y] == (-player):
                    corner_score -= 1
                    
            # Pieces Score
            player_pieces = np.sum(current_board == player)
            opponent_pieces = np.sum(current_board == (-player))
            pieces_score = player_pieces - opponent_pieces # Total pieces score
            
            # Mobility Score (Amount of moves available) for each player
            player_moves = len(find_available_moves(current_board, player))
            opponent_moves = len(find_available_moves(current_board, (-player)))
            mobility_socre = player_moves - opponent_moves # Total mobility score
            
            # Assign multiplier values
            cs_mult = 25 # Corner score multiplier
            ps_mult = 1 # Pieces score multiplier
            ms_mult = 5 # Mobility score multiplier
            # FIXME: Add edges?
            
            total_player_score = (corner_score * cs_mult) + (pieces_score * ps_mult) + (mobility_socre * ms_mult)
            return int(total_player_score)

        def MM_Algorithm(board: np.ndarray, turn: int, depth: int, curr_player: int) -> int:
            """Recursive MM_Algorithm algorithm"""
            legal_moves = find_available_moves(board, turn)
            opponent = -turn
            
            # Depth limit reached
            if depth == 0:
                score = board_score(board, curr_player)
                return score
            
            # No moves
            if len(legal_moves) == 0:
                opponent_moves = find_available_moves(board, opponent)
                
                # Game over (Undo recursion)
                if len(opponent_moves) == 0:
                    score = board_score(board, curr_player)
                    return score
                
                # Skip curr_player's turn
                else:
                    return MM_Algorithm(board, opponent, depth-1, curr_player)
            
            
            # Maximizing player
            if turn == curr_player:
                highest_score = float('-inf')
                
                # Test all moves
                for move in legal_moves:
                    new_board = use_turn(board, move, turn)
                    score = MM_Algorithm(new_board, opponent, depth - 1, curr_player)
                    
                    # Find highest score
                    highest_score = max(highest_score, score)
                return highest_score
            
            # Minimizing player
            else:
                lowest_score = float('inf')
                
                for move in legal_moves:
                    new_board = use_turn(board, move, turn)
                    score = MM_Algorithm(new_board, opponent, depth-1, curr_player)
                    
                    # Find lowest score
                    lowest_score = min(lowest_score, score)
                return lowest_score
        
        
        # Create vars
        x = -1
        y = -1
        best_root_score = float('-inf')
        
        # Find legal moves for top of tree
        moves = find_available_moves(board, turn)
        
        # Decide tree depth
        depth = 3

        for move in moves:
            new_board = use_turn(board, move, turn)
            score = MM_Algorithm(new_board, -turn, depth-1, turn)
            if max(score, best_root_score) == score:
                best_root_score = max(score, best_root_score)
                x, y = move

        #Send your move to the server. Send (x,y) = (-1,-1) to tell the server you have no hand to play
        game_socket.send(pickle.dumps([x,y]))
        
if __name__ == '__main__':
    main()
