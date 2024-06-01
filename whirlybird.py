import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Game settings
GRAVITY = 0.5
JUMP_STRENGTH = -10
PLATFORM_SPEED = 3
PLATFORM_WIDTH = 70
PLATFORM_HEIGHT = 20
PLATFORM_FREQUENCY = 80  # Higher is less frequent

# Load images
BIRD_IMAGE = pygame.image.load('bird.png')
PLATFORM_IMAGE = pygame.image.load('platform.png')
BACKGROUND_IMAGE = pygame.image.load('background.png')

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Whirlybird Game")

# Clock object to control the frame rate
clock = pygame.time.Clock()

# Bird class
class Bird:
    def __init__(self):
        self.image = BIRD_IMAGE
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0

    def jump(self):
        self.velocity = JUMP_STRENGTH

    def move(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return self.image.get_rect(topleft=(self.x, self.y))

# Platform class
class Platform:
    def __init__(self, x, y):
        self.image = PLATFORM_IMAGE
        self.x = x
        self.y = y

    def move(self):
        self.y += PLATFORM_SPEED

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        return self.image.get_rect(topleft=(self.x, self.y))

def draw_background():
    screen.blit(BACKGROUND_IMAGE, (0, 0))

def check_collision(bird, platforms):
    bird_rect = bird.get_rect()
    for platform in platforms:
        if bird_rect.colliderect(platform.get_rect()) and bird.velocity > 0:
            return True
    if bird.y > SCREEN_HEIGHT:
        return True
    return False

def main():
    bird = Bird()
    platforms = [Platform(random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH), i * PLATFORM_FREQUENCY) for i in range(10)]
    score = 0
    running = True

    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()

        bird.move()

        for platform in platforms:
            platform.move()
            if platform.y > SCREEN_HEIGHT:
                platforms.remove(platform)
                platforms.append(Platform(random.randint(0, SCREEN_WIDTH - PLATFORM_WIDTH), -PLATFORM_HEIGHT))
                score += 1

        if check_collision(bird, platforms):
            running = False

        draw_background()
        bird.draw()
        for platform in platforms:
            platform.draw()

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
