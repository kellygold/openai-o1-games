import pygame
import sys
import os
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Klondike Solitaire')

# Define colors
GREEN = (0, 128, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Card dimensions
CARD_WIDTH = 72
CARD_HEIGHT = 96

# Load card images
def load_card_images():
    suits = {
        'spades': 'S',
        'hearts': 'H',
        'diamonds': 'D',
        'clubs': 'C'
    }
    ranks = {
        'ace': 'A',
        '2': '2',
        '3': '3',
        '4': '4',
        '5': '5',
        '6': '6',
        '7': '7',
        '8': '8',
        '9': '9',
        '10': '10',
        'jack': 'J',
        'queen': 'Q',
        'king': 'K'
    }
    images = {}
    # Directory containing your card images
    card_dir = 'playingcards/PNG-cards-1.3'
    for filename in os.listdir(card_dir):
        if filename.endswith('.png'):
            # Extract rank and suit from filename
            name_parts = filename[:-4].split('_of_')
            if len(name_parts) == 2:
                rank_name, suit_name = name_parts
                rank = ranks.get(rank_name)
                suit = suits.get(suit_name)
                if rank and suit:
                    key = f'{rank}{suit}'
                    filepath = os.path.join(card_dir, filename)
                    image = pygame.image.load(filepath).convert_alpha()
                    image = pygame.transform.scale(image, (CARD_WIDTH, CARD_HEIGHT))
                    images[key] = image
    # Generate card back image
    back_image = generate_card_back()
    images['back'] = back_image
    return images

def generate_card_back():
    """Generate a simple card back image."""
    back_surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
    back_surface.fill((0, 0, 255))  # Blue color
    pygame.draw.rect(back_surface, BLACK, back_surface.get_rect(), 2)
    return back_surface

card_images = load_card_images()

# Card class
class Card:
    def __init__(self, suit, rank, face_up=False):
        self.suit = suit
        self.rank = rank
        self.face_up = face_up
        self.image = self.get_image()
        self.rect = self.image.get_rect()
        self.dragging = False

    def get_image(self):
        if self.face_up:
            key = f'{self.rank}{self.suit}'
            return card_images[key]
        else:
            return card_images['back']

    def flip(self):
        self.face_up = not self.face_up
        self.image = self.get_image()

# Create deck
def create_deck():
    suits = ['S', 'H', 'D', 'C']  # Spades, Hearts, Diamonds, Clubs
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    deck = [Card(suit, rank) for suit in suits for rank in ranks]
    random.shuffle(deck)
    return deck

# Initialize game
def initialize_game():
    deck = create_deck()
    tableau = [[] for _ in range(7)]
    foundations = [[] for _ in range(4)]
    waste_pile = []
    stock_pile = deck

    # Deal cards to tableau
    for i in range(7):
        for j in range(i + 1):
            card = stock_pile.pop()
            face_up = (j == i)
            card.face_up = face_up
            card.image = card.get_image()
            tableau[i].append(card)

    return stock_pile, waste_pile, tableau, foundations

# Draw functions
def draw_tableau(screen, tableau):
    x_offset = 50
    y_offset = 200
    for pile in tableau:
        y = y_offset
        for card in pile:
            card.rect.topleft = (x_offset, y)
            screen.blit(card.image, card.rect)
            if card.face_up:
                y += 20
            else:
                y += 5
        x_offset += 100

def draw_foundations(screen, foundations):
    x_offset = 400
    y_offset = 50
    for foundation in foundations:
        if foundation:
            card = foundation[-1]
            card.rect.topleft = (x_offset, y_offset)
            screen.blit(card.image, card.rect)
        else:
            pygame.draw.rect(screen, WHITE, (x_offset, y_offset, CARD_WIDTH, CARD_HEIGHT), 2)
        x_offset += 100

def draw_stock_pile(screen, stock_pile):
    x_offset = 50
    y_offset = 50
    if stock_pile:
        back_image = card_images['back']
        screen.blit(back_image, (x_offset, y_offset))
    else:
        pygame.draw.rect(screen, WHITE, (x_offset, y_offset, CARD_WIDTH, CARD_HEIGHT), 2)

def draw_waste_pile(screen, waste_pile):
    x_offset = 150
    y_offset = 50
    if waste_pile:
        card = waste_pile[-1]
        card.rect.topleft = (x_offset, y_offset)
        screen.blit(card.image, card.rect)
    else:
        pygame.draw.rect(screen, WHITE, (x_offset, y_offset, CARD_WIDTH, CARD_HEIGHT), 2)

# Main game loop
def main():
    stock_pile, waste_pile, tableau, foundations = initialize_game()
    running = True
    clock = pygame.time.Clock()
    selected_card = None
    selected_pile = None
    offset_x = 0
    offset_y = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Mouse events
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # Check stock pile click
                if stock_pile and pygame.Rect(50, 50, CARD_WIDTH, CARD_HEIGHT).collidepoint(pos):
                    card = stock_pile.pop()
                    card.face_up = True
                    card.image = card.get_image()
                    waste_pile.append(card)
                # Check waste pile click
                elif waste_pile:
                    card = waste_pile[-1]
                    if card.rect.collidepoint(pos):
                        selected_card = card
                        selected_pile = waste_pile
                        offset_x = card.rect.x - pos[0]
                        offset_y = card.rect.y - pos[1]
                        card.dragging = True
                # Check tableau click
                for pile in tableau:
                    if pile:
                        for i in range(len(pile)):
                            card = pile[i]
                            if card.face_up and card.rect.collidepoint(pos):
                                selected_card = card
                                selected_pile = pile
                                offset_x = card.rect.x - pos[0]
                                offset_y = card.rect.y - pos[1]
                                card.dragging = True
                                break
                # Check foundations click
                for foundation in foundations:
                    if foundation:
                        card = foundation[-1]
                        if card.rect.collidepoint(pos):
                            selected_card = card
                            selected_pile = foundation
                            offset_x = card.rect.x - pos[0]
                            offset_y = card.rect.y - pos[1]
                            card.dragging = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if selected_card:
                    pos = pygame.mouse.get_pos()
                    # Check for drop on foundations
                    dropped = False
                    x_offset = 400
                    y_offset = 50
                    for foundation in foundations:
                        foundation_rect = pygame.Rect(x_offset, y_offset, CARD_WIDTH, CARD_HEIGHT)
                        if foundation_rect.collidepoint(pos):
                            if can_move_to_foundation(selected_card, foundation):
                                move_to_foundation(selected_card, selected_pile, foundation)
                                dropped = True
                            break
                        x_offset += 100
                    # Check for drop on tableau
                    if not dropped:
                        x_offset = 50
                        y_offset = 200
                        for pile in tableau:
                            if pile:
                                rect = pile[-1].rect
                            else:
                                rect = pygame.Rect(x_offset, y_offset, CARD_WIDTH, CARD_HEIGHT)
                            if rect.collidepoint(pos):
                                if can_move_to_tableau(selected_card, pile):
                                    move_to_tableau(selected_card, selected_pile, pile)
                                    dropped = True
                                break
                            x_offset += 100
                    # Return card to original pile if not dropped
                    if not dropped:
                        selected_card.rect.topleft = (selected_card.rect.x, selected_card.rect.y)
                    selected_card.dragging = False
                    selected_card = None
                    selected_pile = None

            elif event.type == pygame.MOUSEMOTION:
                if selected_card and selected_card.dragging:
                    pos = pygame.mouse.get_pos()
                    selected_card.rect.x = pos[0] + offset_x
                    selected_card.rect.y = pos[1] + offset_y

        # Draw everything
        screen.fill(GREEN)
        draw_stock_pile(screen, stock_pile)
        draw_waste_pile(screen, waste_pile)
        draw_foundations(screen, foundations)
        draw_tableau(screen, tableau)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

# Game logic functions
def can_move_to_foundation(card, foundation):
    if not foundation:
        return card.rank == 'A'
    top_card = foundation[-1]
    return card.suit == top_card.suit and rank_value(card.rank) == rank_value(top_card.rank) + 1

def move_to_foundation(card, source_pile, foundation):
    idx = source_pile.index(card)
    moving_cards = source_pile[idx:]
    foundation.extend(moving_cards)
    del source_pile[idx:]
    if source_pile and not source_pile[-1].face_up:
        source_pile[-1].flip()

def can_move_to_tableau(card, pile):
    if not pile:
        return card.rank == 'K'
    top_card = pile[-1]
    return is_alternate_color(card, top_card) and rank_value(card.rank) == rank_value(top_card.rank) - 1

def move_to_tableau(card, source_pile, target_pile):
    idx = source_pile.index(card)
    moving_cards = source_pile[idx:]
    target_pile.extend(moving_cards)
    del source_pile[idx:]
    if source_pile and not source_pile[-1].face_up:
        source_pile[-1].flip()

def is_alternate_color(card1, card2):
    red_suits = ['H', 'D']
    black_suits = ['S', 'C']
    return (card1.suit in red_suits and card2.suit in black_suits) or (card1.suit in black_suits and card2.suit in red_suits)

def rank_value(rank):
    ranks = {'A':1, '2':2, '3':3, '4':4, '5':5,
             '6':6, '7':7, '8':8, '9':9, '10':10,
             'J':11, 'Q':12, 'K':13}
    return ranks[rank]

if __name__ == '__main__':
    main()

