import os
import pygame


class Gem(pygame.sprite.Sprite):
    """
    Collectible gem that increases the player's gem count upon collection.
    """

    def __init__(self, x: int, y: int, value: int = 1, image_path: str = None):
        """
        Initialize gem sprite.

        Args:
            x, y: Center position for the gem.
            value: Amount to increment player's gem_count.
            image_path: Optional custom image file path.
        """
        super().__init__()

        # Load specified image or fall back to default gem image
        if image_path:
            image = pygame.image.load(image_path).convert_alpha()
        else:
            default_path = os.path.join("assets", "images", "items", "gem.png")
            image = pygame.image.load(default_path).convert_alpha()

        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.value = value

    def apply(self, player):
        """
        Apply the gem's effect to the player and remove this sprite.

        Increments player's gem_count by this gem's value and then kills the sprite.
        """
        player.gem_count = getattr(player, "gem_count", 0) + self.value
        self.kill()
