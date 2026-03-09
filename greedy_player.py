#Zijie Zhang, Sep.24/2023

import numpy as np
import socket, pickle
from reversi import reversi

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

        #Local Greedy - Replace with your algorithm
        x = -1
        y = -1
        max = 0
        game.board = board
        for i in range(8):
            for j in range(8):
                cur = game.step(i, j, turn, False)
                if cur > max:
                    max = cur
                    x, y = i, j

        #Send your move to the server. Send (x,y) = (-1,-1) to tell the server you have no hand to play
        game_socket.send(pickle.dumps([x,y]))
        
if __name__ == '__main__':
    main()