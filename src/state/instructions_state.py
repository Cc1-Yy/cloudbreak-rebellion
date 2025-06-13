import pygame
from src.state.base_state import GameState


class InstructionsState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.screen_width, self.screen_height = game.screen.get_size()

        pygame.font.init()
        fp = "assets/fonts/PixelFun-Regular.ttf"

        self.text_font = pygame.font.Font(fp, 40)

        bg_path = "assets/images/instructions/background.png"
        self.bg = pygame.transform.smoothscale(
            pygame.image.load(bg_path).convert_alpha(),
            (self.screen_width, self.screen_height)
        )
        self.lines = [
            "",
            "Story: ",
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
        pass

    def exit(self):
        pass

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state("main_menu")

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))

        start_y = 200
        line_h = self.text_font.get_height()
        for i, line in enumerate(self.lines):
            surf = self.text_font.render(line, True, "#594842")
            x = 180
            y = start_y + i * line_h
            screen.blit(surf, (x, y))
