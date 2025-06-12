import os
import pygame
from .base_state import GameState
from src.persistence import SaveManager
from ..config import TOTAL_LEVELS


class LevelSelectState(GameState):
    def __init__(self, game):
        """Initialize level select screen: background, buttons, stars, and layout."""
        super().__init__(game)
        self.screen_width, self.screen_height = game.screen.get_size()

        # Load and scale background image
        bg = pygame.image.load(
            os.path.join("assets", "images", "level_select", "background.png")
        ).convert_alpha()
        self.background = pygame.transform.smoothscale(
            bg, (self.screen_width, self.screen_height)
        )

        # Load and scale title image
        title = pygame.image.load(
            os.path.join("assets", "images", "level_select", "title.png")
        ).convert_alpha()
        title_w = int(self.screen_width * 0.47)
        title_h = int(self.screen_height * 0.097)
        self.title_image = pygame.transform.smoothscale(title, (title_w, title_h))
        title_x = int(self.screen_width * 0.265)
        title_y = int(self.screen_height * 0.081)
        self.title_rect = pygame.Rect(title_x, title_y, title_w, title_h)

        # Load and scale star icons (lit and unlit)
        star_lit = pygame.image.load(
            os.path.join("assets", "images", "level_select", "star", "1.png")
        ).convert_alpha()
        star_unlit = pygame.image.load(
            os.path.join("assets", "images", "level_select", "star", "2.png")
        ).convert_alpha()
        star_w = int(self.screen_width * 0.0259)
        star_h = int(self.screen_height * 0.0369)
        self.star_lit = pygame.transform.smoothscale(star_lit, (star_w, star_h))
        self.star_unlit = pygame.transform.smoothscale(star_unlit, (star_w, star_h))

        # Prepare level buttons with positions
        self.level_buttons = []
        btn_w = int(self.screen_width * 0.074)
        btn_h = int(self.screen_height * 0.108)
        base_x = int(self.screen_width * 0.195)
        base_y = int(self.screen_height * 0.27)
        x_offset = int(self.screen_width * 0.135)
        y_offset = int(self.screen_height * 0.18)

        # Load button images for normal, hover, and locked states
        normal_btn = pygame.image.load(
            os.path.join("assets", "images", "level_select", "level", "1.png")
        ).convert_alpha()
        hover_btn = pygame.image.load(
            os.path.join("assets", "images", "level_select", "level", "2.png")
        ).convert_alpha()
        locked_btn = pygame.image.load(
            os.path.join("assets", "images", "level_select", "level", "3.png")
        ).convert_alpha()
        self.btn_img_normal = pygame.transform.smoothscale(normal_btn, (btn_w, btn_h))
        self.btn_img_hover = pygame.transform.smoothscale(hover_btn, (btn_w, btn_h))
        self.btn_img_locked = pygame.transform.smoothscale(locked_btn, (btn_w, btn_h))

        # Create a grid of level button rects and associate level numbers
        for i in range(TOTAL_LEVELS):
            row, col = divmod(i, 5)
            x = base_x + col * x_offset
            y = base_y + row * y_offset
            rect = pygame.Rect(x, y, btn_w, btn_h)
            self.level_buttons.append((rect, i + 1))

        # Track hover state per button
        self.hover_states = [False] * len(self.level_buttons)

        # Precompute star positions for each level
        self.star_positions = []
        star_base_y = int(self.screen_height * 0.39)
        star_x_offsets = [
            self.screen_width * 0.189,
            self.screen_width * 0.219,
            self.screen_width * 0.249,
        ]
        for i in range(TOTAL_LEVELS):
            row = i // 5
            y = int(star_base_y + row * (self.screen_height * 0.18))
            x_base = (i % 5) * (self.screen_width * 0.135)
            positions = [(int(off + x_base), y) for off in star_x_offsets]
            self.star_positions.append(positions)

        # Initialize ratings and unlocked level (loaded in enter())
        self.level_ratings = [0] * TOTAL_LEVELS
        self.unlocked = 1

        # Load and scale back button images and set its rect
        back_norm = pygame.image.load(
            os.path.join("assets", "images", "level_select", "back", "1.png")
        ).convert_alpha()
        back_hover = pygame.image.load(
            os.path.join("assets", "images", "level_select", "back", "2.png")
        ).convert_alpha()
        back_w = int(self.screen_width * 0.05)
        back_h = int(self.screen_height * 0.056)
        self.back_img_normal = pygame.transform.smoothscale(back_norm, (back_w, back_h))
        self.back_img_hover = pygame.transform.smoothscale(back_hover, (back_w, back_h))
        bx = int(self.screen_width * 0.11)
        by = int(self.screen_height * 0.8)
        self.back_button_rect = pygame.Rect(bx, by, back_w, back_h)
        self.back_hover = False

        # Font for level numbers
        font_path = os.path.join("assets", "fonts", "PixelFun-Regular.ttf")
        self.font = pygame.font.Font(font_path, 44)
        self.level_text_color = pygame.Color("#594842")

    def enter(self):
        """Load progress data: unlocked level and ratings."""
        prog = SaveManager.load_progress(num_levels=TOTAL_LEVELS)
        self.unlocked = prog["unlocked"]
        self.level_ratings = prog["ratings"]

    def exit(self):
        """No cleanup required on exit."""
        pass

    def handle_event(self, event):
        """Handle clicks on back button and unlocked level buttons."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Back to main menu
            if self.back_button_rect.collidepoint(mx, my):
                self.game.change_state("main_menu")
                return

            # Start selected level if unlocked
            for idx, (rect, level_num) in enumerate(self.level_buttons):
                if level_num <= self.unlocked and rect.collidepoint(mx, my):
                    play_state = self.game.states["play"]
                    play_state.load_level(level_num)
                    self.game.change_state("play")
                    return

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state("main_menu")

    def update(self, dt):
        """Update hover states for level buttons and back button."""
        mx, my = pygame.mouse.get_pos()
        for idx, (rect, level_num) in enumerate(self.level_buttons):
            self.hover_states[idx] = (level_num <= self.unlocked and rect.collidepoint(mx, my))
        self.back_hover = self.back_button_rect.collidepoint(mx, my)

    def draw(self, screen):
        """Render background, title, level buttons, stars, and back button."""
        screen.blit(self.background, (0, 0))
        screen.blit(self.title_image, self.title_rect)

        # Draw each level button with number and stars
        for idx, (rect, level_num) in enumerate(self.level_buttons):
            if level_num > self.unlocked:
                # Locked state
                screen.blit(self.btn_img_locked, rect.topleft)
            else:
                # Unlocked: choose normal or hover image
                img = self.btn_img_hover if self.hover_states[idx] else self.btn_img_normal
                screen.blit(img, rect.topleft)

            # Draw level number
            num_surf = self.font.render(str(level_num), True, self.level_text_color)
            screen.blit(num_surf, num_surf.get_rect(center=rect.center))

            # Draw star ratings
            for star_idx, (sx, sy) in enumerate(self.star_positions[idx]):
                star_img = self.star_lit if star_idx < self.level_ratings[idx] else self.star_unlit
                screen.blit(star_img, (sx, sy))

        # Draw back button
        back_img = self.back_img_hover if self.back_hover else self.back_img_normal
        screen.blit(back_img, self.back_button_rect.topleft)
