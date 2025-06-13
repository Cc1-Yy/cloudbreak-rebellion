

import os
import pygame
from src.state.base_state import GameState
from src.persistence import SaveManager
from src.config import TOTAL_LEVELS


class LevelSelectState(GameState):
    def __init__(self, game):
        super().__init__(game)

        self.screen_width, self.screen_height = self.game.screen.get_size()

        bg_raw = pygame.image.load(
            os.path.join("assets", "images", "level_select", "background.png")
        ).convert_alpha()
        self.background = pygame.transform.smoothscale(
            bg_raw,
            (self.screen_width, self.screen_height)
        )

        title_raw = pygame.image.load(
            os.path.join("assets", "images", "level_select", "title.png")
        ).convert_alpha()
        title_w = int(self.screen_width * 0.47)
        title_h = int(self.screen_height * 0.097)
        self.title_image = pygame.transform.smoothscale(title_raw, (title_w, title_h))
        title_x = int(self.screen_width * 0.265)
        title_y = int(self.screen_height * 0.081)
        self.title_rect = pygame.Rect(title_x, title_y, title_w, title_h)

        star_lit_raw = pygame.image.load(
            os.path.join("assets", "images", "level_select", "star", "1.png")
        ).convert_alpha()
        star_unlit_raw = pygame.image.load(
            os.path.join("assets", "images", "level_select", "star", "2.png")
        ).convert_alpha()
        star_w = int(self.screen_width * 0.0259)
        star_h = int(self.screen_height * 0.0369)
        self.star_lit = pygame.transform.smoothscale(star_lit_raw, (star_w, star_h))
        self.star_unlit = pygame.transform.smoothscale(star_unlit_raw, (star_w, star_h))

        self.level_buttons = []
        btn_w = int(self.screen_width * 0.074)
        btn_h = int(self.screen_height * 0.108)
        base_y_row1 = int(self.screen_height * 0.27)
        base_x_col1 = int(self.screen_width * 0.195)
        x_offset = int(self.screen_width * 0.135)
        y_offset = int(self.screen_height * 0.18)

        btn_normal_raw = pygame.image.load(
            os.path.join("assets", "images", "level_select", "level", "1.png")
        ).convert_alpha()
        btn_hover_raw = pygame.image.load(
            os.path.join("assets", "images", "level_select", "level", "2.png")
        ).convert_alpha()
        self.btn_img_normal = pygame.transform.smoothscale(btn_normal_raw, (btn_w, btn_h))
        self.btn_img_hover = pygame.transform.smoothscale(btn_hover_raw, (btn_w, btn_h))

        btn_locked_raw = pygame.image.load(
            os.path.join("assets", "images", "level_select", "level", "3.png")
        ).convert_alpha()
        self.btn_img_locked = pygame.transform.smoothscale(btn_locked_raw, (btn_w, btn_h))

        for i in range(TOTAL_LEVELS):
            row = i // 5
            col = i % 5
            x = base_x_col1 + col * x_offset
            y = base_y_row1 + row * y_offset
            rect = pygame.Rect(x, y, btn_w, btn_h)
            self.level_buttons.append((rect, i + 1))

        self.hover_states = [False] * len(self.level_buttons)

        self.star_positions = []
        base_star_y_row1 = int(self.screen_height * 0.39)
        base_star_x_offsets = [
            self.screen_width * 0.189,
            self.screen_width * 0.219,
            self.screen_width * 0.249,
        ]
        for i in range(TOTAL_LEVELS):
            row = i // 5
            star_y = int(base_star_y_row1 + row * (self.screen_height * 0.18))
            col = i % 5
            x_base = col * (self.screen_width * 0.135)
            pos = [(int(offset + x_base), star_y) for offset in base_star_x_offsets]
            self.star_positions.append(pos)

        self.level_ratings = [0] * TOTAL_LEVELS

        self.unlocked = 1

        back_normal_raw = pygame.image.load(
            os.path.join("assets", "images", "level_select", "back", "1.png")
        ).convert_alpha()
        back_hover_raw = pygame.image.load(
            os.path.join("assets", "images", "level_select", "back", "2.png")
        ).convert_alpha()
        back_w = int(self.screen_width * 0.05)
        back_h = int(self.screen_height * 0.056)
        self.back_img_normal = pygame.transform.smoothscale(back_normal_raw, (back_w, back_h))
        self.back_img_hover = pygame.transform.smoothscale(back_hover_raw, (back_w, back_h))
        back_x = int(self.screen_width * 0.11)
        back_y = int(self.screen_height * 0.8)
        self.back_button_rect = pygame.Rect(back_x, back_y, back_w, back_h)
        self.back_hover = False

        self.font = pygame.font.Font(
            os.path.join("assets", "fonts", "PixelFun-Regular.ttf"),
            44
        )
        self.level_text_color = pygame.Color("#594842")

    def enter(self):

        prog = SaveManager.load_progress(num_levels=len(self.level_buttons))
        self.unlocked = prog["unlocked"]
        self.level_ratings = prog["ratings"]

    def exit(self):
        pass

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if self.back_button_rect.collidepoint(mx, my):
                self.game.change_state("main_menu")
                return

            for idx, (rect, lvl_num) in enumerate(self.level_buttons):
                if lvl_num <= self.unlocked and rect.collidepoint(mx, my):
                    play_state = self.game.states["play"]
                    play_state.load_level(lvl_num)
                    self.game.change_state("play")
                    return

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state("main_menu")

    def update(self, dt):
        mx, my = pygame.mouse.get_pos()

        for idx, (rect, lvl_num) in enumerate(self.level_buttons):
            self.hover_states[idx] = (lvl_num <= self.unlocked and rect.collidepoint(mx, my))

        self.back_hover = self.back_button_rect.collidepoint(mx, my)

    def draw(self, screen):

        screen.blit(self.background, (0, 0))
        screen.blit(self.title_image, self.title_rect)

        for idx, (rect, lvl_num) in enumerate(self.level_buttons):
            if lvl_num > self.unlocked:

                screen.blit(self.btn_img_locked, rect.topleft)
            else:

                img = self.btn_img_hover if self.hover_states[idx] else self.btn_img_normal
                screen.blit(img, rect.topleft)

            text_surf = self.font.render(str(lvl_num), True, self.level_text_color)
            screen.blit(text_surf, text_surf.get_rect(center=rect.center))

            for s_i, (sx, sy) in enumerate(self.star_positions[idx]):
                star_img = self.star_lit if s_i < self.level_ratings[idx] else self.star_unlit
                screen.blit(star_img, (sx, sy))

        back_img = self.back_img_hover if self.back_hover else self.back_img_normal
        screen.blit(back_img, self.back_button_rect.topleft)