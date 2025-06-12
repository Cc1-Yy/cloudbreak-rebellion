import os
import pygame
from src.projectile import Projectile
from src.entities.enemy import load_gif_frames  # Reuse enemy GIF loader


class Player(pygame.sprite.Sprite):
    """
    Player character: handles movement, jumping, shooting arrows, taking damage,
    animations via GIF frames, and interaction with level geometry.
    """

    def __init__(self, x: int, y: int):
        """
        Initialize player sprite, load animation frames, set physics and state.
        x, y: initial spawn coordinates.
        """
        super().__init__()

        # Load animation frames from GIF
        gif_path = os.path.join("assets", "images", "player", "player.gif")
        self.frames = load_gif_frames(gif_path)
        self.frame_index = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.1  # Seconds per frame

        # Initial sprite image, rect, and mask
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

        # Physics properties
        self.vel_x = 0
        self.vel_y = 0
        self.facing = 1  # 1=right, -1=left
        self.speed = 300  # Horizontal speed (px/sec)
        self.jump_strength = -600  # Initial jump velocity (px/sec)
        self.gravity = 2000  # Gravity acceleration (px/sec²)
        self.max_fall_speed = 1200  # Terminal velocity (px/sec)
        self.on_ground = True

        # Health
        self.health = 3
        self.max_health = self.health

        # Gems collected
        self.gem_count = 0

        # Arrow shooting
        self.bullets = pygame.sprite.Group()
        self.shoot_cooldown = 0.5  # Seconds between shots
        self.shoot_timer = 0.0

        # Invincibility after hit
        self.is_invincible = False
        self.invincible_timer = 0.0
        self.invincible_duration = 2.0  # Seconds
        self.flash_timer = 0.0
        self.flash_interval = 0.1  # Seconds between visibility toggles
        self.visible = True

        # Knockback when damaged
        self.knock_back_speed = 800  # Horizontal knockback speed
        self.knock_back_duration = 0.2  # Seconds
        self.knock_back_timer = 0.0
        self.knock_back_dir = 0
        self.knock_back_vertical = -400

        # Death state
        self.is_dead = False
        self.death_ascending = False
        self.death_speed = -300  # Upward velocity when dying

        # Reference to LevelManager (set externally)
        self.level_manager = None

    def handle_event(self, event):
        """
        Process input events: jump on W/Up, shoot on SPACE if cooldown allows.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP) and self.on_ground:
                self.vel_y = self.jump_strength
                self.on_ground = False
            elif event.key == pygame.K_SPACE and self.shoot_timer <= 0:
                self.shoot()
                self.shoot_timer = self.shoot_cooldown

    def shoot(self):
        """Instantiate an arrow projectile in the current facing direction."""
        px, py = self.rect.center
        arrow = Projectile(px, py + 10, self.facing)
        self.bullets.add(arrow)

    def take_damage(self, amount: int, source_x: float):
        """
        Apply damage if not invincible, trigger knockback and invincibility frames.
        source_x: x-coordinate of damage source to determine knockback direction.
        """
        if self.is_invincible:
            return

        self.health = max(self.health - amount, 0)
        if self.health > 0:
            # Apply knockback
            self.on_ground = False
            self.vel_y = self.knock_back_vertical
            self.knock_back_dir = 1 if source_x < self.rect.centerx else -1
            self.knock_back_timer = self.knock_back_duration
            # Start invincibility
            self.is_invincible = True
            self.invincible_timer = self.invincible_duration
            self.flash_timer = 0.0
            self.visible = False
        else:
            # Enter death sequence
            self.is_dead = True
            self.death_ascending = True
            self.vel_y = self.death_speed

    def start_invincibility(self):
        """Enable invincibility at start of level or after respawn."""
        self.is_invincible = True
        self.invincible_timer = self.invincible_duration
        self.flash_timer = 0.0
        self.visible = False

    def update(self, dt: float):
        """
        Per-frame update:
         1) Handle death animation
         2) Apply knockback or player input
         3) Horizontal collision resolution
         4) Apply gravity & vertical collision
         5) Update invincibility flashing
         6) Update shoot cooldown
         7) Update projectiles
         8) Animate sprite frames
        dt: elapsed time in seconds.
        """
        # 1) Death animation
        if self.is_dead:
            # Ascend then fall
            if self.death_ascending:
                self.rect.y += int(self.vel_y * dt)
                self.vel_y += self.gravity * dt
                if self.vel_y >= 0:
                    self.death_ascending = False
            else:
                self.rect.y += int(self.vel_y * dt)
                self.vel_y += self.gravity * dt
            return

        # 2) Knockback vs input
        if self.knock_back_timer > 0:
            self.knock_back_timer -= dt
            self.vel_x = self.knock_back_dir * self.knock_back_speed
        else:
            keys = pygame.key.get_pressed()
            self.vel_x = 0
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.vel_x = -self.speed
                self.facing = -1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.vel_x = self.speed
                self.facing = 1

        # 3) Horizontal collision stepping
        if self.level_manager:
            dx = int(self.vel_x * dt)
            tile_w = self.level_manager.tile_width
            steps = max(1, abs(dx) // tile_w + 1)
            step_dx = dx // steps
            for _ in range(steps):
                self.rect.x += step_dx
                for obs in self.level_manager.get_obstacle_rects():
                    if self.rect.colliderect(obs):
                        # Adjust position to avoid overlap
                        if step_dx > 0:
                            self.rect.right = obs.left
                        else:
                            self.rect.left = obs.right
                        self.vel_x = 0
                        break

        # 4) Gravity and terminal velocity
        if not self.on_ground:
            self.vel_y += self.gravity * dt
        if self.vel_y > self.max_fall_speed:
            self.vel_y = self.max_fall_speed
        dy = int(self.vel_y * dt)

        # Vertical collision stepping
        if self.level_manager:
            prev_bottom = self.rect.bottom
            tile_h = self.level_manager.tile_height
            steps = max(1, abs(dy) // tile_h + 1)
            step_dy = dy // steps
            self.on_ground = False

            for _ in range(steps):
                self.rect.y += step_dy
                if step_dy > 0:
                    # Landing detection
                    for ground in self.level_manager.get_ground_rects():
                        if (prev_bottom <= ground.top <= self.rect.bottom and
                                self.rect.right > ground.left and
                                self.rect.left < ground.right):
                            self.rect.bottom = ground.top
                            self.vel_y = 0
                            self.on_ground = True
                            break
                else:
                    # Ceiling collision
                    for obs in self.level_manager.get_obstacle_rects():
                        if (self.rect.top <= obs.bottom <= prev_bottom and
                                self.rect.right > obs.left and
                                self.rect.left < obs.right):
                            self.rect.top = obs.bottom
                            self.vel_y = 0
                            break

                if self.on_ground:
                    break
                prev_bottom = self.rect.bottom

        # 5) Invincibility timer and flashing
        if self.is_invincible:
            self.invincible_timer -= dt
            self.flash_timer += dt
            if self.flash_timer >= self.flash_interval:
                self.flash_timer -= self.flash_interval
                self.visible = not self.visible
            if self.invincible_timer <= 0:
                self.is_invincible = False
                self.visible = True

        # 6) Shoot cooldown
        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        # 7) Update projectiles
        for arrow in list(self.bullets):
            arrow.update(dt)

        # 8) Animate sprite frames when moving
        if self.vel_x != 0:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer -= self.anim_speed
                self.frame_index = (self.frame_index + 1) % len(self.frames)
        else:
            self.frame_index = 0

        frame = self.frames[self.frame_index]
        # Flip image when facing left
        self.image = pygame.transform.flip(frame, True, False) if self.facing < 0 else frame
        self.mask = pygame.mask.from_surface(self.image)
