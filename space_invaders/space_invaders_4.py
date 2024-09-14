import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Enhanced Space Invaders by ChatGPT')

# Load background image
background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
background.fill((0, 0, 0))  # Black background

# Load player image
player_image = pygame.Surface((50, 50), pygame.SRCALPHA)
pygame.draw.polygon(player_image, (0, 255, 0), [(25, 0), (0, 50), (50, 50)])
player_rect = player_image.get_rect()
player_rect.midbottom = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 10)

# Enemy image
enemy_image = pygame.Surface((40, 40), pygame.SRCALPHA)
pygame.draw.circle(enemy_image, (255, 0, 0), (20, 20), 20)
enemy_rect = enemy_image.get_rect()

# Player bullet image
bullet_image = pygame.Surface((5, 15), pygame.SRCALPHA)
bullet_image.fill((255, 255, 0))
bullet_rect = bullet_image.get_rect()

# Enemy bullet image
enemy_bullet_image = pygame.Surface((5, 15), pygame.SRCALPHA)
enemy_bullet_image.fill((255, 0, 0))
enemy_bullet_rect = enemy_bullet_image.get_rect()

# Game variables
player_speed = 5
bullet_speed = -10
enemy_speed = 1
enemy_bullet_speed = 5

# Fonts
font = pygame.font.SysFont('Arial', 32)

# Score
score_value = 0

def show_text(text, x, y, color=(255, 255, 255)):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

# Game Over
def game_over_text():
    over_text = font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2))

# Draw player
def draw_player(x, y):
    screen.blit(player_image, (x, y))

# Draw enemy
def draw_enemy(x, y):
    screen.blit(enemy_image, (x, y))

# Bullet movement
def fire_bullet(x, y):
    screen.blit(bullet_image, (x, y))

# Enemy bullet movement
def fire_enemy_bullet(x, y):
    screen.blit(enemy_bullet_image, (x, y))

# Collision detection
def is_collision(obj1_x, obj1_y, obj2_x, obj2_y, distance_threshold=27):
    distance = math.hypot(obj1_x - obj2_x, obj1_y - obj2_y)
    return distance < distance_threshold

def main():
    global enemy_speed, enemy_bullet_speed, enemy_fire_delay, score_value

    # Game variables
    player_x = SCREEN_WIDTH // 2 - player_rect.width // 2
    player_y = SCREEN_HEIGHT - player_rect.height - 10
    player_x_change = 0
    player_lives = 3
    level = 1
    max_level = 5
    score_value = 0

    # Enemy variables
    enemies = []
    enemy_bullets = []
    num_of_enemies = 3  # Starting with 3 enemies
    initial_enemy_fire_delay = 2000  # Time in milliseconds between enemy shots
    enemy_fire_delay = initial_enemy_fire_delay

    # Create enemies
    def create_enemies(num):
        for _ in range(num):
            enemy = {
                'x': random.randint(0, SCREEN_WIDTH - enemy_rect.width),
                'y': random.randint(50, 150),
                'x_change': enemy_speed,
                'y_change': 40,
                'last_shot_time': pygame.time.get_ticks(),
                'fire_interval': random.randint(int(enemy_fire_delay * 0.5), int(enemy_fire_delay * 1.5))
            }
            enemies.append(enemy)

    create_enemies(num_of_enemies)

    # Bullet variables
    bullet_x = 0
    bullet_y = player_y
    bullet_state = "ready"  # "ready" - you can't see the bullet, "fire" - bullet is moving

    running = True
    clock = pygame.time.Clock()

    while running:
        # Fill background
        screen.blit(background, (0, 0))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            # Keystroke events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player_x_change = -player_speed
                if event.key == pygame.K_RIGHT:
                    player_x_change = player_speed
                if event.key == pygame.K_SPACE:
                    if bullet_state == "ready":
                        bullet_x = player_x + player_rect.width // 2 - bullet_rect.width // 2
                        bullet_y = player_y
                        bullet_state = "fire"
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    player_x_change = 0

        # Player movement
        player_x += player_x_change
        if player_x <= 0:
            player_x = 0
        elif player_x >= SCREEN_WIDTH - player_rect.width:
            player_x = SCREEN_WIDTH - player_rect.width

        # Enemy movement
        for enemy in enemies[:]:  # Iterate over a copy to safely remove enemies
            # Game Over if enemy reaches bottom
            if enemy['y'] > SCREEN_HEIGHT - 150:
                player_lives = 0
                break

            enemy['x'] += enemy['x_change']
            if enemy['x'] <= 0:
                enemy['x_change'] = enemy_speed
                enemy['y'] += enemy['y_change']
            elif enemy['x'] >= SCREEN_WIDTH - enemy_rect.width:
                enemy['x_change'] = -enemy_speed
                enemy['y'] += enemy['y_change']

            # Enemy shooting
            current_time = pygame.time.get_ticks()
            if current_time - enemy['last_shot_time'] > enemy['fire_interval']:
                enemy_bullet_x = enemy['x'] + enemy_rect.width // 2 - enemy_bullet_rect.width // 2
                enemy_bullet_y = enemy['y'] + enemy_rect.height
                enemy_bullets.append([enemy_bullet_x, enemy_bullet_y])
                enemy['last_shot_time'] = current_time
                # Set next fire interval
                enemy['fire_interval'] = random.randint(int(enemy_fire_delay * 0.5), int(enemy_fire_delay * 1.5))

            # Check collision between player and enemy
            if is_collision(enemy['x'], enemy['y'], player_x, player_y, distance_threshold=30):
                player_lives -= 1
                enemies.remove(enemy)
                if player_lives <= 0:
                    break

            draw_enemy(enemy['x'], enemy['y'])

        # Enemy bullets movement
        for bullet in enemy_bullets[:]:
            bullet[1] += enemy_bullet_speed
            fire_enemy_bullet(bullet[0], bullet[1])
            if bullet[1] > SCREEN_HEIGHT:
                enemy_bullets.remove(bullet)
            elif is_collision(
                bullet[0], bullet[1],
                player_x + player_rect.width // 2,
                player_y + player_rect.height // 2,
                distance_threshold=25
            ):
                player_lives -= 1
                enemy_bullets.remove(bullet)
                if player_lives <= 0:
                    break

        # Bullet movement
        if bullet_state == "fire":
            fire_bullet(bullet_x, bullet_y)
            bullet_y += bullet_speed
            if bullet_y <= 0:
                bullet_y = player_y
                bullet_state = "ready"
            else:
                # Collision detection with enemies
                for enemy in enemies[:]:
                    collision = is_collision(enemy['x'], enemy['y'], bullet_x, bullet_y)
                    if collision:
                        bullet_y = player_y
                        bullet_state = "ready"
                        score_value += 1
                        enemies.remove(enemy)
                        break  # Exit the loop since bullet is used up

        # Check if all enemies are eliminated to increase level
        if not enemies:
            if level >= max_level:
                # Victory
                victory_text = font.render("YOU WIN!", True, (0, 255, 0))
                screen.blit(
                    victory_text,
                    (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, SCREEN_HEIGHT // 2)
                )
                pygame.display.update()
                pygame.time.wait(3000)
                main()  # Restart game
                return
            else:
                level += 1
                # Increase difficulty
                enemy_speed += 0.5
                enemy_bullet_speed += 0.5
                # Decrease enemy fire delay to increase shooting frequency
                enemy_fire_delay = max(500, int(initial_enemy_fire_delay - (level - 1) * 300))
                num_of_enemies += 2  # Increase enemies each level
                enemies = []
                enemy_bullets = []
                create_enemies(num_of_enemies)

        # Draw player
        draw_player(player_x, player_y)

        # Show score and lives
        show_text(f"Score: {score_value}", 10, 10)
        show_text(f"Lives: {player_lives}", 10, 50)
        show_text(f"Level: {level}", SCREEN_WIDTH - 150, 10)

        # Game Over condition
        if player_lives <= 0:
            game_over_text()
            pygame.display.update()
            pygame.time.wait(3000)
            main()  # Restart game
            return

        # Update the display
        pygame.display.update()
        clock.tick(60)  # 60 FPS

if __name__ == '__main__':
    main()

