import pygame
import sys
import random

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
GRAVITY = 0.6
MAX_JUMP_HEIGHT = 12  # Reduced jump height
PLAYER_SPEED = 5
ATTACK_COOLDOWN = 500  # milliseconds

# Player class
class Player:
    def __init__(self, x, y, color, controls):
        self.initial_x = x
        self.initial_y = y
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
        self.alive = True

    def reset(self):
        self.rect.x = self.initial_x
        self.rect.y = self.initial_y
        self.velocity_y = 0
        self.on_ground = False
        self.move_left = False
        self.move_right = False
        self.is_jumping = False
        self.is_attacking = False
        self.attack_time = 0
        self.percent = 0
        self.alive = True

    def handle_keys(self):
        keys = pygame.key.get_pressed()
        if self.controls:
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
                if self.velocity_y >= 0 and self.rect.bottom <= platform.rect.bottom + 10:
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
                    knockback = 5 + (opponent.percent * 0.2)  # Increased knockback scaling
                    if self.rect.centerx < opponent.rect.centerx:
                        opponent.rect.x += knockback
                    else:
                        opponent.rect.x -= knockback
                    opponent.rect.y -= knockback * 0.5  # Apply upward knockback
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
        self.state = 'idle'
        self.direction = random.choice(['left', 'right'])
        self.change_direction_time = pygame.time.get_ticks()
        self.jump_cooldown = 0
        self.idle_time = pygame.time.get_ticks()
        self.idle_duration = 1000  # AI waits for 1 second before moving

    def update(self):
        current_time = pygame.time.get_ticks()

        # Idle state at the beginning
        if self.state == 'idle':
            self.opponent.move_left = False
            self.opponent.move_right = False
            if current_time - self.idle_time > self.idle_duration:
                self.state = 'wander'
            return

        # Decide whether to change state
        if abs(self.player.rect.centerx - self.opponent.rect.centerx) < 200:
            self.state = 'chase'
        else:
            self.state = 'wander'

        if self.state == 'wander':
            # Randomly change direction
            if current_time - self.change_direction_time > 2000:
                self.direction = random.choice(['left', 'right'])
                self.change_direction_time = current_time

            if self.direction == 'left':
                self.opponent.move_left = True
                self.opponent.move_right = False
            else:
                self.opponent.move_left = False
                self.opponent.move_right = True

            # Randomly jump
            if self.opponent.on_ground and current_time - self.jump_cooldown > 3000:
                self.opponent.is_jumping = True
                self.opponent.velocity_y = -MAX_JUMP_HEIGHT
                self.jump_cooldown = current_time

        elif self.state == 'chase':
            # Move towards the player
            if self.opponent.rect.x < self.player.rect.x:
                self.opponent.move_left = False
                self.opponent.move_right = True
            else:
                self.opponent.move_left = True
                self.opponent.move_right = False

            # Jump if player is above
            if self.player.rect.y < self.opponent.rect.y - 50 and self.opponent.on_ground:
                self.opponent.is_jumping = True
                self.opponent.velocity_y = -MAX_JUMP_HEIGHT

        # Prevent AI from moving off platforms
        self.prevent_falling()

        # Attack if close enough
        distance = abs(self.player.rect.centerx - self.opponent.rect.centerx)
        if distance < 60 and not self.opponent.is_attacking:
            self.opponent.is_attacking = True
            self.opponent.attack_time = pygame.time.get_ticks()  # Corrected line

    def prevent_falling(self):
        # Check if AI is on a platform
        on_platform = False
        for platform in self.platforms:
            if (self.opponent.rect.bottom == platform.rect.top and
                platform.rect.left <= self.opponent.rect.centerx <= platform.rect.right):
                on_platform = True
                # Edge detection
                edge_margin = 20  # Increased edge margin
                if self.opponent.rect.right >= platform.rect.right - edge_margin:
                    self.opponent.move_right = False
                    self.direction = 'left'
                if self.opponent.rect.left <= platform.rect.left + edge_margin:
                    self.opponent.move_left = False
                    self.direction = 'right'
                break

        if not on_platform:
            # If not on any platform, stop moving horizontally
            self.opponent.move_left = False
            self.opponent.move_right = False
            # Attempt to move back onto platform if on ground
            if self.opponent.on_ground:
                closest_platform = min(self.platforms, key=lambda p: abs(self.opponent.rect.centerx - p.rect.centerx))
                if self.opponent.rect.centerx < closest_platform.rect.centerx:
                    self.opponent.move_right = True
                else:
                    self.opponent.move_left = True

def main():
    # Create platforms
    platforms = [
        Platform(200, 500, 400, 20),
        Platform(100, 400, 150, 20),
        Platform(550, 400, 150, 20),
        Platform(350, 300, 100, 20),
        Platform(250, 200, 100, 20),  # Added higher platform
        Platform(450, 200, 100, 20),  # Added higher platform
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
    ai_player = Player(550, 400 - 60, BLUE, {})  # Adjusted starting position

    # Create AI controller
    ai_controller = AIController(player, ai_player, platforms)

    running = True
    game_active = True
    game_over_message = ""

    while running:
        clock.tick(60)  # 60 FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Handle play again option
            if event.type == pygame.KEYDOWN:
                if not game_active:
                    if event.key == pygame.K_r:
                        # Reset game
                        player.reset()
                        ai_player.reset()
                        ai_player.rect.x = 550  # Reset AI position
                        ai_player.rect.y = 400 - 60  # Reset AI position
                        ai_controller = AIController(player, ai_player, platforms)
                        game_active = True
                        game_over_message = ""

        if game_active:
            screen.fill(WHITE)

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
                player.alive = False
            if ai_player.rect.top > SCREEN_HEIGHT or ai_player.rect.right < 0 or ai_player.rect.left > SCREEN_WIDTH:
                ai_player.alive = False

            if not player.alive:
                game_active = False
                game_over_message = "You Lose! Press 'R' to Play Again"
            elif not ai_player.alive:
                game_active = False
                game_over_message = "You Win! Press 'R' to Play Again"

            pygame.display.flip()

        else:
            # Game is not active, display game over screen
            screen.fill(WHITE)
            game_over(screen, game_over_message)
            pygame.display.flip()

    pygame.quit()
    sys.exit()

def game_over(surface, message):
    font = pygame.font.SysFont('Arial', 48)
    text = font.render(message, True, BLACK)
    surface.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))

if __name__ == '__main__':
    main()

