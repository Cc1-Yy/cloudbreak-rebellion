

import pygame
from src.state.base_state import GameState


class MainMenuState(GameState):
    def __init__(self, game):
        super().__init__(game)

        self.screen_width, self.screen_height = self.game.screen.get_size()

        bg_raw = pygame.image.load("assets/images/main_menu/background.png").convert_alpha()
        bg_size = (int(self.screen_width), int(self.screen_height))
        self.background = pygame.transform.smoothscale(bg_raw, bg_size)

        gloopie_raw = pygame.image.load("assets/images/main_menu/gloopie.png").convert_alpha()
        target_w = int(self.screen_width * 0.30)


        target_h = 0.28 * self.screen_height
        self.gloopie_image = pygame.transform.smoothscale(gloopie_raw, (target_w, target_h))
        self.gloopie_rect = self.gloopie_image.get_rect()
        self.gloopie_rect.centerx = self.screen_width // 2
        self.gloopie_rect.centery = int(self.screen_height * 0.18)

        title_raw = pygame.image.load("assets/images/main_menu/title.png").convert_alpha()
        title_w = int(self.screen_width * 0.63)
        title_h = int(self.screen_height * 0.25)
        self.title_image = pygame.transform.smoothscale(title_raw, (title_w, title_h))

        title_x = int(self.screen_width * 0.17)
        title_y = int(self.screen_height * 0.30)
        self.title_rect = pygame.Rect(title_x, title_y, title_w, title_h)

        self.btn_images = {
            "normal": "assets/images/main_menu/buttons/normal.png",
            "hover": "assets/images/main_menu/buttons/hover.png"
        }

        btn_width = int(self.screen_width * 0.28)
        btn_height = int(self.screen_height * 0.12)
        btn_x = (self.screen_width - btn_width) // 2
        btn_y_start = int(self.screen_height * 0.56)
        btn_y_load = btn_y_start + int(self.screen_height * 0.136)
        btn_y_setting = btn_y_load + int(self.screen_height * 0.136)

        normal_raw = pygame.image.load(self.btn_images["normal"]).convert_alpha()
        hover_raw = pygame.image.load(self.btn_images["hover"]).convert_alpha()
        self.start_img_normal = pygame.transform.smoothscale(normal_raw, (btn_width, btn_height))
        self.start_img_hover = pygame.transform.smoothscale(hover_raw, (btn_width, btn_height))
        self.load_img_normal = pygame.transform.smoothscale(normal_raw, (btn_width, btn_height))
        self.load_img_hover = pygame.transform.smoothscale(hover_raw, (btn_width, btn_height))
        self.setting_img_normal = pygame.transform.smoothscale(normal_raw, (btn_width, btn_height))
        self.setting_img_hover = pygame.transform.smoothscale(hover_raw, (btn_width, btn_height))

        self.start_button_rect = pygame.Rect(btn_x, btn_y_start, btn_width, btn_height)
        self.load_button_rect = pygame.Rect(btn_x, btn_y_load, btn_width, btn_height)
        self.instructions_button_rect = pygame.Rect(btn_x, btn_y_setting, btn_width, btn_height)

        self.start_hover = False
        self.load_hover = False
        self.setting_hover = False

        self.font = pygame.font.Font("assets/fonts/PixelFun-Regular.ttf", 45)
        self.text_color_normal = pygame.Color("#677a84")
        self.text_color_hover = pygame.Color("#566870")

    def enter(self):
        pass

    def exit(self):
        pass

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if self.start_button_rect.collidepoint((mx, my)):
                self.game.change_state("level_select")
                return
            elif self.load_button_rect.collidepoint((mx, my)):
                self.game.change_state("load_save")
                return
            elif self.instructions_button_rect.collidepoint((mx, my)):
                self.game.change_state("instructions")
                return

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, dt):
        mx, my = pygame.mouse.get_pos()
        self.start_hover = self.start_button_rect.collidepoint((mx, my))
        self.load_hover = self.load_button_rect.collidepoint((mx, my))
        self.setting_hover = self.instructions_button_rect.collidepoint((mx, my))

    def draw(self, screen):

        screen.blit(self.background, (0, 0))

        screen.blit(self.gloopie_image, self.gloopie_rect)

        screen.blit(self.title_image, self.title_rect)

        if self.start_hover:
            screen.blit(self.start_img_hover, self.start_button_rect.topleft)
            color = self.text_color_hover
        else:
            screen.blit(self.start_img_normal, self.start_button_rect.topleft)
            color = self.text_color_normal
        start_text = self.font.render("START", True, color)
        start_text_rect = start_text.get_rect()
        start_text_rect.centerx = self.start_button_rect.centerx
        start_text_rect.centery = self.start_button_rect.centery + 10
        screen.blit(start_text, start_text_rect)

        if self.load_hover:
            screen.blit(self.load_img_hover, self.load_button_rect.topleft)
            color = self.text_color_hover
        else:
            screen.blit(self.load_img_normal, self.load_button_rect.topleft)
            color = self.text_color_normal
        load_text = self.font.render("LOAD", True, color)
        load_text_rect = load_text.get_rect()
        load_text_rect.centerx = self.load_button_rect.centerx
        load_text_rect.centery = self.load_button_rect.centery + 10
        screen.blit(load_text, load_text_rect)

        if self.setting_hover:
            screen.blit(self.setting_img_hover, self.instructions_button_rect.topleft)
            color = self.text_color_hover
        else:
            screen.blit(self.setting_img_normal, self.instructions_button_rect.topleft)
            color = self.text_color_normal
        instructions_text = self.font.render("INSTRUCTIONS", True, color)
        instructions_text_rect = instructions_text.get_rect()
        instructions_text_rect.centerx = self.instructions_button_rect.centerx
        instructions_text_rect.centery = self.instructions_button_rect.centery + 15
        screen.blit(instructions_text, instructions_text_rect)