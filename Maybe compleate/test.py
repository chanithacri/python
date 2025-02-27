import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (127, 255 ,212)
RED = (255, 0, 0)

# Game variables
BIRD_WIDTH = 40
BIRD_HEIGHT = 30
PIPE_WIDTH = 60
PIPE_GAP = 200
GRAVITY = 0.5
JUMP_HEIGHT = 10

# Fonts
TITLE_FONT = pygame.font.Font(None, 64)
MENU_FONT = pygame.font.Font(None, 36)

class Bird:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0

    def jump(self):
        self.velocity = -JUMP_HEIGHT

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def draw(self):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, BIRD_WIDTH, BIRD_HEIGHT))

class Pipe:
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.height = random.randint(100, SCREEN_HEIGHT - PIPE_GAP - 100)
        self.passed = False

    def update(self):
        self.x -= 5

    def draw(self):
        pygame.draw.rect(screen, BLUE, (self.x, 0, PIPE_WIDTH, self.height))
        pygame.draw.rect(screen, BLUE, (self.x, self.height + PIPE_GAP, PIPE_WIDTH, SCREEN_HEIGHT))

def game_over(bird, pipes):
    if bird.y <= 0 or bird.y + BIRD_HEIGHT >= SCREEN_HEIGHT:
        return True

    for pipe in pipes:
        if (bird.x < pipe.x + PIPE_WIDTH and
            bird.x + BIRD_WIDTH > pipe.x and
            (bird.y < pipe.height or
             bird.y + BIRD_HEIGHT > pipe.height + PIPE_GAP)):
            return True
    return False

def start_screen():
    screen.fill(BLACK)
    title = TITLE_FONT.render('Flappy Bird', True, WHITE)
    start_text = MENU_FONT.render('Press SPACE to Start', True, WHITE)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//2 - 100))
    screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True

def game_over_screen(score):
    screen.fill(BLACK)
    game_over_text = TITLE_FONT.render('Game Over', True, RED)
    score_text = MENU_FONT.render(f'Score: {score}', True, WHITE)
    restart_text = MENU_FONT.render('Press SPACE to Restart', True, WHITE)

    screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 150))
    screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2))
    screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 100))
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True

def main():
    while True:
        # Start screen
        if not start_screen():
            break

        clock = pygame.time.Clock()
        bird = Bird()
        pipes = []
        score = 0
        font = pygame.font.Font(None, 36)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        bird.jump()

            # Add new pipes
            if len(pipes) == 0 or pipes[-1].x < SCREEN_WIDTH - 250:
                pipes.append(Pipe())

            # Update bird and pipes
            bird.update()
            for pipe in pipes:
                pipe.update()
                if pipe.x + PIPE_WIDTH < 0:
                    pipes.remove(pipe)

                # Score tracking
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    score += 1

            # Check for game over
            if game_over(bird, pipes):
                if not game_over_screen(score):
                    return
                break

            # Drawing
            screen.fill(BLACK)
            bird.draw()
            for pipe in pipes:
                pipe.draw()

            # Display score
            score_text = font.render(f'Score: {score}', True, WHITE)
            screen.blit(score_text, (10, 10))

            pygame.display.update()
            clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()