import pygame
import random

# Initialize pygame
pygame.init()

# Set up some constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
BLOCK_SIZE = 20
FPS = 60

# Set up some colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Set up the game board
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

# Set up the Tetriminos
TETRIMINOS = [
    [[1, 1],
     [1, 1]],  # O
    [[1, 1, 1, 1]],  # I
    [[1, 0, 0],
     [1, 1, 1]],  # J
    [[0, 0, 1],
     [1, 1, 1]],  # L
    [[1, 1, 0],
     [0, 1, 1]],  # S
    [[0, 1, 1],
     [1, 1, 0]],  # Z
    [[1],
     [1],
     [1],
     [1]]  # T
]

class Tetrimino:
    def __init__(self):
        self.type = random.randint(0, len(TETRIMINOS) - 1)
        self.offset_x = 0
        self.offset_y = 0
        self.rotation = 0

    def get_shape(self):
        return TETRIMINOS[self.type]

    def rotate(self):
        self.rotation = (self.rotation + 1) % 4

    def move_left(self):
        self.offset_x -= 1

    def move_right(self):
        self.offset_x += 1

    def move_down(self):
        self.offset_y += 1

    def get_position(self):
        return (self.offset_x, self.offset_y)

def draw_board(screen, board):
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            color = WHITE if board[y][x] == 0 else RED
            pygame.draw.rect(screen, color, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

def draw_tetrimino(screen, tetrimino):
    shape = tetrimino.get_shape()
    for y in range(len(shape)):
        for x in range(len(shape[y])):
            if shape[y][x] == 1:
                pygame.draw.rect(screen, RED, (((x + tetrimino.offset_x) * BLOCK_SIZE), ((y + tetrimino.offset_y) * BLOCK_SIZE), BLOCK_SIZE, BLOCK_SIZE), 0)

def check_collision(board, tetrimino):
    shape = tetrimino.get_shape()
    for y in range(len(shape)):
        for x in range(len(shape[y])):
            if shape[y][x] == 1:
                if x + tetrimino.offset_x < 0 or x + tetrimino.offset_x >= BOARD_WIDTH or y + tetrimino.offset_y < 0 or y + tetrimino.offset_y >= BOARD_HEIGHT:
                    return True
                if board[y + tetrimino.offset_y][x + tetrimino.offset_x] == 1:
                    return True
    return False

def update_board(board, tetrimino):
    shape = tetrimino.get_shape()
    for y in range(len(shape)):
        for x in range(len(shape[y])):
            if shape[y][x] == 1:
                board[y + tetrimino.offset_y][x + tetrimino.offset_x] = 1

def check_lines(board):
    lines = []
    for y in range(BOARD_HEIGHT):
        if all([cell == 1 for cell in board[y]]):
            lines.append(y)
    return lines

def remove_lines(board, lines):
    for line in lines:
        board.pop(line)
        board.insert(0, [0 for _ in range(BOARD_WIDTH)])

def game_loop():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    tetrimino = Tetrimino()
    score = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    tetrimino.move_left()
                elif event.key == pygame.K_RIGHT:
                    tetrimino.move_right()
                elif event.key == pygame.K_DOWN:
                    tetrimino.move_down()
                elif event.key == pygame.K_UP:
                    tetrimino.rotate()

        screen.fill(BLACK)

        if check_collision(board, tetrimino):
            update_board(board, tetrimino)
            tetrimino = Tetrimino()
            lines = check_lines(board)
            if lines:
                remove_lines(board, lines)
                score += len(lines)

        draw_board(screen, board)
        draw_tetrimino(screen, tetrimino)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    game_loop()
