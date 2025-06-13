import os
import pygame


class Gem(pygame.sprite.Sprite):
    """
    A collectible gem. When the player touches it, the gem is removed
    and its value is applied to the player's gem_count.
    """

    def __init__(self, x: int, y: int, value: int = 1, image_path: str = None):
        super().__init__()

        if image_path:
            img = pygame.image.load(image_path).convert_alpha()
        else:
            default_path = os.path.join("assets", "images", "items", "gem.png")
            img = pygame.image.load(default_path).convert_alpha()

        self.image = img
        self.rect = self.image.get_rect(center=(x, y))

        self.value = value

    def apply(self, player):
        player.gem_count = getattr(player, "gem_count", 0) + self.value

        self.kill()
