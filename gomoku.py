import pygame
import sys
import socket
import pickle
import tkinter as tk
from tkinter import simpledialog

# Definice konstant
SCREEN_SIZE = 600
GRID_SIZE = 15
CELL_SIZE = SCREEN_SIZE // GRID_SIZE

# Barvy
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Velikosti fontu
DEFAULT_FONT_SIZE = 36
WINNER_FONT_SIZE = 60

class Player:
    def __init__(self, symbol, color):
        self.symbol = symbol
        self.color = color

class Gomoku:
    def __init__(self):
        self.board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.players = [Player('X', RED), Player('O', BLUE)]
        self.current_player = self.players[0]
        self.winner = None

    def switch_player(self):
        self.current_player = self.players[1] if self.current_player == self.players[0] else self.players[0]

    def make_move(self, row, col):
        if self.board[row][col] == 0 and not self.winner:
            self.board[row][col] = self.current_player.symbol
            if self.check_win(row, col):
                self.winner = self.current_player
            else:
                self.switch_player()

    def check_win(self, row, col):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            for i in range(1, 5):
                r, c = row + i * dr, col + i * dc
                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and self.board[r][c] == self.current_player.symbol:
                    count += 1
                else:
                    break
            for i in range(1, 5):
                r, c = row - i * dr, col - i * dc
                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and self.board[r][c] == self.current_player.symbol:
                    count += 1
                else:
                    break
            if count >= 5:
                return True
        return False

class GomokuSetup:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Skryje hlavní okno Tkinteru

    def get_server_info(self):
        host = simpledialog.askstring("Server Info", "Zadejte IP adresu kamaráda:")
        port = simpledialog.askinteger("Server Info", "Zadejte port pro připojení:")
        return host, port

class GomokuGame:
    def __init__(self):
        self.gomoku = Gomoku()
        self.initialize_pygame()
        self.server_info = GomokuSetup().get_server_info()
        self.host, self.port = self.server_info
        self.server_socket = None
        self.client_socket = None

    def initialize_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        pygame.display.set_caption('Gomoku')
        self.clock = pygame.time.Clock()

    def draw_board(self):
        self.screen.fill(WHITE)
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                pygame.draw.rect(self.screen, BLACK, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
                symbol = self.gomoku.board[row][col]
                if symbol != 0:
                    font_size = WINNER_FONT_SIZE if self.gomoku.winner else DEFAULT_FONT_SIZE
                    font = pygame.font.Font(None, font_size)
                    text_color = self.gomoku.players[0].color if symbol == self.gomoku.players[0].symbol else self.gomoku.players[1].color
                    text = font.render(symbol, True, text_color)
                    text_rect = text.get_rect(center=(col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2))
                    self.screen.blit(text, text_rect.move(-1, -2))  # Upraveno umístění symbolů

    def run_game(self):
        self.setup_network()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    col = event.pos[0] // CELL_SIZE
                    row = event.pos[1] // CELL_SIZE
                    self.gomoku.make_move(row, col)
                    self.send_data((row, col))

            self.draw_board()
            if self.gomoku.winner:
                font_size = WINNER_FONT_SIZE
                font = pygame.font.Font(None, font_size)
                text = font.render(f"Player {self.gomoku.winner.symbol} wins!", True, BLACK)
                self.screen.blit(text, (SCREEN_SIZE // 2 - 200, SCREEN_SIZE // 2 - 37))
            pygame.display.flip()
            self.clock.tick(30)

    def setup_network(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_socket.connect((self.host, self.port))
            print(f"Připojeno na server {self.host}:{self.port}")
        except socket.error as e:
            print(f"Nelze se připojit na server: {e}")
            sys.exit(1)

    def send_data(self, data):
        try:
            serialized_data = pickle.dumps(data)
            self.server_socket.send(serialized_data)
        except socket.error as e:
            print(f"Chyba při odesílání dat: {e}")

if __name__ == "__main__":
    game = GomokuGame()
    game.run_game()
