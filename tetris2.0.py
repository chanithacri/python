import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
GRID_SIZE = 30
BOARD_WIDTH = SCREEN_WIDTH // GRID_SIZE
BOARD_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),  # Cyan
    (0, 0, 255),    # Blue
    (255, 165, 0),  # Orange
    (255, 255, 0),  # Yellow
    (0, 255, 0),    # Green
    (128, 0, 128),  # Purple
    (255, 0, 0)     # Red
]

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1],     # I
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0]],

    [[1, 1, 1],        # T
    [0, 1, 0],
    [0, 0, 0]],

    [[0, 1, 1],        # S
    [1, 1, 0],
    [0, 0, 0]],

    [[1, 1, 0],        # Z
    [0, 1, 1],
    [0, 0, 0]],

    [[1, 1],           # O
    [1, 1]],

    [[1, 1, 1],        # L
    [1, 0, 0],
    [0, 0, 0]],

    [[1, 1, 1],        # J
    [0, 0, 1],
    [0, 0, 0]]
]

# Rotate function for shapes
def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

# Clock object to control the frame rate
clock = pygame.time.Clock()

class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = random.choice(COLORS)
        self.rotation = 0

    def rotate(self):
        self.rotation = (self.rotation + 1) % 4
        self.shape = rotate(self.shape)

    def get_cells(self):
        cells = []
        for i, row in enumerate(self.shape):
            for j, val in enumerate(row):
                if val:
                    cells.append((self.x + j, self.y + i))
        return cells

class Tetris:
    def __init__(self):
        self.board = [[BLACK for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.game_over = False

    def new_piece(self):
        shape = random.choice(SHAPES)
        return Piece(BOARD_WIDTH // 2 - len(shape[0]) // 2, 0, shape)

    def rotate_piece(self):
        self.current_piece.rotate()
        if self.check_collision():
            self.current_piece.rotate()
            self.current_piece.rotate()
            self.current_piece.rotate()

    def move_piece(self, dx, dy):
        self.current_piece.x += dx
        self.current_piece.y += dy
        if self.check_collision():
            self.current_piece.x -= dx
            self.current_piece.y -= dy

    def drop_piece(self):
        self.current_piece.y += 1
        if self.check_collision():
            self.current_piece.y -= 1
            self.lock_piece()
            self.clear_lines()
            self.current_piece = self.next_piece
            self.next_piece = self.new_piece()
            if self.check_collision():
                self.game_over = True

    def check_collision(self):
        for x, y in self.current_piece.get_cells():
            if x < 0 or x >= BOARD_WIDTH or y >= BOARD_HEIGHT or self.board[y][x] != BLACK:
                return True
        return False

    def lock_piece(self):
        for x, y in self.current_piece.get_cells():
            self.board[y][x] = self.current_piece.color

    def clear_lines(self):
        lines_to_clear = [i for i, row in enumerate(self.board) if all(cell != BLACK for cell in row)]
        for i in lines_to_clear:
            del self.board[i]
            self.board.insert(0, [BLACK for _ in range(BOARD_WIDTH)])
        self.score += len(lines_to_clear)

    def draw_board(self):
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                pygame.draw.rect(screen, self.board[y][x], (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)
                pygame.draw.rect(screen, GRAY, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

    def draw_piece(self, piece):
        for x, y in piece.get_cells():
            pygame.draw.rect(screen, piece.color, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 0)
            pygame.draw.rect(screen, GRAY, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

def main():
    tetris = Tetris()
    running = True
    fall_time = 0
    fall_speed = 500  # in milliseconds

    while running:
        screen.fill(BLACK)
        tetris.draw_board()
        tetris.draw_piece(tetris.current_piece)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    tetris.move_piece(-1, 0)
                if event.key == pygame.K_RIGHT:
                    tetris.move_piece(1, 0)
                if event.key == pygame.K_DOWN:
                    tetris.drop_piece()
                if event.key == pygame.K_UP:
                    tetris.rotate_piece()

        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time >= fall_speed:
            fall_time = 0
            tetris.drop_piece()

        if tetris.game_over:
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
