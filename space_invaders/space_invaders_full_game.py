import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Enhanced Space Invaders')

# Load background
background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
background.fill((0, 0, 0))  # Black background

# Player image
player_image = pygame.Surface((50, 50), pygame.SRCALPHA)
pygame.draw.polygon(player_image, (0, 255, 0), [(25, 0), (0, 50), (50, 50)])
player_rect = player_image.get_rect()

# Enemy image
enemy_image = pygame.Surface((40, 40), pygame.SRCALPHA)
pygame.draw.circle(enemy_image, (255, 0, 0), (20, 20), 20)

# Bullet images
bullet_image = pygame.Surface((5, 15), pygame.SRCALPHA)
bullet_image.fill((255, 255, 0))

enemy_bullet_image = pygame.Surface((5, 15), pygame.SRCALPHA)
enemy_bullet_image.fill((255, 0, 0))

# Fonts
font = pygame.font.SysFont('Arial', 32)

def show_text(text, x, y, color=(255, 255, 255)):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

def game_over_screen(score):
    """Display 'Game Over' message and high scores."""
    # Load high scores
    high_scores = load_high_scores()
    # Update high scores
    updated = update_high_scores(high_scores, score)
    if updated:
        save_high_scores(high_scores)

    screen.fill((0, 0, 0))  # Clear the screen
    over_text = font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(
        over_text,
        (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100)
    )

    # Display high scores
    y_offset = SCREEN_HEIGHT // 2 - 50
    show_text("High Scores:", SCREEN_WIDTH // 2 - 80, y_offset)
    y_offset += 40
    for idx, hs in enumerate(high_scores[:5], start=1):
        score_text = f"{idx}. {hs}"
        show_text(score_text, SCREEN_WIDTH // 2 - 40, y_offset)
        y_offset += 30

    show_text("Press any key to restart", SCREEN_WIDTH // 2 - 150, y_offset + 20)
    pygame.display.update()

    # Wait for key press to restart
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
                main()  # Restart the game

def load_high_scores():
    """Load high scores from a file."""
    if not os.path.exists("high_scores.txt"):
        return []
    with open("high_scores.txt", "r") as f:
        scores = f.readlines()
    return [int(score.strip()) for score in scores]

def save_high_scores(scores):
    """Save high scores to a file."""
    with open("high_scores.txt", "w") as f:
        for score in scores:
            f.write(f"{score}\n")

def update_high_scores(scores, new_score):
    """Update the high scores list with the new score."""
    scores.append(new_score)
    scores.sort(reverse=True)
    # Keep only top 5 scores
    scores = scores[:5]
    return True

def main():
    global enemy_speed, enemy_bullet_speed, enemy_fire_delay

    # Game variables
    player_speed = 5
    bullet_speed = -10
    enemy_speed = 1
    enemy_bullet_speed = 5

    player_x = SCREEN_WIDTH // 2 - player_rect.width // 2
    player_y = SCREEN_HEIGHT - player_rect.height - 10
    player_x_change = 0
    player_lives = 3
    level = 1
    max_level = 5
    score_value = 0

    # Initialize bullet rects inside main
    bullet_rect = bullet_image.get_rect()
    enemy_bullet_rect = enemy_bullet_image.get_rect()

    # Enemy variables
    enemies = []
    enemy_bullets = []
    num_of_enemies = 3  # Starting with 3 enemies
    initial_enemy_fire_delay = 3500  # Increased initial delay to 3500 ms
    enemy_fire_delay = initial_enemy_fire_delay

    # Create enemies
    def create_enemies(num):
        for _ in range(num):
            enemy = {
                'x': random.randint(0, SCREEN_WIDTH - enemy_image.get_width()),
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
    bullet_state = "ready"  # "ready" or "fire"

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
                        bullet_x = player_x + player_rect.width // 2 - bullet_image.get_width() // 2
                        bullet_y = player_y
                        bullet_state = "fire"
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    player_x_change = 0

        # Player movement
        player_x += player_x_change
        player_x = max(0, min(player_x, SCREEN_WIDTH - player_rect.width))

        # Update player rect position
        player_rect.x = player_x
        player_rect.y = player_y

        # Enemy movement and actions
        for enemy in enemies[:]:  # Copy of the list
            # Enemy movement
            enemy['x'] += enemy['x_change']
            if enemy['x'] <= 0 or enemy['x'] >= SCREEN_WIDTH - enemy_image.get_width():
                enemy['x_change'] *= -1
                enemy['y'] += enemy['y_change']

            # Enemy shoots
            current_time = pygame.time.get_ticks()
            if current_time - enemy['last_shot_time'] > enemy['fire_interval']:
                enemy_bullet_x = enemy['x'] + enemy_image.get_width() // 2 - enemy_bullet_image.get_width() // 2
                enemy_bullet_y = enemy['y'] + enemy_image.get_height()
                enemy_bullets.append([enemy_bullet_x, enemy_bullet_y])
                enemy['last_shot_time'] = current_time
                enemy['fire_interval'] = random.randint(int(enemy_fire_delay * 0.5), int(enemy_fire_delay * 1.5))

            # Update enemy rect
            enemy_rect = enemy_image.get_rect(topleft=(enemy['x'], enemy['y']))

            # Check collision with player
            if enemy_rect.colliderect(player_rect):
                player_lives -= 1
                enemies.remove(enemy)
                if player_lives <= 0:
                    break

            # Draw enemy
            screen.blit(enemy_image, (enemy['x'], enemy['y']))

        # Enemy bullets movement
        for bullet in enemy_bullets[:]:
            bullet[1] += enemy_bullet_speed
            screen.blit(enemy_bullet_image, (bullet[0], bullet[1]))

            # Update enemy bullet rect
            enemy_bullet_rect = enemy_bullet_image.get_rect(topleft=(bullet[0], bullet[1]))

            if bullet[1] > SCREEN_HEIGHT:
                enemy_bullets.remove(bullet)
            elif enemy_bullet_rect.colliderect(player_rect):
                player_lives -= 1
                enemy_bullets.remove(bullet)
                if player_lives <= 0:
                    break

        # Player bullet movement
        if bullet_state == "fire":
            screen.blit(bullet_image, (bullet_x, bullet_y))
            bullet_y += bullet_speed

            # Update bullet rect
            bullet_rect = bullet_image.get_rect(topleft=(bullet_x, bullet_y))

            if bullet_y <= 0:
                bullet_y = player_y
                bullet_state = "ready"
            else:
                # Collision with enemies
                for enemy in enemies[:]:
                    enemy_rect = enemy_image.get_rect(topleft=(enemy['x'], enemy['y']))
                    if bullet_rect.colliderect(enemy_rect):
                        bullet_y = player_y
                        bullet_state = "ready"
                        score_value += 1
                        enemies.remove(enemy)
                        break  # Bullet used up

        # Check for level completion
        if not enemies:
            if level >= max_level:
                # Victory
                victory_text = font.render("YOU WIN!", True, (0, 255, 0))
                screen.blit(victory_text, (SCREEN_WIDTH // 2 - victory_text.get_width() // 2, SCREEN_HEIGHT // 2))
                pygame.display.update()
                pygame.time.wait(3000)
                game_over_screen(score_value)  # Show high scores
                return
            else:
                level += 1
                # Increase difficulty
                enemy_speed += 0.5
                enemy_bullet_speed += 0.5
                # Adjust enemy fire delay
                enemy_fire_delay = max(2000, int(initial_enemy_fire_delay - (level - 1) * 250))
                num_of_enemies += 2
                enemies = []
                enemy_bullets = []
                create_enemies(num_of_enemies)

        # Draw player
        screen.blit(player_image, (player_x, player_y))

        # Display score and lives
        show_text(f"Score: {score_value}", 10, 10)
        show_text(f"Lives: {player_lives}", 10, 50)
        show_text(f"Level: {level}", SCREEN_WIDTH - 150, 10)

        # Game Over
        if player_lives <= 0:
            pygame.display.update()
            pygame.time.wait(1000)
            game_over_screen(score_value)  # Show high scores
            return

        # Update the display
        pygame.display.update()
        clock.tick(60)  # 60 FPS

if __name__ == '__main__':
    main()

