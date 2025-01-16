import pygame
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 700
PLAY_WIDTH, PLAY_HEIGHT = 300, 600
BLOCK_SIZE = 30

# Top left coordinates of play area
TOP_LEFT_X = (WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = HEIGHT - PLAY_HEIGHT

# Shapes (S, Z, I, O, J, L, T)
S = [['.....',
    '.....',
    '..00.',
    '.00..',
    '.....'],
    ['.....',
    '..0..',
    '..00.',
    '...0.',
    '.....']]

Z = [['.....',
    '.....',
    '.00..',
    '..00.',
    '.....'],
    ['.....',
    '..0..',
    '.00..',
    '.0...',
    '.....']]

I = [['.....',
    '..0..',
    '..0..',
    '..0..',
    '..0..'],
    ['.....',
    '0000.',
    '.....',
    '.....',
    '.....']]

O = [['.....',
    '.....',
    '.00..',
    '.00..',
    '.....']]

J = [['.....',
    '.0...',
    '.000.',
    '.....',
    '.....'],
    ['.....',
    '..00.',
    '..0..',
    '..0..',
    '.....'],
    ['.....',
    '.....',
    '.000.',
    '...0.',
    '.....'],
    ['.....',
    '..0..',
    '..0..',
    '.00..',
    '.....']]

L = [['.....',
    '...0.',
    '.000.',
    '.....',
    '.....'],
    ['.....',
    '..0..',
    '..0..',
    '..00.',
    '.....'],
    ['.....',
    '.....',
    '.000.',
    '.0...',
    '.....'],
    ['.....',
    '.00..',
    '..0..',
    '..0..',
    '.....']]

T = [['.....',
    '..0..',
    '.000.',
    '.....',
    '.....'],
    ['.....',
    '..0..',
    '..00.',
    '..0..',
    '.....'],
    ['.....',
    '.....',
    '.000.',
    '..0..',
    '.....'],
    ['.....',
    '..0..',
    '.00..',
    '..0..',
    '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (0, 0, 255), (255, 165, 0), (128, 0, 128)]

# Shape class
class Shape:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0

def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if (x, y) in locked_positions:
                color = locked_positions[(x, y)]
                grid[y][x] = color
    return grid

def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))
    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)
    return positions

def valid_space(shape, grid):
    accepted_positions = [[(x, y) for x in range(10) if grid[y][x] == (0, 0, 0)] for y in range(20)]
    accepted_positions = [x for sub in accepted_positions for x in sub]
    formatted = convert_shape_format(shape)
    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def get_shape():
    return Shape(5, 0, random.choice(shapes))

def draw_text_middle(text, size, color, surface):
    font = pygame.font.Font(None, size)
    label = font.render(text, 1, color)
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - (label.get_width() / 2), 
                        TOP_LEFT_Y + PLAY_HEIGHT / 2 - (label.get_height() / 2)))

def draw_grid(surface, grid):
    for y in range(len(grid)):
        pygame.draw.line(surface, (128, 128, 128), (TOP_LEFT_X, TOP_LEFT_Y + y * BLOCK_SIZE), 
                        (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + y * BLOCK_SIZE))
        for x in range(len(grid[y])):
            pygame.draw.line(surface, (128, 128, 128), (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y), 
                            (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT))

def clear_rows(grid, locked):
    increment = 0
    for y in range(len(grid)-1, -1, -1):
        row = grid[y]
        if (0, 0, 0) not in row:
            increment += 1
            ind = y
            for x in range(len(row)):
                try:
                    del locked[(x, y)]
                except:
                    continue
    if increment > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + increment)
                locked[newKey] = locked.pop(key)
    return increment

def draw_next_shape(shape, surface):
    font = pygame.font.Font(None, 30)
    label = font.render('Next Shape', 1, (255, 255, 255))
    start_x = TOP_LEFT_X + PLAY_WIDTH + 50
    start_y = TOP_LEFT_Y + PLAY_HEIGHT / 2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, 
                                (start_x + j * BLOCK_SIZE, start_y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    surface.blit(label, (start_x + 10, start_y - 30))

def draw_window(surface, grid, score=0):
    surface.fill((0, 0, 0))
    pygame.font.init()
    font = pygame.font.Font(None, 60)
    label = font.render('Tetris', 1, (255, 255, 255))
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - (label.get_width() / 2), 30))
    font = pygame.font.Font(None, 30)
    label = font.render(f'Score: {score}', 1, (255, 255, 255))
    start_x = TOP_LEFT_X + PLAY_WIDTH + 50
    start_y = TOP_LEFT_Y + PLAY_HEIGHT / 2 - 100
    surface.blit(label, (start_x + 20, start_y + 160))
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            pygame.draw.rect(surface, grid[y][x], 
                            (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    draw_grid(surface, grid)
    pygame.draw.rect(surface, (255, 0, 0), 
                    (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 5)

def main():
    locked_positions = {}
    grid = create_grid(locked_positions)
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    score = 0

    move_left_time = 0
    move_right_time = 0
    move_down_time = 0

    while run:
        grid = create_grid(locked_positions)
        fall_speed = 0.27
        fall_time += clock.get_rawtime()
        move_left_time += clock.get_rawtime()
        move_right_time += clock.get_rawtime()
        move_down_time += clock.get_rawtime()
        clock.tick()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            if move_left_time > 100:  # move left every 100 milliseconds
                current_piece.x -= 1
                if not valid_space(current_piece, grid):
                    current_piece.x += 1
                move_left_time = 0

        if keys[pygame.K_RIGHT]:
            if move_right_time > 100:  # move right every 100 milliseconds
                current_piece.x += 1
                if not valid_space(current_piece, grid):
                    current_piece.x -= 1
                move_right_time = 0

        if keys[pygame.K_DOWN]:
            if move_down_time > 100:  # move down every 100 milliseconds
                current_piece.y += 1
                if not valid_space(current_piece, grid):
                    current_piece.y -= 1
                move_down_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)

        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                change_piece = True

        shape_pos = convert_shape_format(current_piece)

        for pos in shape_pos:
            x, y = pos
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10

        draw_window(win, grid, score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        if check_lost(locked_positions):
            run = False

    draw_text_middle("You Lost", 80, (255, 255, 255), win)
    pygame.display.update()
    pygame.time.delay(2000)

def main_menu():
    run = True
    while run:
        win.fill((0, 0, 0))
        draw_text_middle('Press Any Key To Play', 60, (255, 255, 255), win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main()
    pygame.display.quit()

win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Tetris')

main_menu()
