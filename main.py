import os
import sys
import pygame

from src.config import TOTAL_LEVELS
from src.engine import Game
from src.persistence import SaveManager

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def main():
    pygame.init()
    screen = pygame.display.set_mode((1536, 1024))
    pygame.display.set_caption("Cloudbreak Rebellion")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 0))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    SaveManager.reset_progress(TOTAL_LEVELS)
    game = Game()
    game.run()
