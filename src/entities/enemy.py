import pygame
from PIL import Image


def load_gif_frames(path):
    """
    Load frames from a GIF file and return as a list of pygame.Surface objects.
    """
    pil_img = Image.open(path)
    frames = []
    try:
        while True:
            frame = pil_img.copy().convert('RGBA')
            data = frame.tobytes()
            surf = pygame.image.fromstring(data, frame.size, frame.mode)
            frames.append(surf)
            pil_img.seek(pil_img.tell() + 1)
    except EOFError:
        pass
    return frames


class Enemy(pygame.sprite.Sprite):
    """
    A patrol‐walking enemy that animates via GIF frames, damages the player
    on contact, and is destroyed by projectiles.
    """

    def __init__(self, frames, spawn_x, spawn_y, patrol_start, patrol_end, speed):
        """
        Args:
            frames: List[pygame.Surface], animation frames.
            spawn_x, spawn_y: Initial position in pixels.
            patrol_start, patrol_end: X-coordinate bounds for patrol movement.
            speed: Movement speed in pixels per second.
        """
        super().__init__()

        # Animation setup
        self.frames = frames
        self.frame_index = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.1  # Seconds per frame

        # Sprite image and rectangle
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(spawn_x, spawn_y))

        # Patrol configuration
        self.start_x = min(patrol_start, patrol_end)
        self.end_x = max(patrol_start, patrol_end)
        self.speed = speed
        # Initial direction: move toward the closer boundary
        self.direction = 1 if spawn_x <= self.end_x else -1

        # Health and state
        self.alive = True
        self.contact_damage = 1

    def update(self, dt, player_group, arrow_group):
        """
        Update movement, animation, and handle collisions.

        dt: Delta time in seconds since last update.
        player_group: Group of player sprites for collision detection.
        arrow_group: Group of projectile sprites.
        """
        if not self.alive:
            return

        # 1) Patrol movement and direction reversal
        self.rect.x += self.direction * self.speed * dt
        if self.rect.x <= self.start_x or self.rect.x >= self.end_x:
            self.direction *= -1
            # Flip all frames horizontally when direction changes
            self.frames = [pygame.transform.flip(f, True, False) for f in self.frames]

        # 2) Animate by advancing frame index
        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_timer -= self.anim_speed
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

        # 3) Player collision: inflict damage and knockback
        hits = pygame.sprite.spritecollide(self, player_group, False)
        for player in hits:
            damage = self.contact_damage
            if hasattr(player, "take_damage"):
                player.take_damage(damage, self.rect.centerx)
            else:
                # Fallback: directly reduce health attribute
                player.health -= damage

        # 4) Projectile collision: die when hit by an arrow
        if pygame.sprite.spritecollide(self, arrow_group, True):
            self.die()

    def die(self):
        """
        Handle death: mark not alive and remove sprite.
        """
        self.alive = False
        self.kill()
