import os
import pygame


class Box(pygame.sprite.Sprite):
    """
    A pushable box that the player can move horizontally, jump on, and
    that responds to simple physics (gravity, friction, collisions).
    Optionally holds properties to grant effects to the player.
    """

    def __init__(self, x: int, y: int, **properties):
        """
        Initialize the box sprite.

        Args:
            x, y: Top-left coordinates in world space (pixels).
            properties: Optional custom properties (e.g., heal, ammo).
        """
        super().__init__()

        # Load box image
        img_path = os.path.join("assets", "images", "items", "box.png")
        self.image = pygame.image.load(img_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))

        # Store any custom properties
        self.properties = properties

        # Physics attributes
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.gravity = 1500.0  # Gravity acceleration (px/s²)
        self.friction = 3000.0  # Horizontal deceleration (px/s²)
        self.max_fall_speed = 1200.0  # Terminal velocity (px/s)
        self.on_ground = False

        # Reference to level geometry for collision (set externally)
        self.level_manager = None

    def update(self, dt: float):
        """
        Update box position and physics.

        Args:
            dt: Time elapsed since last frame (seconds).
        """
        if not self.level_manager:
            return

        # Horizontal movement with friction and collision
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
                    else:
                        self.rect.left = obs.right
                    self.vel_x = 0
                    break

        # Apply friction to slow horizontal movement
        if self.vel_x > 0:
            self.vel_x = max(self.vel_x - self.friction * dt, 0)
        elif self.vel_x < 0:
            self.vel_x = min(self.vel_x + self.friction * dt, 0)

        # Vertical movement with gravity and terminal speed
        if not self.on_ground:
            self.vel_y += self.gravity * dt
        self.vel_y = min(self.vel_y, self.max_fall_speed)
        dy = int(self.vel_y * dt)

        # Vertical collision stepping
        prev_bottom = self.rect.bottom
        tile_h = self.level_manager.tile_height
        steps = max(1, abs(dy) // tile_h + 1)
        step_dy = dy // steps
        self.on_ground = False

        for _ in range(steps):
            self.rect.y += step_dy

            if step_dy > 0:
                # Landing detection on ground rectangles
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
        """
        Optionally apply box properties to the player. Does not remove the box.

        Args:
            player: The player object to receive property effects.
        """
        for key, value in self.properties.items():
            # Convert numeric strings to numbers
            try:
                val = int(value) if isinstance(value, str) and value.isdigit() else float(value)
            except Exception:
                val = value

            if hasattr(player, key):
                current = getattr(player, key)
                if isinstance(current, (int, float)) and isinstance(val, (int, float)):
                    setattr(player, key, current + val)
