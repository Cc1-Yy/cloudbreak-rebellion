import pygame

from .config import TOTAL_LEVELS
from .persistence import SaveManager
from .state.main_menu_state import MainMenuState
from .state.play_state import PlayState
from .state.instructions_state import InstructionsState
from .state.level_select_state import LevelSelectState
from .state.load_save_state import LoadSaveState
from .state.game_over_state import GameOverState
from .state.game_clear_state import GameClearState
from .state.pause_state import PauseState


class Game:
    def __init__(self):
        """Initialize pygame, create window, clock, and all game states."""
        pygame.init()
        self.screen = pygame.display.set_mode((1536, 1024))
        pygame.display.set_caption("Cloudbreak Rebellion")
        self.clock = pygame.time.Clock()

        # Instantiate all game states and store them in a dictionary
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

        # State stack for push/pop transitions
        self.state_stack = []

    def push_state(self, state_name):
        """
        Push a new state onto the stack and call its enter() method.
        Underlying states remain in memory but are not updated or drawn.
        """
        state = self.states[state_name]
        self.state_stack.append(state)
        state.enter()

    def pop_state(self):
        """
        Pop the current state from the stack and call its exit() method.
        Resumes the next state on top of the stack, if any.
        """
        if not self.state_stack:
            return
        state = self.state_stack.pop()
        state.exit()

    def change_state(self, state_name):
        """
        Completely switch to a new state:
        Exit and clear all current states, then push the target state.
        """
        # Exit and clear all active states
        while self.state_stack:
            old_state = self.state_stack.pop()
            old_state.exit()
        # Enter the new state
        self.push_state(state_name)

    def run(self):
        """Main game loop: handle events, update, draw, and manage state transitions."""
        # Start with the main menu state
        self.push_state("main_menu")

        running = True
        while running:
            # Calculate delta time in seconds
            dt = self.clock.tick(60) / 1000.0

            # Dispatch events to the top state
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    self.state_stack[-1].handle_event(event)

            # Update and draw the top state
            self.state_stack[-1].update(dt)
            self.screen.fill((0, 0, 0))
            self.state_stack[-1].draw(self.screen)
            pygame.display.flip()

        # Reset progress and clean up on exit
        SaveManager.reset_progress(num_levels=TOTAL_LEVELS)
        pygame.quit()
