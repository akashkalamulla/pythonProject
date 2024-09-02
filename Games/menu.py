import pygame
import sys
import os
import subprocess

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Game Menu')

# Define menu options
menu_options = [
    'Start Game 1',
    'Start Game 2',
    'Start Game 3',
    'Start Game 4',
    'Start Game 5'
]

# Game paths
game_files = [
    'Game1/game.py',
    'Game2/test.py',
    'Game3/game.py',
    'game4.py',
    'Game5/test.py',
]

# Set positions for each menu option
font = pygame.font.Font(None, 50)
option_positions = [(100, 200 + i * 60) for i in range(len(menu_options))]

# Main menu loop
running = True
while running:
    screen.fill((0, 0, 0))  # Black background
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for i, pos in enumerate(option_positions):
                option_rect = font.render(menu_options[i], True, (255, 255, 255)).get_rect(topleft=pos)
                if option_rect.collidepoint(mouse_pos):
                    game_path = game_files[i]
                    if os.path.exists(game_path):
                        subprocess.run(["python", game_path])
                    else:
                        print(f"File not found: {game_path}")

    # Draw menu options
    for i, pos in enumerate(option_positions):
        text_surface = font.render(menu_options[i], True, (255, 255, 255))
        screen.blit(text_surface, pos)

    pygame.display.flip()
