#Zijie Zhang, Sep.24/2023

import pygame
from sys import exit
import numpy as np
import itertools
from reversi import reversi
import socket   
import pickle
import threading

RECV_EVENT_WAITING = -1
RECV_EVENT_END = -2
RECV_EVENT_PLAYER1 = 0
RECV_EVENT_PLAYER2 = 1
RECV_EVENT_NOT_STARTED = -3

class server:
    def __init__(self, host = '127.0.0.1', port = 33333) -> None:
        self.server_socket = socket.socket()
        try:
            self.server_socket.bind((host, port))
        except socket.error as e:
            print(str(e))
        self.server_socket.listen()
        self.player = [None, None]
        self.player_addr = [None, None]
        self.recv_event = RECV_EVENT_WAITING
        self.recv_cords = [-1, -1]

    def wait_for_players(self) -> None:
        self.player[0], self.player_addr[0] = self.server_socket.accept()
        self.player[1], self.player_addr[1] = self.server_socket.accept()

    def request_play(self, turn, board : np.ndarray, _player = 0):
        package = pickle.dumps([turn, board])
        self.player[_player].send(package)
    
    def close(self):
        self.player[0].close()
        self.player[1].close()

class drawable_reversi(reversi):
    def __init__(self,  _white_pic, _black_pic) -> None:
        super().__init__()
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.white_pic = _white_pic
        self.black_pic = _black_pic

    def render_text(self, _screen, _text, x, y, color = (255,255,255)):
        text = self.font.render(_text, True, color)
        text_rect = text.get_rect()
        text_rect.center = (x, y)
        _screen.fill((0,0,0), text_rect)
        _screen.blit(text, text_rect)


    def render(self, _screen) -> None:

        if self.white_count > 0:
            white_cords = np.c_[np.where(self.board == 1)] * 100 + 15
            white_pics = list(zip(itertools.repeat(self.white_pic, white_cords.shape[0]), tuple(map(tuple, white_cords))))
            _screen.blits(white_pics)

        if self.black_count > 0:
            black_cords = np.c_[np.where(self.board == -1)] * 100 + 15
            black_pics = list(zip(itertools.repeat(self.black_pic, black_cords.shape[0]), tuple(map(tuple, black_cords))))
            _screen.blits(black_pics)
            
        self.render_text(_screen, f'White : {self.white_count}', 1000, 100)
        self.render_text(_screen, f'Black : {self.black_count}', 1000, 200)
        self.render_text(_screen, f'Hand : {"White" if self.turn == 1 else "Black"}', 1000,500)
        self.render_text(_screen, f'Time : {self.time}', 1000,600, (255,255,255) if self.time <= 5 else (255, 0, 0))
        self.time += 1

def player_handler(_server : server, _player):
    while True:
        if _server.recv_event == RECV_EVENT_END:
            return
        try:
            _server.recv_cords = pickle.loads(_server.player[_player].recv(4096))
        except ConnectionAbortedError:
            return 
        except EOFError:
            return
        _server.recv_event = _player

def main():

    pygame.init()
    screen = pygame.display.set_mode((1200,800))
    pygame.display.set_caption('Runner')
    clock = pygame.time.Clock()

    background_surface = pygame.image.load('data/background.jpeg')
    background_surface = pygame.transform.scale(background_surface, (800,800))

    white_piece = pygame.image.load('data/white_piece.png')
    white_piece = pygame.transform.scale(white_piece, (70,70))
    black_piece = pygame.image.load('data/black_piece.png')
    black_piece = pygame.transform.scale(black_piece, (70,70))
    game = drawable_reversi(white_piece, black_piece)

    game.render_text(screen, 'Waiting for Players...', 600, 400)
    pygame.display.update()

    game_server = server()
    game_server.wait_for_players()

    p1thread = threading.Thread(target = player_handler, args = (game_server, 0))
    p2thread = threading.Thread(target = player_handler, args = (game_server, 1))
    p1thread.start()
    p2thread.start()

    screen.blit(background_surface,(0,0))
    for i in range(7):
        pygame.draw.line(screen, (255,255,255), (100*i + 100, 0), (100*i + 100, 800), 2)
        pygame.draw.line(screen, (255,255,255), (0, 100*i + 100), (800, 100*i + 100), 2)
    game.render(screen)

    pygame.display.update()

    escape_flag = False
    while True:
        if escape_flag:
            break
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                escape_flag = True

    game_server.request_play(game.turn, game.board, 0 if game.turn == 1 else 1)
    endFlag = False
    game.time = 0
    while True: 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if game_server.recv_event >= 0:
            x, y = game_server.recv_cords
            if x == -1 and y == -1:
                if endFlag:
                    break
                else:
                    endFlag = True
                    game.turn = -game.turn
                    game.time = 0
            else:
                if game.step(x, y, game.turn) >= 0:
                    game.turn = -game.turn
                    game.time = 0
                    endFlag = False
            game_server.recv_event = RECV_EVENT_WAITING
            game_server.request_play(game.turn, game.board, 0 if game.turn == 1 else 1)

        screen.blit(background_surface,(0,0))
        for i in range(7):
            pygame.draw.line(screen, (255,255,255), (100*i + 100, 0), (100*i + 100, 800), 2)
            pygame.draw.line(screen, (255,255,255), (0, 100*i + 100), (800, 100*i + 100), 2)
        game.render(screen)

        pygame.display.update()
        clock.tick(5) # Clock Tick

    game_server.request_play(0, game.board, 0)
    game_server.request_play(0, game.board, 1)
    game_server.close()
    p1thread.join()
    p2thread.join()

    escape_flag = False
    while True:
        if escape_flag:
            break
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                escape_flag = True


if __name__ == '__main__':
    main()

