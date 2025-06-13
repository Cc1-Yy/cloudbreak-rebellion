import os
import pygame
from src.projectile import Projectile
from src.entities.enemy import load_gif_frames


class Player(pygame.sprite.Sprite):

    def __init__(self, x: int, y: int):
        super().__init__()

        gif_path = os.path.join("assets", "images", "player", "player.gif")
        self.frames = load_gif_frames(gif_path)
        self.frame_index = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.1

        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.image)

        self.vel_x = 0
        self.vel_y = 0
        self.facing = 1
        self.speed = 300
        self.jump_strength = -600
        self.gravity = 2000
        self.max_fall_speed = 1200
        self.on_ground = True

        self.health = 3
        self.max_health = self.health

        self.gem_count = 0

        self.bullets = pygame.sprite.Group()
        self.shoot_cooldown = 0.5
        self.shoot_timer = 0.0

        self.is_invincible = False
        self.invincible_timer = 0.0
        self.invincible_duration = 2.0
        self.flash_timer = 0.0
        self.flash_interval = 0.1
        self.visible = True

        self.knock_back_speed = 800
        self.knock_back_duration = 0.2
        self.knock_back_timer = 0.0
        self.knock_back_dir = 0
        self.knock_back_vertical = -400

        self.is_dead = False
        self.death_ascending = False
        self.death_speed = -300

        self.level_manager = None

    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP) and self.on_ground:
                self.vel_y = self.jump_strength
                self.on_ground = False

            elif event.key == pygame.K_SPACE and self.shoot_timer <= 0:
                self.shoot()
                self.shoot_timer = self.shoot_cooldown

    def shoot(self):
        px, py = self.rect.center
        arrow = Projectile(px, py + 10, self.facing)
        self.bullets.add(arrow)

    def take_damage(self, amount: int, source_x: float):
        if self.is_invincible:
            return

        self.health = max(self.health - amount, 0)
        if self.health > 0:
            self.on_ground = False
            self.vel_y = self.knock_back_vertical
            self.knock_back_dir = 1 if source_x < self.rect.centerx else -1
            self.knock_back_timer = self.knock_back_duration
            self.is_invincible = True
            self.invincible_timer = self.invincible_duration
            self.flash_timer = 0.0
            self.visible = False
        else:
            self.is_dead = True
            self.death_ascending = True
            self.vel_y = self.death_speed

    def start_invincibility(self):
        self.is_invincible = True
        self.invincible_timer = self.invincible_duration
        self.flash_timer = 0.0
        self.visible = False

    def update(self, dt: float):
        if self.is_dead:
            if self.death_ascending:
                self.rect.y += int(self.vel_y * dt)
                self.vel_y += self.gravity * dt
                if self.vel_y >= 0:
                    self.death_ascending = False
            else:
                self.rect.y += int(self.vel_y * dt)
                self.vel_y += self.gravity * dt
            return
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
                self.vel_x = +self.speed
                self.facing = +1

        if self.level_manager:
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

        if not self.on_ground:
            self.vel_y += self.gravity * dt
        if self.vel_y > self.max_fall_speed:
            self.vel_y = self.max_fall_speed
        dy = int(self.vel_y * dt)

        if self.level_manager:
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

                elif step_dy < 0:
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

        if self.is_invincible:
            self.invincible_timer -= dt
            self.flash_timer += dt
            if self.flash_timer >= self.flash_interval:
                self.flash_timer -= self.flash_interval
                self.visible = not self.visible
            if self.invincible_timer <= 0:
                self.is_invincible = False
                self.visible = True

        if self.shoot_timer > 0:
            self.shoot_timer -= dt

        for arrow in list(self.bullets):
            arrow.update(dt)

        if self.vel_x != 0:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer -= self.anim_speed
                self.frame_index = (self.frame_index + 1) % len(self.frames)
        else:
            self.frame_index = 0

        frame = self.frames[self.frame_index]
        self.image = pygame.transform.flip(frame, True, False) if self.facing < 0 else frame
        self.mask = pygame.mask.from_surface(self.image)
