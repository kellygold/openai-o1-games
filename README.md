
# Python Games Collection

This repository contains classic games developed in Python using Pygame. Each game is ready to play and can be easily customized.

I built these in September 2024 to see what OpenAI's o1 model could produce from short prompts. The write-up is on Medium: [Building Games With OpenAI's o1 Model](https://medium.com/@kellytgold/building-games-with-openais-o1-model-da3fc8d1a4e6).

## Games Included

- **Flappy Bird**: Navigate the bird through pipes.
  - Path: `flappy_bird/flappy_bird.py`
  
- **Snake**: Classic snake game where you collect food to grow.
  - Path: `snake/snake.py`
  
- **Solitaire**: A basic solitaire card game.
  - Path: `solitare/solitare.py`
  - Assets: Card images in `solitare/playingcards/`
  
- **Space Invaders**: Shoot down the aliens before they reach Earth.
  - Path: `space_invaders/space_invaders_full_game.py`
  
- **Platform Fighter**: Inspired by Super Smash Bros., battle the AI on platforms.
  - Path: `super_smash/super_smash_final.py`
  
- **Tetris**: Arrange falling tetrominoes to clear lines.
  - Path: `tetris/tetris.py`

## How to Run

### Prerequisites

- Install Python 3.x
- Install Pygame:

  ```bash
  pip install pygame
  ```

### Running a Game

1. Clone the repository:

   ```bash
   git clone https://github.com/kellygold/openai-o1-games.git
   cd openai-o1-games
   ```

2. Navigate to the game folder and run the game:

   ```bash
   cd flappy_bird
   python flappy_bird.py
   ```

   Replace `flappy_bird` with the folder of the game you want to play.


