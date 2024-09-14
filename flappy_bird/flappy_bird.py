import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

# Create the window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird by ChatGPT')

# Game variables
GRAVITY = 0.5
BIRD_JUMP = -10
PIPE_SPEED = 3
PIPE_GAP = 150

# Load images
bird_image = pygame.Surface((34, 24))
bird_image.fill((255, 255, 0))  # Yellow bird

pipe_width = 52
pipe_height = SCREEN_HEIGHT
pipe_image = pygame.Surface((pipe_width, pipe_height))
pipe_image.fill((0, 255, 0))  # Green pipes

# Fonts
font = pygame.font.SysFont('Arial', 32)

class Bird:
    """Class representing the bird."""
    def __init__(self):
        self.image = bird_image
        self.rect = self.image.get_rect()
        self.rect.center = (50, SCREEN_HEIGHT // 2)
        self.velocity = 0

    def update(self):
        """Update the bird's position."""
        self.velocity += GRAVITY
        self.rect.y += int(self.velocity)

    def jump(self):
        """Make the bird jump."""
        self.velocity = BIRD_JUMP

    def draw(self, surface):
        """Draw the bird on the screen."""
        surface.blit(self.image, self.rect)

class Pipe:
    """Class representing a pipe."""
    def __init__(self, x, y, flipped):
        self.image = pipe_image
        self.rect = self.image.get_rect()
        if flipped:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = (x, y - PIPE_GAP // 2)
        else:
            self.rect.topleft = (x, y + PIPE_GAP // 2)

    def update(self):
        """Move the pipe to the left."""
        self.rect.x -= PIPE_SPEED

    def draw(self, surface):
        """Draw the pipe on the screen."""
        surface.blit(self.image, self.rect)

def check_collision(bird, pipes):
    """Check for collision between the bird and pipes."""
    for pipe in pipes:
        if bird.rect.colliderect(pipe.rect):
            return True
    if bird.rect.top <= 0 or bird.rect.bottom >= SCREEN_HEIGHT:
        return True
    return False

def display_text(surface, text, x, y):
    """Display text on the screen."""
    label = font.render(text, True, (255, 255, 255))
    surface.blit(label, (x, y))

def main():
    """Main game loop."""
    clock = pygame.time.Clock()
    bird = Bird()
    pipes = []
    pipe_timer = 0
    score = 0

    running = True
    while running:
        clock.tick(60)  # 60 FPS

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()

        # Update bird
        bird.update()

        # Update pipes
        pipe_timer += 1
        if pipe_timer > 90:
            pipe_y = random.randint(100, SCREEN_HEIGHT - 100)
            top_pipe = Pipe(SCREEN_WIDTH, pipe_y, True)
            bottom_pipe = Pipe(SCREEN_WIDTH, pipe_y, False)
            pipes.append(top_pipe)
            pipes.append(bottom_pipe)
            pipe_timer = 0

        for pipe in pipes:
            pipe.update()
            if pipe.rect.right < 0:
                pipes.remove(pipe)
                score += 0.5  # Each pair of pipes passed adds 1 to the score

        # Check for collisions
        if check_collision(bird, pipes):
            break  # End the game

        # Draw everything
        screen.fill((0, 0, 255))  # Blue background
        bird.draw(screen)
        for pipe in pipes:
            pipe.draw(screen)
        display_text(screen, f"Score: {int(score)}", 10, 10)
        pygame.display.update()

    # Game over screen
    while True:
        screen.fill((0, 0, 0))
        display_text(screen, "Game Over", SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 50)
        display_text(screen, f"Final Score: {int(score)}", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2)
        display_text(screen, "Press R to Restart or Q to Quit", SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2 + 50)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

if __name__ == '__main__':
    main()

