import pygame

from src.config import TOTAL_LEVELS
from src.persistence import SaveManager
from src.state.main_menu_state import MainMenuState
from src.state.play_state import PlayState
from src.state.instructions_state import InstructionsState
from src.state.level_select_state import LevelSelectState
from src.state.load_save_state import LoadSaveState
from src.state.game_over_state import GameOverState
from src.state.game_clear_state import GameClearState
from src.state.pause_state import PauseState


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1536, 1024))
        pygame.display.set_caption("Cloudbreak Rebellion")
        self.clock = pygame.time.Clock()

        self.states = {
            "main_menu": MainMenuState(self),
            "play": PlayState(self),
            "instructions": InstructionsState(self),
            "level_select": LevelSelectState(self),
            "load_save": LoadSaveState(self),
            "game_over": GameOverState(self),
            "game_clear": GameClearState(self),
            "pause": PauseState(self),
        }

        self.state_stack = []

    def push_state(self, state_name):

        state = self.states[state_name]
        self.state_stack.append(state)
        state.enter()

    def pop_state(self):

        if not self.state_stack:
            return
        state = self.state_stack.pop()
        state.exit()

    def change_state(self, state_name):
        while self.state_stack:
            old = self.state_stack.pop()
            old.exit()
        self.push_state(state_name)

    def run(self):
        self.push_state("main_menu")

        running = True

        while running:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.state_stack[-1].handle_event(event)

            self.state_stack[-1].update(dt)
            self.screen.fill((0, 0, 0))
            self.state_stack[-1].draw(self.screen)
            pygame.display.flip()

        SaveManager.reset_progress(num_levels=TOTAL_LEVELS)
        pygame.quit()