import pygame
import random

# Initialize Pygame
pygame.init()

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Define game window dimensions
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
PLAY_WIDTH = 300  # Dimensions of the playing area
PLAY_HEIGHT = 600
BLOCK_SIZE = 30  # Size of a single block

# Create the game window
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Tetris")

# Define the shapes of the Tetromino pieces
S_SHAPE = [['.....',
            '.....',
            '..00.',
            '.00..',
            '.....'],
           ['.....',
            '..0..',
            '..00.',
            '...0.',
            '.....']]

Z_SHAPE = [['.....',
            '.....',
            '.00..',
            '..00.',
            '.....'],
           ['.....',
            '..0..',
            '.00..',
            '.0...',
            '.....']]

I_SHAPE = [['.....',
            '.....',
            '0000.',
            '.....',
            '.....'],
           ['.....',
            '..0..',
            '..0..',
            '..0..',
            '..0..']]

O_SHAPE = [['.....',
            '.....',
            '.00..',
            '.00..',
            '.....']]

J_SHAPE = [['.....',
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

L_SHAPE = [['.....',
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

T_SHAPE = [['.....',
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

SHAPES = [S_SHAPE, Z_SHAPE, I_SHAPE, O_SHAPE, J_SHAPE, L_SHAPE, T_SHAPE]

# Create a function to draw the game grid
def draw_grid():
    for x in range(0, WINDOW_WIDTH, BLOCK_SIZE):
        for y in range(0, WINDOW_HEIGHT, BLOCK_SIZE):
            rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(window, GRAY, rect, 1)

    pygame.draw.rect(window, WHITE, (WINDOW_WIDTH // 2 - PLAY_WIDTH // 2, 0, PLAY_WIDTH, PLAY_HEIGHT), 5)

# Create a function to draw a tetromino piece
def draw_piece(piece, row, col):
    for i, line in enumerate(piece):
        for j, block in enumerate(line):
            if block == '0':
                pygame.draw.rect(window, BLACK, (col * BLOCK_SIZE + WINDOW_WIDTH // 2 - PLAY_WIDTH // 2 + j * BLOCK_SIZE,
                                                 row * BLOCK_SIZE + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

# Main game loop
def main():
    # Set up the initial game state
    current_piece = random.choice(SHAPES)
    next_piece = random.choice(SHAPES)
    piece_row, piece_col = 0, PLAY_WIDTH // 2 // BLOCK_SIZE
    clockwise, counter_clockwise = 0, len(current_piece)

    # Game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    piece_col -= 1
                elif event.key == pygame.K_RIGHT:
                    piece_col += 1
                elif event.key == pygame.K_DOWN:
                    piece_row += 1
                elif event.key == pygame.K_UP:
                    current_piece = [line[:] for line in current_piece[counter_clockwise:]] + \
                                    [line[:] for line in current_piece[:counter_clockwise]]
                    counter_clockwise = (counter_clockwise - 1) % len(current_piece)
                    clockwise = (clockwise + 1) % len(current_piece)

        # Clear the window
        window.fill(BLACK)

        # Draw the game grid
        draw_grid()

        # Draw the current piece
        draw_piece(current_piece, piece_row, piece_col)

        # Update the display
        pygame.display.update()

    # Quit Pygame
    pygame.quit()

# Run the game
if __name__ == "__main__":
    main()