import pygame
from PIL import Image


def load_gif_frames(path):
    """
    Load all frames from a GIF file into a list of pygame.Surface.
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
    A patrol‐walking enemy with GIF animation, hurts the player on contact,
    and dies when hit by a projectile.
    """

    def __init__(self, frames, spawn_x, spawn_y, patrol_start, patrol_end, speed):
        """
        frames: list of pygame.Surface animation frames
        spawn_x, spawn_y: initial position (pixels)
        patrol_start, patrol_end: x‐coordinates (pixels) defining patrol range
        speed: movement speed in pixels per second
        """
        super().__init__()

        self.frames = frames
        self.frame_index = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.1
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(spawn_x, spawn_y))

        self.start_x = min(patrol_start, patrol_end)
        self.end_x = max(patrol_start, patrol_end)
        self.speed = speed

        self.direction = 1 if spawn_x <= self.end_x else -1

        self.alive = True

        self.contact_damage = 1

    def update(self, dt, player_group, arrow_group):
        """
        dt: time elapsed since last frame (seconds)
        player_group: pygame.sprite.GroupSingle or Group for collision
        arrow_group: pygame.sprite.Group of projectiles
        """
        if not self.alive:
            return

        self.rect.x += self.direction * self.speed * dt
        if self.rect.x <= self.start_x or self.rect.x >= self.end_x:
            self.direction *= -1

            self.frames = [pygame.transform.flip(f, True, False) for f in self.frames]

        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_timer -= self.anim_speed
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
        hits = pygame.sprite.spritecollide(self, player_group, False)
        for player in hits:
            damage = getattr(self, "contact_damage", 1)
            if hasattr(player, "take_damage"):
                player.take_damage(damage, self.rect.centerx)
            else:
                player.health -= damage

        if pygame.sprite.spritecollide(self, arrow_group, True):
            self.die()

    def die(self):
        """
        Handle death: remove from all groups. You can also add a death animation here.
        """
        self.alive = False
        self.kill()