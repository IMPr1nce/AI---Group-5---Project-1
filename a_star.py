#Zijie Zhang, Sep.24/2023

import numpy as np
import socket, pickle
from reversi import reversi
import heapq

class Node:
    def __init__(self, board_state, player, g=0, h=0, parent=None):
        self.board_state = board_state
        self.player = player
        self.g = g
        self.h = h
        self.f = g + h
        self.parent = parent

    def __lt__(self, other):
        return self.f < other.f

# Constants
CORNERS = [(0,0), (0, 7), (7, 0), (7, 7)]
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
        print("I am playing as", "WHITE" if turn == 1 else "BLACK")
        #Turn = 0 indicates game ended
        if turn == 0:
            game_socket.close()
            return
        
        #Debug info
        print(turn)
        print(board)

        def heuristic(board,root_player):
            h = board_score(board, root_player)
            return h
        def A_star(start_board, player, depth, root_player):

            open_list = []
            heapq.heapify(open_list)

            start_node = Node(start_board, player, g=0,
                            h=board_score(start_board, root_player))

            heapq.heappush(open_list, start_node)

            best_score = float('-inf')

            while open_list:

                current = heapq.heappop(open_list)

                # Stop at depth limit
                if current.g >= depth:
                    score = board_score(current.board_state, root_player)
                    best_score = max(best_score, score)
                    continue

                moves = find_available_moves(current.board_state, current.player)

                # No moves available
                if not moves:
                    score = board_score(current.board_state, root_player)
                    best_score = max(best_score, score)
                    continue

                for move in moves:

                    new_board = use_turn(current.board_state, move, current.player)

                    next_player = -current.player

                    g = current.g + 1
                    h = board_score(new_board, root_player)

                    child = Node(new_board, next_player, g, h, current)

                    heapq.heappush(open_list, child)

            return best_score

            
        
        
        # Create vars
        x = -1
        y = -1
        best_root_score = float('-inf')
        
        # Find legal moves for top of tree
        moves = find_available_moves(board, turn)
        
        # Decide tree depth
        depth = 6

        for move in moves:
            new_board = use_turn(board, move, turn)

            score = A_star(new_board, -turn, depth-1, turn)

            if score > best_root_score:
                best_root_score = score
                x, y = move

        #Send your move to the server. Send (x,y) = (-1,-1) to tell the server you have no hand to play
        game_socket.send(pickle.dumps([x,y]))
        
if __name__ == '__main__':
    main()




