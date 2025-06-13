import pygame
from src.state.base_state import GameState


class PauseState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.screen_width, self.screen_height = game.screen.get_size()

        overlay_w = int(self.screen_width * 0.6)
        overlay_h = int(self.screen_height * 0.5)
        overlay_x = (self.screen_width - overlay_w) // 2
        overlay_y = (self.screen_height - overlay_h) // 2
        self.overlay_rect = pygame.Rect(overlay_x, overlay_y, overlay_w, overlay_h)


        normal_path = "assets/images/level/buttons/normal.png"
        hover_path = "assets/images/level/buttons/hover.png"
        normal_raw = pygame.image.load(normal_path).convert_alpha()
        hover_raw = pygame.image.load(hover_path).convert_alpha()

        btn_w = int(overlay_w * 0.4)
        btn_h = int(overlay_h * 0.225)
        total_gap = overlay_w - 2 * btn_w
        margin = total_gap // 3
        x1 = overlay_x + margin
        x2 = overlay_x + margin * 2 + btn_w
        y_btn = overlay_y + int(overlay_h * 0.6)

        self.btn1_rect = pygame.Rect(x1, y_btn, btn_w, btn_h)
        self.btn2_rect = pygame.Rect(x2, y_btn, btn_w, btn_h)

        self.btn_normal = pygame.transform.smoothscale(normal_raw, (btn_w, btn_h))
        self.btn_hover = pygame.transform.smoothscale(hover_raw, (btn_w, btn_h))

        self.btn1_hover = False
        self.btn2_hover = False

        self.font_title = None
        self.font_option = None

        self.text_color_normal = pygame.Color("#323232")
        self.text_color_hover = pygame.Color("#000000")

    def enter(self):
        pygame.font.init()
        fp = "assets/fonts/PixelFun-Regular.ttf"
        self.font_title = pygame.font.Font(fp, 80)
        self.font_option = pygame.font.Font(fp, 44)

    def exit(self):
        pass

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.btn1_rect.collidepoint(mx, my):
                self.game.pop_state()
                return
            if self.btn2_rect.collidepoint(mx, my):
                self.game.pop_state()
                self.game.change_state("main_menu")
                return
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                self.game.pop_state()

    def update(self, dt):
        mx, my = pygame.mouse.get_pos()
        self.btn1_hover = self.btn1_rect.collidepoint(mx, my)
        self.btn2_hover = self.btn2_rect.collidepoint(mx, my)

    def draw(self, screen):
        stack = self.game.state_stack
        if len(stack) >= 2:
            stack[-2].draw(screen)

        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        panel = pygame.Surface((self.overlay_rect.w, self.overlay_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (255, 255, 255, 180), panel.get_rect(), border_radius=20)
        screen.blit(panel, (self.overlay_rect.x, self.overlay_rect.y))

        title_surf = self.font_title.render("Paused", True, "#373737")
        title_rect = title_surf.get_rect(
            center=(self.screen_width // 2,
                    self.overlay_rect.y + int(self.overlay_rect.h * 0.25))
        )
        screen.blit(title_surf, title_rect)

        img1 = self.btn_hover if self.btn1_hover else self.btn_normal
        screen.blit(img1, self.btn1_rect.topleft)
        color1 = self.text_color_hover if self.btn1_hover else self.text_color_normal
        txt1 = self.font_option.render("Resume", True, color1)
        r1 = txt1.get_rect(center=self.btn1_rect.center)
        r1.centery += 12
        screen.blit(txt1, r1)

        img2 = self.btn_hover if self.btn2_hover else self.btn_normal
        screen.blit(img2, self.btn2_rect.topleft)
        color2 = self.text_color_hover if self.btn2_hover else self.text_color_normal
        txt2 = self.font_option.render("Main Menu", True, color2)
        r2 = txt2.get_rect(center=self.btn2_rect.center)
        r2.centery += 12
        r2.centerx += 5
        screen.blit(txt2, r2)