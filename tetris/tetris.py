import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 400
screen_height = 600

# Playable grid dimensions
play_width = 300  # 10 blocks wide
play_height = 600  # 20 blocks high
block_size = 30

# Top-left coordinates of the play area
top_left_x = (screen_width - play_width) // 2
top_left_y = screen_height - play_height

# Shapes and their rotations
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
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

L = [['.....',
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

T = [['.....',
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

# List of shapes
shapes = [S, Z, I, O, J, L, T]
# Corresponding colors
shape_colors = [
    (0, 255, 0),    # Green
    (255, 0, 0),    # Red
    (0, 255, 255),  # Cyan
    (255, 255, 0),  # Yellow
    (255, 165, 0),  # Orange
    (0, 0, 255),    # Blue
    (128, 0, 128)   # Purple
]

class Piece:
    """Represents a Tetris piece."""
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0

def create_grid(locked_positions={}):
    """Create a grid with locked positions."""
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                grid[i][j] = locked_positions[(j, i)]
    return grid

def convert_shape_format(shape):
    """Convert the shape format for the grid."""
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j - 2, shape.y + i - 4))
    return positions

def valid_space(shape, grid):
    """Check if the space is valid for movement."""
    accepted_positions = [
        [(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)]
        for i in range(20)
    ]
    accepted_positions = [pos for sublist in accepted_positions for pos in sublist]
    formatted = convert_shape_format(shape)
    for pos in formatted:
        if pos not in accepted_positions and pos[1] > -1:
            return False
    return True

def check_lost(positions):
    """Check if the game is lost."""
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def get_shape():
    """Get a random new shape."""
    return Piece(5, 0, random.choice(shapes))

def draw_text_middle(surface, text, size, color):
    """Draw text in the middle of the surface."""
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, True, color)
    surface.blit(
        label,
        (top_left_x + play_width / 2 - label.get_width() / 2,
         top_left_y + play_height / 2 - label.get_height() / 2)
    )

def draw_grid(surface, grid):
    """Draw the grid lines."""
    sx = top_left_x
    sy = top_left_y
    for i in range(len(grid)):
        # Horizontal lines
        pygame.draw.line(
            surface, (128, 128, 128),
            (sx, sy + i * block_size),
            (sx + play_width, sy + i * block_size)
        )
        for j in range(len(grid[i])):
            # Vertical lines
            pygame.draw.line(
                surface, (128, 128, 128),
                (sx + j * block_size, sy),
                (sx + j * block_size, sy + play_height)
            )

def clear_rows(grid, locked):
    """Clear completed rows from the grid."""
    inc = 0
    for i in range(len(grid) - 1, -1, -1):
        if (0, 0, 0) not in grid[i]:
            inc += 1
            ind = i
            for j in range(len(grid[i])):
                try:
                    del locked[(j, i)]
                except:
                    continue
    if inc > 0:
        # Shift rows down
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                new_key = (x, y + inc)
                locked[new_key] = locked.pop(key)

def draw_next_shape(shape, surface):
    """Draw the next shape on the side."""
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', True, (255, 255, 255))
    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]
    for i, line in enumerate(format):
        for j, column in enumerate(list(line)):
            if column == '0':
                pygame.draw.rect(
                    surface, shape.color,
                    (sx + j * block_size, sy + i * block_size, block_size, block_size)
                )
    surface.blit(label, (sx + 10, sy - 30))

def draw_window(surface, grid, score=0):
    """Draw the main game window."""
    surface.fill((0, 0, 0))
    # Title
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('Tetris', True, (255, 255, 255))
    surface.blit(
        label,
        (top_left_x + play_width / 2 - label.get_width() / 2, 30)
    )
    # Current score
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render(f'Score: {score}', True, (255, 255, 255))
    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 150
    surface.blit(label, (sx + 20, sy + 160))
    # Draw grid
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(
                surface, grid[i][j],
                (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size)
            )
    # Grid and border
    draw_grid(surface, grid)
    pygame.draw.rect(
        surface, (255, 0, 0),
        (top_left_x, top_left_y, play_width, play_height), 5
    )

def main():
    """Main game loop."""
    global win
    locked_positions = {}
    grid = create_grid(locked_positions)
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5
    level_time = 0
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        # Increase speed over time
        if level_time / 1000 > 5:
            level_time = 0
            if fall_speed > 0.15:
                fall_speed -= 0.005

        # Piece falls
        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x +=1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x +=1
                    if not valid_space(current_piece, grid):
                        current_piece.x -=1
                elif event.key == pygame.K_DOWN:
                    current_piece.y +=1
                    if not valid_space(current_piece, grid):
                        current_piece.y -=1
                elif event.key == pygame.K_UP:
                    current_piece.rotation +=1
                    if not valid_space(current_piece, grid):
                        current_piece.rotation -=1

        shape_pos = convert_shape_format(current_piece)

        # Add piece to grid
        for pos in shape_pos:
            x, y = pos
            if y > -1:
                grid[y][x] = current_piece.color

        # Check if piece should lock in place
        if change_piece:
            for pos in shape_pos:
                locked_positions[(pos[0], pos[1])] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            # Clear rows and update score
            cleared = clear_rows(grid, locked_positions)
            if cleared:
                score += cleared * 10

        draw_window(win, grid, score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        # Check for game over
        if check_lost(locked_positions):
            draw_text_middle(win, "GAME OVER", 80, (255, 255, 255))
            pygame.display.update()
            pygame.time.delay(2000)
            run = False

def main_menu():
    """Display the main menu."""
    global win
    win = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Tetris by ChatGPT')
    run = True
    while run:
        win.fill((0, 0, 0))
        draw_text_middle(win, 'Press Any Key To Play', 60, (255, 255, 255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False
            if event.type == pygame.KEYDOWN:
                main()
    pygame.quit()

if __name__ == '__main__':
    main_menu()

