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
pygame.display.set_caption('Space Invaders by ChatGPT')

# Load background image
background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
background.fill((0, 0, 0))  # Black background

# Load player image
player_image = pygame.Surface((50, 50))
pygame.draw.polygon(player_image, (0, 255, 0), [(25, 0), (0, 50), (50, 50)])
player_rect = player_image.get_rect()
player_rect.midbottom = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 10)

# Enemy image
enemy_image = pygame.Surface((40, 40))
pygame.draw.circle(enemy_image, (255, 0, 0), (20, 20), 20)
enemy_rect = enemy_image.get_rect()

# Bullet image
bullet_image = pygame.Surface((5, 15))
bullet_image.fill((255, 255, 0))
bullet_rect = bullet_image.get_rect()

# Game variables
player_speed = 5
bullet_speed = -10
enemy_speed = 1
num_of_enemies = 6

# Fonts
font = pygame.font.SysFont('Arial', 32)

# Sounds (optional, comment out if you don't have sound files)
# bullet_sound = pygame.mixer.Sound('laser.wav')
# explosion_sound = pygame.mixer.Sound('explosion.wav')

# Score
score_value = 0
def show_score():
    score = font.render(f"Score: {score_value}", True, (255, 255, 255))
    screen.blit(score, (10, 10))

# Game Over
def game_over_text():
    over_text = font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2))

# Player movement
def player(x, y):
    screen.blit(player_image, (x, y))

# Enemy movement
def enemy(x, y):
    screen.blit(enemy_image, (x, y))

# Bullet movement
def fire_bullet(x, y):
    screen.blit(bullet_image, (x, y))

# Collision detection
def is_collision(enemy_x, enemy_y, bullet_x, bullet_y):
    distance = math.hypot(enemy_x - bullet_x, enemy_y - bullet_y)
    return distance < 27

def main():
    # Player position
    player_x = SCREEN_WIDTH // 2 - player_rect.width // 2
    player_y = SCREEN_HEIGHT - player_rect.height - 10
    player_x_change = 0

    # Enemy positions
    enemy_x = []
    enemy_y = []
    enemy_x_change = []
    enemy_y_change = []
    for _ in range(num_of_enemies):
        enemy_x.append(random.randint(0, SCREEN_WIDTH - enemy_rect.width))
        enemy_y.append(random.randint(50, 150))
        enemy_x_change.append(enemy_speed)
        enemy_y_change.append(40)

    # Bullet position
    bullet_x = 0
    bullet_y = player_y
    bullet_state = "ready"  # "ready" - you can't see the bullet, "fire" - bullet is moving

    global score_value
    score_value = 0

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
                        # bullet_sound.play()
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
        for i in range(num_of_enemies):
            # Game Over
            if enemy_y[i] > SCREEN_HEIGHT - 150:
                for j in range(num_of_enemies):
                    enemy_y[j] = SCREEN_HEIGHT + 100  # Move enemies off screen
                game_over_text()
                pygame.display.update()
                pygame.time.wait(2000)
                main()
                return

            enemy_x[i] += enemy_x_change[i]
            if enemy_x[i] <= 0:
                enemy_x_change[i] = enemy_speed
                enemy_y[i] += enemy_y_change[i]
            elif enemy_x[i] >= SCREEN_WIDTH - enemy_rect.width:
                enemy_x_change[i] = -enemy_speed
                enemy_y[i] += enemy_y_change[i]

            # Collision detection
            if bullet_state == "fire":
                collision = is_collision(enemy_x[i], enemy_y[i], bullet_x, bullet_y)
                if collision:
                    # explosion_sound.play()
                    bullet_y = player_y
                    bullet_state = "ready"
                    score_value += 1
                    enemy_x[i] = random.randint(0, SCREEN_WIDTH - enemy_rect.width)
                    enemy_y[i] = random.randint(50, 150)

            enemy(enemy_x[i], enemy_y[i])

        # Bullet movement
        if bullet_state == "fire":
            fire_bullet(bullet_x, bullet_y)
            bullet_y += bullet_speed
            if bullet_y <= 0:
                bullet_y = player_y
                bullet_state = "ready"

        # Draw player
        player(player_x, player_y)

        # Show score
        show_score()

        # Update the display
        pygame.display.update()
        clock.tick(60)  # 60 FPS

if __name__ == '__main__':
    main()

