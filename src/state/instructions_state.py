import pygame
from src.state.base_state import GameState


class InstructionsState(GameState):
    def __init__(self, game):
        """Initialize instruction screen: load background and prepare text."""
        super().__init__(game)
        self.screen_width, self.screen_height = game.screen.get_size()

        # Initialize font for instructions text
        pygame.font.init()
        font_path = "assets/fonts/PixelFun-Regular.ttf"
        self.text_font = pygame.font.Font(font_path, 40)

        # Load and scale background image
        bg_path = "assets/images/instructions/background.png"
        bg_raw = pygame.image.load(bg_path).convert_alpha()
        self.bg = pygame.transform.smoothscale(bg_raw, (self.screen_width, self.screen_height))

        # Instruction text lines
        self.lines = [
            "",
            "Story:",
            "In the lost floating archipelago, you are a brave",
            "warrior on a quest to restore balance and reclaim",
            "the skies from tyranny.",
            "",
            "Controls:",
            "  ← / A    Move Left",
            "  → / D    Move Right",
            "  ↑ / W    Jump",
            "  SPACE    Shoot Arrow",
            "  ESC      Pause",
            "",
            "Press ESC to return to the Main Menu"
        ]

    def enter(self):
        """No special action on entering the instructions state."""
        pass

    def exit(self):
        """No special cleanup on exiting the instructions state."""
        pass

    def handle_event(self, event):
        """Return to main menu when ESC key is pressed."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state("main_menu")

    def update(self, dt):
        """No dynamic update needed for instructions screen."""
        pass

    def draw(self, screen):
        """Render background and instruction text lines."""
        screen.blit(self.bg, (0, 0))
        start_y = 200
        line_height = self.text_font.get_height()
        x = 180
        for i, line in enumerate(self.lines):
            surf = self.text_font.render(line, True, "#594842")
            y = start_y + i * line_height
            screen.blit(surf, (x, y))
