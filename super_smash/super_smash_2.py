import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Platform Fighter')

# Clock object
clock = pygame.time.Clock()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BLUE = (173, 216, 230)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Game variables
GRAVITY = 0.5
MAX_JUMP_HEIGHT = 10
PLAYER_SPEED = 5
ATTACK_COOLDOWN = 500  # milliseconds

# Player class
class Player:
    def __init__(self, x, y, color, controls):
        self.rect = pygame.Rect(x, y, 40, 60)
        self.color = color
        self.velocity_y = 0
        self.on_ground = False
        self.move_left = False
        self.move_right = False
        self.is_jumping = False
        self.is_attacking = False
        self.attack_time = 0
        self.controls = controls
        self.percent = 0  # Damage percentage

    def handle_keys(self):
        keys = pygame.key.get_pressed()
        if keys[self.controls.get('left', 0)]:
            self.move_left = True
        else:
            self.move_left = False

        if keys[self.controls.get('right', 0)]:
            self.move_right = True
        else:
            self.move_right = False

        if keys[self.controls.get('jump', 0)]:
            if self.on_ground:
                self.is_jumping = True
                self.velocity_y = -MAX_JUMP_HEIGHT

        if keys[self.controls.get('attack', 0)]:
            if not self.is_attacking:
                self.is_attacking = True
                self.attack_time = pygame.time.get_ticks()

    def move(self):
        # Horizontal movement
        if self.move_left:
            self.rect.x -= PLAYER_SPEED
        if self.move_right:
            self.rect.x += PLAYER_SPEED

        # Apply gravity
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        # Reset jump
        if self.is_jumping and self.velocity_y >= 0:
            self.is_jumping = False

    def check_collisions(self, platforms):
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Landing on top of a platform
                if self.velocity_y >= 0 and self.rect.bottom <= platform.rect.bottom:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
                # Hitting the bottom of a platform
                elif self.velocity_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0

    def attack(self, opponent):
        # Simple attack logic: if close enough, increase opponent's damage
        if self.is_attacking:
            current_time = pygame.time.get_ticks()
            if current_time - self.attack_time > ATTACK_COOLDOWN:
                self.is_attacking = False
            else:
                attack_rect = pygame.Rect(self.rect.centerx - 25, self.rect.y, 50, self.rect.height)
                if attack_rect.colliderect(opponent.rect):
                    # Apply knockback based on opponent's percent
                    knockback = 5 + (opponent.percent * 0.1)
                    if self.rect.centerx < opponent.rect.centerx:
                        opponent.rect.x += knockback
                    else:
                        opponent.rect.x -= knockback
                    opponent.rect.y -= knockback
                    opponent.percent += 10  # Increase damage percentage
                    self.is_attacking = False  # Reset attack

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        # Draw damage percentage
        font = pygame.font.SysFont('Arial', 24)
        percent_text = font.render(f"{int(self.percent)}%", True, self.color)
        surface.blit(percent_text, (self.rect.x, self.rect.y - 30))

# Platform class
class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        pygame.draw.rect(surface, LIGHT_BLUE, self.rect)

# AI Controller
class AIController:
    def __init__(self, player, opponent, platforms):
        self.player = player
        self.opponent = opponent
        self.platforms = platforms

    def update(self):
        # Simple AI logic
        # Move towards the player
        if self.opponent.rect.x < self.player.rect.x:
            self.opponent.move_left = False
            self.opponent.move_right = True
        else:
            self.opponent.move_left = True
            self.opponent.move_right = False

        # Check if AI is near the edge of a platform
        on_platform = False
        for platform in self.platforms:
            if self.opponent.rect.bottom == platform.rect.top and platform.rect.left <= self.opponent.rect.centerx <= platform.rect.right:
                on_platform = True
                # Stop moving right if at the right edge
                if self.opponent.rect.right >= platform.rect.right:
                    self.opponent.move_right = False
                # Stop moving left if at the left edge
                if self.opponent.rect.left <= platform.rect.left:
                    self.opponent.move_left = False
                break

        # Jump if player is above
        if self.player.rect.y < self.opponent.rect.y and self.opponent.on_ground:
            self.opponent.is_jumping = True
            self.opponent.velocity_y = -MAX_JUMP_HEIGHT

        # Attack if close enough
        distance = abs(self.player.rect.centerx - self.opponent.rect.centerx)
        if distance < 60 and not self.opponent.is_attacking:
            self.opponent.is_attacking = True
            self.opponent.attack_time = pygame.time.get_ticks()

def main():
    # Create platforms
    platforms = [
        Platform(200, 500, 400, 20),
        Platform(150, 400, 100, 20),
        Platform(550, 400, 100, 20),
        Platform(350, 300, 100, 20),
    ]

    # Define player controls
    player_controls = {
        'left': pygame.K_LEFT,
        'right': pygame.K_RIGHT,
        'jump': pygame.K_UP,
        'attack': pygame.K_SPACE,
    }

    # Create players
    player = Player(300, 100, RED, player_controls)
    ai_player = Player(500, 100, BLUE, {})  # Empty controls for AI

    # Create AI controller
    ai_controller = AIController(player, ai_player, platforms)

    running = True

    while running:
        clock.tick(60)  # 60 FPS
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Player input
        player.handle_keys()

        # AI logic
        ai_controller.update()

        # Move players
        player.move()
        ai_player.move()

        # Check collisions
        player.check_collisions(platforms)
        ai_player.check_collisions(platforms)

        # Attacks
        player.attack(ai_player)
        ai_player.attack(player)

        # Draw platforms
        for platform in platforms:
            platform.draw(screen)

        # Draw players
        player.draw(screen)
        ai_player.draw(screen)

        # Check if players are off-screen (knocked out)
        if player.rect.top > SCREEN_HEIGHT or player.rect.right < 0 or player.rect.left > SCREEN_WIDTH:
            # Player loses
            game_over(screen, "You Lose!")
            return
        if ai_player.rect.top > SCREEN_HEIGHT or ai_player.rect.right < 0 or ai_player.rect.left > SCREEN_WIDTH:
            # Player wins
            game_over(screen, "You Win!")
            return

        pygame.display.flip()

    pygame.quit()
    sys.exit()

def game_over(surface, message):
    font = pygame.font.SysFont('Arial', 64)
    text = font.render(message, True, BLACK)
    surface.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000)

if __name__ == '__main__':
    main()

