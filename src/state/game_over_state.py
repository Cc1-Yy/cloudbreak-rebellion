import os
import pygame
from src.state.base_state import GameState


class GameOverState(GameState):
    def __init__(self, game):
        """Initialize game over screen: load images, layout overlay and buttons."""
        super().__init__(game)
        self.screen_width, self.screen_height = game.screen.get_size()
        self.level_index = None  # Level to retry

        # Load and scale Gloopie image
        gloopie_path = os.path.join("assets", "images", "main_menu", "gloopie.png")
        graw = pygame.image.load(gloopie_path).convert_alpha()
        gw = int(self.screen_width * 0.30)
        gh = int(self.screen_height * 0.28)
        self.gloopie_image = pygame.transform.smoothscale(graw, (gw, gh))
        self.gloopie_rect = self.gloopie_image.get_rect(center=(
            self.screen_width // 2,
            int(self.screen_height * 0.20)
        ))

        # Overlay panel rectangle
        overlay_w = int(self.screen_width * 0.8)
        overlay_h = int(self.screen_height * 0.6)
        overlay_x = (self.screen_width - overlay_w) // 2
        overlay_y = (self.screen_height - overlay_h) // 2 + 20
        self.overlay_rect = pygame.Rect(overlay_x, overlay_y, overlay_w, overlay_h)

        # Load button images for normal and hover states
        normal_img = pygame.image.load(
            os.path.join("assets", "images", "level", "buttons", "normal.png")
        ).convert_alpha()
        hover_img = pygame.image.load(
            os.path.join("assets", "images", "level", "buttons", "hover.png")
        ).convert_alpha()

        # Compute button sizes and positions
        btn_w = int(self.screen_width * 0.28)
        btn_h = int(self.screen_height * 0.12)
        total_gap = overlay_w - 2 * btn_w
        margin = total_gap // 3
        x1 = overlay_x + margin
        x2 = overlay_x + margin * 2 + btn_w
        y_btn = overlay_y + int(overlay_h * 0.55)

        self.btn1_rect = pygame.Rect(x1, y_btn, btn_w, btn_h)
        self.btn2_rect = pygame.Rect(x2, y_btn, btn_w, btn_h)

        self.btn_normal = pygame.transform.smoothscale(normal_img, (btn_w, btn_h))
        self.btn_hover = pygame.transform.smoothscale(hover_img, (btn_w, btn_h))

        self.btn1_hover = False
        self.btn2_hover = False

        # Text colors for buttons
        self.text_color_normal = pygame.Color("#323232")
        self.text_color_hover = pygame.Color("#000000")

        # Fonts will be initialized in enter()
        self.font_title = None
        self.font_option = None

    def enter(self, level_index=None):
        """
        Set up the background and fonts when entering state.
        level_index: level number to retry.
        """
        self.level_index = level_index or 1

        # Select background based on level range (placeholder logic)
        bg_file = "background_3.png"
        bg_path = os.path.join("assets", "images", "level", bg_file)
        self.bg_image = pygame.image.load(bg_path).convert()

        # Initialize fonts
        pygame.font.init()
        font_path = os.path.join("assets", "fonts", "PixelFun-Regular.ttf")
        self.font_title = pygame.font.Font(font_path, 100)
        self.font_option = pygame.font.Font(font_path, 44)

    def handle_event(self, event):
        """Handle button clicks for retry and main menu."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Retry level
            if self.btn1_rect.collidepoint(mx, my):
                play_state = self.game.states["play"]
                play_state.current_level_index = self.level_index
                self.game.change_state("play")
                return
            # Return to main menu
            if self.btn2_rect.collidepoint(mx, my):
                self.game.change_state("main_menu")
                return

    def update(self, dt):
        """Update hover states for buttons."""
        mx, my = pygame.mouse.get_pos()
        self.btn1_hover = self.btn1_rect.collidepoint(mx, my)
        self.btn2_hover = self.btn2_rect.collidepoint(mx, my)

    def draw(self, screen):
        """Render background, overlay, Gloopie, title, and buttons."""
        # Draw background scaled to screen
        bg = pygame.transform.scale(self.bg_image, (self.screen_width, self.screen_height))
        screen.blit(bg, (0, 0))

        # Draw semi-transparent overlay panel
        overlay = pygame.Surface((self.overlay_rect.w, self.overlay_rect.h), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (255, 255, 255, 153), overlay.get_rect(), border_radius=25)
        screen.blit(overlay, self.overlay_rect.topleft)

        # Draw Gloopie image
        screen.blit(self.gloopie_image, self.gloopie_rect)

        # Draw "Game Over!" title
        title_surf = self.font_title.render("Game Over!", True, "#373737")
        title_rect = title_surf.get_rect(center=(
            self.screen_width // 2,
            self.overlay_rect.y + int(self.overlay_rect.h * 0.3)
        ))
        screen.blit(title_surf, title_rect)

        # Draw Retry button
        img1 = self.btn_hover if self.btn1_hover else self.btn_normal
        screen.blit(img1, self.btn1_rect.topleft)
        color1 = self.text_color_hover if self.btn1_hover else self.text_color_normal
        txt1 = self.font_option.render("Retry", True, color1)
        r1 = txt1.get_rect(center=self.btn1_rect.center)
        r1.centery += 10
        screen.blit(txt1, r1)

        # Draw Main Menu button
        img2 = self.btn_hover if self.btn2_hover else self.btn_normal
        screen.blit(img2, self.btn2_rect.topleft)
        color2 = self.text_color_hover if self.btn2_hover else self.text_color_normal
        txt2 = self.font_option.render("Main Menu", True, color2)
        r2 = txt2.get_rect(center=self.btn2_rect.center)
        r2.centery += 10
        screen.blit(txt2, r2)
