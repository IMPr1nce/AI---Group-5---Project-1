#Zijie Zhang, Sep.24/2023

import numpy as np

class reversi:
    def __init__(self) -> None:
        self.board = np.zeros([8,8])

        self.board[3,4] = -1
        self.board[3,3] = 1
        self.board[4,3] = -1
        self.board[4,4] = 1
        self.white_count = 2
        self.black_count = 2
        self.directions = [
            [1,1],
            [1,0],
            [1,-1],
            [0,1],
            [0,-1],
            [-1,1],
            [-1,0],
            [-1,-1]
        ]

        self.time = 0
        self.turn = 1

    def step(self, x, y, piece = 1, commit = True) -> int:

        #Piece already exists
        if self.board[x,y] != 0:
            return -1
        
        #Out of bound
        elif x < 0 or x > 7 or y < 0 or y > 7:
            return -2
        
        else:
            fliped = 0
            for direction in self.directions:
                dx, dy = direction
                cursor_x, cursor_y = x + dx, y + dy
                flip_list = []
                while 0 <= cursor_x <=7 and 0 <= cursor_y <=7:
                    if self.board[cursor_x, cursor_y] == 0:
                        break
                    elif self.board[cursor_x, cursor_y] == piece:
                        if len(flip_list) == 0:
                            break
                        else:
                            for cord in flip_list:
                                if commit:
                                    self.board[*cord] = piece
                                fliped += 1
                            break
                    else:
                        flip_list.append([cursor_x, cursor_y])
                        cursor_x, cursor_y = cursor_x + dx, cursor_y + dy

            #Illegal Move
            if fliped == 0:
                return -3
            else:
                if commit:
                    self.board[x,y] = piece
                    if piece == 1:
                        self.white_count += 1
                    else:
                        self.black_count += 1
                    self.white_count += fliped * piece
                    self.black_count -= fliped * piece
                return fliped