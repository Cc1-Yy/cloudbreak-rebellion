import os
import pygame


class Projectile(pygame.sprite.Sprite):
    """
    Represents an arrow projectile shot by the player.
    Moves horizontally and is removed when it leaves the screen.
    Supports 'sticking' into surfaces or other sprites (e.g., boxes),
    and will follow a parent sprite if attached.
    """

    def __init__(self, x: int, y: int, direction: int,
                 speed: int = 1500, damage: int = 1):
        """
        x, y: starting center position of the arrow
        direction: +1 for right, -1 for left
        speed: pixels per second
        damage: damage dealt to an enemy on hit
        """
        super().__init__()

        img_path = os.path.join("assets", "images", "projectile", "arrow.png")
        self.image = pygame.image.load(img_path).convert_alpha()
        if direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(center=(x, y))

        self.direction = direction
        self.speed = speed
        self.damage = damage

        self.vel_y = 0
        self.gravity = 1500

        self.stuck = False
        self.stuck_on_wall = False
        self.stuck_on_ground = False
        self.ground_timer = 0.0
        self.ground_life = 10.0
        self.flash_threshold = 2.0
        self.visible = True


        self.parent = None
        self.offset_x = 0
        self.offset_y = 0

    def update(self, dt: float):

        if self.parent is not None:
            self.rect.x = self.parent.rect.x + self.offset_x
            self.rect.y = self.parent.rect.y + self.offset_y
            return

        dt = dt * 0.4

        if not self.stuck:

            self.rect.x += int(self.direction * self.speed * dt)
            self.vel_y += self.gravity * dt
            self.rect.y += int(self.vel_y * dt)
        else:

            self.ground_timer += dt
            time_left = self.ground_life - self.ground_timer
            if time_left <= self.flash_threshold:

                self.visible = (int(self.ground_timer * 5) % 2 == 0)
            if self.ground_timer >= self.ground_life:
                self.kill()
            return

        surface = pygame.display.get_surface()
        if surface:
            sw = surface.get_width()
            if self.rect.right < 0 or self.rect.left > sw:
                self.kill()

    def stick(self, hit_rect: pygame.Rect):
        """
        Called when arrow hits a vertical surface (wall or sprite side).
        Positions arrow flush against surface and enters stuck state.
        """
        self.stuck = True
        self.stuck_on_wall = True
        self.vel_y = 0

        if self.direction > 0:
            self.rect.right = hit_rect.left + 10
        else:
            self.rect.left = hit_rect.right - 10

        self.ground_timer = 0.0
        self.visible = True

    def stick_vertical(self, ground_rect: pygame.Rect):
        """
        Called when arrow hits a horizontal surface (ground or sprite top).
        Positions arrow tip flush on top and enters stuck state.
        """
        self.stuck = True
        self.stuck_on_ground = True
        self.vel_y = 0
        self.rect.bottom = ground_rect.top
        self.ground_timer = 0.0
        self.visible = True
