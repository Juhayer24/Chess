Python Chess Game with AI
This repository contains a comprehensive chess game developed in Python, leveraging the Pygame library for its graphical interface. The game offers both a two-player mode and a single-player mode against an AI opponent, with robust rule enforcement and a focus on an engaging user experience.

Features
Game Modes: Supports Player vs. Player and Player vs. AI modes.

AI Opponent: Integrated AI powered by the Minimax algorithm with Alpha-Beta Pruning, offering adjustable difficulty levels (Easy, Medium, Hard) through configurable search depth.

Rule Enforcement: Strict adherence to FIDE chess rules, including move validation, castling, en passant, and pawn promotion.

Game State Management: Tracks move history, enables undo functionality, and detects check and checkmate conditions.

User Interface: Provides clear turn indicators, displays captured pieces, and presents real-time player statistics.

Visuals & Audio: Features custom board and piece designs rendered with Pygame, complemented by sound effects for game actions.

AI Implementation
The AI opponent is built upon the classic Minimax algorithm, enhanced with Alpha-Beta Pruning for computational efficiency.

Evaluation Function: Employs a material-based scoring system for board evaluation (e.g., Queen = 9, Rook = 5, Bishop/Knight = 3, Pawn = 1).

Adjustable Depth: The AI's difficulty is directly controlled by the search depth of the Minimax algorithm, allowing users to select their preferred challenge.

Threaded Computation: AI move calculations are performed in a separate thread to ensure a smooth and responsive user interface, preventing freezing during intensive computations.

File Structure
.
├── main.py             # Main entry point for the game application
├── ai.py               # Contains the AI logic, including Minimax and Alpha-Beta Pruning implementations
├── board.py            # Manages the game board state, legal move generation, and rule enforcement
├── constants.py        # Defines global constants such as colors, dimensions, and frames per second
├── models.py           # Defines data models for game entities, including pieces and game state
├── ui.py               # Handles all graphical rendering functions for the board, pieces, and side panel
├── utils.py            # Provides utility functions, including sound management and initial setup
├── assets/             # Directory containing images for chess pieces and sound files
└── README.md           # Project documentation
Requirements
Python 3.7+

Pygame library

Installation
To install the necessary dependencies, execute the following command:

Bash

pip install pygame
How to Run
Navigate to the project's root directory in your terminal and execute the main.py file:

Bash

python main.py

<img src="https://github.com/user-attachments/assets/1a59c7b2-11e7-492d-bf9e-f923c58d00b8">
<img src="https://github.com/user-attachments/assets/02fdbe9d-0818-4143-829e-60d46a3223c5">
<img src="https://github.com/user-attachments/assets/d95d7598-75d9-414e-b42e-c6ddd9b14480">

