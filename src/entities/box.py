import os
import pygame


class Box(pygame.sprite.Sprite):

    def __init__(self, x: int, y: int, **properties):

        super().__init__()

        img_path = os.path.join("assets", "images", "items", "box.png")
        self.image = pygame.image.load(img_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))

        self.properties = properties

        self.vel_x = 0.0
        self.vel_y = 0.0
        self.gravity = 1500.0
        self.friction = 3000.0
        self.max_fall_speed = 1200.0
        self.on_ground = False

        self.level_manager = None

    def update(self, dt: float):
        if not self.level_manager:
            return

        dx = int(self.vel_x * dt)
        tile_w = self.level_manager.tile_width
        steps = max(1, abs(dx) // tile_w + 1)
        step_dx = dx // steps

        for _ in range(steps):
            self.rect.x += step_dx
            for obs in self.level_manager.get_obstacle_rects():
                if self.rect.colliderect(obs):
                    if step_dx > 0:
                        self.rect.right = obs.left
                    elif step_dx < 0:
                        self.rect.left = obs.right
                    self.vel_x = 0
                    break

        if abs(self.vel_x) > 0:
            if self.vel_x > 0:
                self.vel_x = max(self.vel_x - self.friction * dt, 0)
            else:
                self.vel_x = min(self.vel_x + self.friction * dt, 0)

        if not self.on_ground:
            self.vel_y += self.gravity * dt
        if self.vel_y > self.max_fall_speed:
            self.vel_y = self.max_fall_speed
        dy = int(self.vel_y * dt)
        prev_bottom = self.rect.bottom
        tile_h = self.level_manager.tile_height
        steps = max(1, abs(dy) // tile_h + 1)
        step_dy = dy // steps
        self.on_ground = False

        for _ in range(steps):
            self.rect.y += step_dy

            if step_dy > 0:
                for ground in self.level_manager.get_ground_rects():
                    if (prev_bottom <= ground.top <= self.rect.bottom and
                            self.rect.right > ground.left and
                            self.rect.left < ground.right):
                        self.rect.bottom = ground.top
                        self.vel_y = 0
                        self.on_ground = True
                        break

            if self.on_ground:
                break

            prev_bottom = self.rect.bottom

    def apply(self, player):

        for key, value in self.properties.items():
            try:
                val = int(value) if isinstance(value, str) and value.isdigit() else float(value)
            except Exception:
                val = value

            if hasattr(player, key):
                curr = getattr(player, key)
                if isinstance(curr, (int, float)) and isinstance(val, (int, float)):
                    setattr(player, key, curr + val)
