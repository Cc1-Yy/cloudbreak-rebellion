import os
import sys
import pygame

from src.config import TOTAL_LEVELS
from src.engine import Game
from src.persistence import SaveManager

# Ensure working directory is the project root
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def main():
    """Initialize pygame, create the main window and run the event loop."""
    pygame.init()

    # Create the game window with a fixed resolution
    screen = pygame.display.set_mode((1536, 1024))
    pygame.display.set_caption("Cloudbreak Rebellion")

    # Clock to cap the frame rate
    clock = pygame.time.Clock()

    running = True
    while running:
        # Process all events in the event queue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear the screen (fill with black)
        screen.fill((0, 0, 0))

        # Update the full display surface to the screen
        pygame.display.flip()

        # Maintain a maximum of 60 frames per second
        clock.tick(60)

    # Clean up and exit
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    # Reset saved progress to include all levels at startup
    SaveManager.reset_progress(TOTAL_LEVELS)

    # Instantiate and run the main game loop
    game = Game()
    game.run()
