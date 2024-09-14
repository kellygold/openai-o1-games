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
                self.state = 'chase'
            return

        # Aggressive chase behavior
        self.chase_player()

        # Attack if close enough
        distance = abs(self.player.rect.centerx - self.opponent.rect.centerx)
        if distance < 60 and not self.opponent.is_attacking:
            self.opponent.is_attacking = True
            self.opponent.attack_time = pygame.time.get_ticks()

    def chase_player(self):
        # Determine vertical relation
        if self.opponent.rect.bottom < self.player.rect.top - 10:
            # Player is below AI
            self.move_to_lower_platform()
        elif self.opponent.rect.top > self.player.rect.bottom + 10:
            # Player is above AI
            self.move_to_higher_platform()
        else:
            # Player is on the same level
            self.move_horizontally_towards_player()

    def move_horizontally_towards_player(self):
        # Move towards the player
        if self.opponent.rect.x < self.player.rect.x:
            self.opponent.move_left = False
            self.opponent.move_right = True
        else:
            self.opponent.move_left = True
            self.opponent.move_right = False

        # Prevent AI from falling off platforms
        if not self.can_move('left') and self.opponent.move_left:
            self.opponent.move_left = False
        if not self.can_move('right') and self.opponent.move_right:
            self.opponent.move_right = False

    def move_to_higher_platform(self):
        # Find platforms above the AI
        platforms_above = [p for p in self.platforms if p.rect.bottom <= self.opponent.rect.top]
        if platforms_above:
            # Find the closest platform above
            target_platform = min(platforms_above, key=lambda p: abs(p.rect.centerx - self.player.rect.centerx))
            # Move towards the platform's position
            if self.opponent.rect.centerx < target_platform.rect.centerx:
                self.opponent.move_left = False
                self.opponent.move_right = True
            else:
                self.opponent.move_left = True
                self.opponent.move_right = False

            # Jump if underneath the platform
            if self.opponent.on_ground and not self.opponent.is_jumping:
                self.opponent.is_jumping = True
                self.opponent.velocity_y = -MAX_JUMP_HEIGHT
        else:
            # No platforms above, move towards player horizontally
            self.move_horizontally_towards_player()

    def move_to_lower_platform(self):
        # Find platforms below the AI
        platforms_below = [p for p in self.platforms if p.rect.top >= self.opponent.rect.bottom]
        if platforms_below:
            # Find the closest platform below
            target_platform = min(platforms_below, key=lambda p: abs(p.rect.centerx - self.player.rect.centerx))
            # Move towards the platform's position
            if self.opponent.rect.centerx < target_platform.rect.centerx:
                self.opponent.move_left = False
                self.opponent.move_right = True
            else:
                self.opponent.move_left = True
                self.opponent.move_right = False

            # Drop down if at the edge of the platform
            if self.opponent.on_ground and self.is_at_platform_edge():
                self.opponent.velocity_y += GRAVITY  # Apply gravity to fall off the platform
        else:
            # No platforms below, move towards player horizontally
            self.move_horizontally_towards_player()

    def is_at_platform_edge(self):
        # Check if AI is at the edge of the platform
        for platform in self.platforms:
            if self.opponent.rect.bottom == platform.rect.top:
                edge_margin = 5
                if self.opponent.move_left and self.opponent.rect.left <= platform.rect.left + edge_margin:
                    return True
                if self.opponent.move_right and self.opponent.rect.right >= platform.rect.right - edge_margin:
                    return True
        return False

    def can_move(self, direction):
        # Predict next position
        next_rect = self.opponent.rect.copy()
        if direction == 'left':
            next_rect.x -= PLAYER_SPEED
        elif direction == 'right':
            next_rect.x += PLAYER_SPEED

        # Check if next position keeps the AI on the platform
        for platform in self.platforms:
            if (next_rect.bottom == platform.rect.top and
                platform.rect.left <= next_rect.centerx <= platform.rect.right):
                return True
        return False

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
    player = Player(300, 500 - 60, RED, player_controls)
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
                        player.rect.x = 300
                        player.rect.y = 500 - 60
                        ai_player.rect.x = 550
                        ai_player.rect.y = 400 - 60
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

