
import os
import pygame
from src.state.base_state import GameState
from src.persistence import SaveManager


class GameClearState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.screen_width, self.screen_height = game.screen.get_size()

        bg_path = os.path.join("assets", "images", "level", "background_3.png")
        self.bg_image = pygame.image.load(bg_path).convert()

        gloopie_path = os.path.join("assets", "images", "main_menu", "gloopie.png")
        graw = pygame.image.load(gloopie_path).convert_alpha()
        gw = int(self.screen_width * 0.30)
        gh = int(self.screen_height * 0.28)
        self.gloopie_image = pygame.transform.smoothscale(graw, (gw, gh))
        self.gloopie_rect = self.gloopie_image.get_rect(center=(
            self.screen_width // 2,
            int(self.screen_height * 0.15)
        ))

        overlay_w = int(self.screen_width * 0.8)
        overlay_h = int(self.screen_height * 0.7)
        overlay_x = (self.screen_width - overlay_w) // 2
        overlay_y = (self.screen_height - overlay_h) // 2 + 20
        self.overlay_rect = pygame.Rect(overlay_x, overlay_y, overlay_w, overlay_h)

        normal_path = os.path.join("assets", "images", "level", "buttons", "normal.png")
        hover_path = os.path.join("assets", "images", "level", "buttons", "hover.png")
        normal_raw = pygame.image.load(normal_path).convert_alpha()
        hover_raw = pygame.image.load(hover_path).convert_alpha()

        btn_w = int(self.screen_width * 0.28)
        btn_h = int(self.screen_height * 0.12)
        total_gap = overlay_w - 2 * btn_w
        margin = total_gap // 3
        y_btn = overlay_y + int(overlay_h * 0.73)

        x1 = overlay_x + margin
        x2 = overlay_x + margin * 2 + btn_w
        self.btn1_rect = pygame.Rect(x1, y_btn, btn_w, btn_h)
        self.btn2_rect = pygame.Rect(x2, y_btn, btn_w, btn_h)

        bx = overlay_x + (overlay_w - btn_w) // 2 - 0.028 * self.screen_width
        self.single_rect = pygame.Rect(bx, y_btn, btn_w, btn_h)

        self.btn_normal = pygame.transform.smoothscale(normal_raw, (btn_w, btn_h))
        self.btn_hover = pygame.transform.smoothscale(hover_raw, (btn_w, btn_h))

        self.btn1_hover = False
        self.btn2_hover = False
        self.single_hover = False

        self.text_color_normal = pygame.Color("#323232")
        self.text_color_hover = pygame.Color("#000000")

        self.max_hearts = 3
        self.remaining_hearts = 0
        self.total_gems = 3
        self.gem_count = 0
        self.star_count = 0

        self.level_index = 1

        self.icon_h = 36
        self.star_h = 78
        self.heart_full = pygame.transform.smoothscale(
            pygame.image.load(os.path.join("assets", "images", "level", "hud", "heart.png")).convert_alpha(),
            (self.icon_h, self.icon_h)
        )
        self.heart_empty = pygame.transform.smoothscale(
            pygame.image.load(os.path.join("assets", "images", "level", "hud", "heart_gray.png")).convert_alpha(),
            (self.icon_h, self.icon_h)
        )
        self.gem_full = pygame.transform.smoothscale(
            pygame.image.load(os.path.join("assets", "images", "level", "gem", "gem.png")).convert_alpha(),
            (self.icon_h, self.icon_h)
        )
        self.gem_empty = pygame.transform.smoothscale(
            pygame.image.load(os.path.join("assets", "images", "level", "gem", "gem_gray.png")).convert_alpha(),
            (self.icon_h, self.icon_h)
        )
        self.star_full = pygame.transform.smoothscale(
            pygame.image.load(os.path.join("assets", "images", "level", "star", "1.png")).convert_alpha(),
            (self.star_h, self.star_h)
        )
        self.star_empty = pygame.transform.smoothscale(
            pygame.image.load(os.path.join("assets", "images", "level", "star", "2.png")).convert_alpha(),
            (self.star_h, self.star_h)
        )

        self.font_title = None
        self.font_option = None

        self.is_last = False

    def enter(self):
        pygame.font.init()
        fp = os.path.join("assets", "fonts", "PixelFun-Regular.ttf")
        self.font_title = pygame.font.Font(fp, 100)
        self.font_option = pygame.font.Font(fp, 44)

        self.star_count = (self.remaining_hearts + self.gem_count) // 2

        prog = SaveManager.load_progress()
        idx = self.level_index - 1
        if self.star_count > prog["ratings"][idx]:
            prog["ratings"][idx] = self.star_count

        if self.level_index < len(prog["ratings"]) and self.level_index + 1 > prog["unlocked"]:
            prog["unlocked"] = self.level_index + 1
        SaveManager.save_progress(prog)

        self.is_last = (self.level_index == len(prog["ratings"]))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.is_last:

                if self.single_rect.collidepoint(mx, my):
                    self.game.change_state("main_menu")
            else:

                if self.btn1_rect.collidepoint(mx, my):
                    next_level = self.level_index + 1
                    play = self.game.states["play"]
                    play.load_level(next_level)
                    self.game.change_state("play")
                    return

                if self.btn2_rect.collidepoint(mx, my):
                    self.game.change_state("main_menu")
            return
        elif event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_p):

            self.game.change_state("main_menu")

    def update(self, dt):
        mx, my = pygame.mouse.get_pos()
        if self.is_last:
            self.single_hover = self.single_rect.collidepoint(mx, my)
        else:
            self.btn1_hover = self.btn1_rect.collidepoint(mx, my)
            self.btn2_hover = self.btn2_rect.collidepoint(mx, my)

    def draw(self, screen):

        bg = pygame.transform.scale(self.bg_image, (self.screen_width, self.screen_height))
        screen.blit(bg, (0, 0))

        overlay = pygame.Surface((self.overlay_rect.w, self.overlay_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (255, 255, 255, 153), overlay.get_rect(), border_radius=25)
        screen.blit(overlay, (self.overlay_rect.x, self.overlay_rect.y))

        screen.blit(self.gloopie_image, self.gloopie_rect)

        title_text = "Congratulations!" if self.is_last else "Level Clear!"
        title_surf = self.font_title.render(title_text, True, "#373737")
        title_rect = title_surf.get_rect(center=(
            self.screen_width // 2,
            self.overlay_rect.y + int(self.overlay_rect.h * (0.2 if not self.is_last else 0.2))
        ))
        screen.blit(title_surf, title_rect)

        start_x = 0.44 * self.screen_width
        start_y = self.overlay_rect.y + int(self.overlay_rect.h * 0.32)
        spacing = 12

        for i in range(self.max_hearts):
            icon = self.heart_full if i < self.remaining_hearts else self.heart_empty
            x = start_x + (i + 1) * (self.icon_h + spacing)
            screen.blit(icon, (x, start_y))
        heart_text = self.font_option.render("HUD", True, "#373737")
        hx = start_x - 0.04 * self.screen_width
        hy = start_y + (self.icon_h - heart_text.get_height()) // 2
        screen.blit(heart_text, (hx, hy))

        gem_y = start_y + self.icon_h + spacing * 2
        for j in range(self.total_gems):
            icon = self.gem_full if j < self.gem_count else self.gem_empty
            x = start_x + (j + 1) * (self.icon_h + spacing)
            screen.blit(icon, (x, gem_y))
        gem_text = self.font_option.render("GEM", True, "#373737")
        gx = start_x - 0.04 * self.screen_width
        gy = gem_y + (self.icon_h - gem_text.get_height()) // 2
        screen.blit(gem_text, (gx, gy))

        score_text = self.font_option.render("Score", True, "#373737")
        score_x = start_x - 0.02 * self.screen_width
        score_y = gem_y + self.star_h - spacing
        screen.blit(score_text, (score_x, score_y))

        star_y = score_y + self.font_option.get_height() + spacing
        for k in range(3):
            star = self.star_full if k < self.star_count else self.star_empty
            x = start_x + k * (self.star_h + spacing * 2) - 0.06 * self.screen_width
            screen.blit(star, (x, star_y))

        if self.is_last:
            img = self.btn_hover if self.single_hover else self.btn_normal
            screen.blit(img, self.single_rect.topleft)
            color = self.text_color_hover if self.single_hover else self.text_color_normal
            txt = self.font_option.render("Main Menu", True, color)
            r = txt.get_rect(center=self.single_rect.center)
            r.centery += 10
            screen.blit(txt, r)
        else:

            img1 = self.btn_hover if self.btn1_hover else self.btn_normal
            screen.blit(img1, self.btn1_rect.topleft)
            color1 = self.text_color_hover if self.btn1_hover else self.text_color_normal
            txt1 = self.font_option.render("Continue", True, color1)
            r1 = txt1.get_rect(center=self.btn1_rect.center)
            r1.centery += 10
            screen.blit(txt1, r1)

            img2 = self.btn_hover if self.btn2_hover else self.btn_normal
            screen.blit(img2, self.btn2_rect.topleft)
            color2 = self.text_color_hover if self.btn2_hover else self.text_color_normal
            txt2 = self.font_option.render("Main Menu", True, color2)
            r2 = txt2.get_rect(center=self.btn2_rect.center)
            r2.centery += 10
            screen.blit(txt2, r2)