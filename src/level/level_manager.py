import os
import pygame
import pytmx
from pytmx.util_pygame import load_pygame


class LevelManager:
    """
    Load and manage TMX levels exported from Tiled.
    Provides tile layers, collision rectangles, and object data:
    player spawn, exit point, enemies, items, and other objects.
    """

    def __init__(self):
        # TMX map data and dimensions
        self.tmx_data = None
        self.tile_width = self.tile_height = 0
        self.map_width = self.map_height = 0
        self.width = self.height = 0

        # Layer names by rendering order
        self.background_layers = []
        self.middle_layers = []
        self.foreground_layers = []

        # Collision rectangles
        self.ground_rects = []
        self.obstacle_rects = []

        # Object data
        self.spawn_point = (0, 0)
        self.exit_point = None
        self.enemy_data = []
        self.item_data = []
        self.other_objects = []

    def load_level(self, level_index: int):
        """
        Load the TMX file for the given level index.
        Parse layer names, collision tiles, and objects.
        """
        # Construct TMX file path
        tmx_path = os.path.normpath(
            os.path.join(
                os.path.dirname(__file__), os.pardir, os.pardir,
                "assets", "levels", f"level_{level_index:02d}.tmx"
            )
        )
        self.tmx_data = load_pygame(tmx_path)

        # Store map and tile dimensions
        self.tile_width = self.tmx_data.tilewidth
        self.tile_height = self.tmx_data.tileheight
        self.map_width = self.tmx_data.width
        self.map_height = self.tmx_data.height
        self.width = self.map_width * self.tile_width
        self.height = self.map_height * self.tile_height

        # Reset previous data
        self.background_layers.clear()
        self.middle_layers.clear()
        self.foreground_layers.clear()
        self.ground_rects.clear()
        self.obstacle_rects.clear()
        self.spawn_point = (0, 0)
        self.exit_point = None
        self.enemy_data.clear()
        self.item_data.clear()
        self.other_objects.clear()

        # Temporary storage for enemy spawn points and waypoints
        enemy_spawns = {}

        # Classify tile layers and collect collision rectangles
        for layer in self.tmx_data.layers:
            if isinstance(layer, pytmx.TiledImageLayer):
                # Image layers are background layers
                self.background_layers.append(layer.name)

            elif isinstance(layer, pytmx.TiledTileLayer):
                name_lower = layer.name.lower()
                # Assign to background, middle, or foreground
                if "bg" in name_lower or "background" in name_lower:
                    self.background_layers.append(layer.name)
                elif "fg" in name_lower or "foreground" in name_lower:
                    self.foreground_layers.append(layer.name)
                else:
                    self.middle_layers.append(layer.name)

                # Obstacle layer: every non-zero tile is a collision rect
                if layer.name == "Obstacle":
                    for x, y, gid in layer:
                        if gid:
                            rect = pygame.Rect(
                                x * self.tile_width,
                                y * self.tile_height,
                                self.tile_width,
                                self.tile_height
                            )
                            self.obstacle_rects.append(rect)

                # Ground layer: treat similarly for player-ground collisions
                elif layer.name == "Ground":
                    for x, y, gid in layer:
                        if gid:
                            rect = pygame.Rect(
                                x * self.tile_width,
                                y * self.tile_height,
                                self.tile_width,
                                self.tile_height
                            )
                            self.ground_rects.append(rect)

        # Parse object groups: enemies, player spawn, exit, items, others
        for layer in self.tmx_data.layers:
            if not isinstance(layer, pytmx.TiledObjectGroup):
                continue

            if layer.name == "Enemies":
                # Collect spawn points and waypoints, then assemble enemy_data
                for obj in layer:
                    otype = obj.type.lower()
                    if otype == "enemy_spawn":
                        name = obj.name
                        etype = obj.properties.get("enemy_type", 0)
                        gif_file = f"enemy_{etype}.gif"
                        gif_path = os.path.normpath(
                            os.path.join(
                                os.path.dirname(__file__), os.pardir, os.pardir,
                                "assets", "images", "enemies", gif_file
                            )
                        )
                        enemy_spawns[name] = {
                            "x": int(obj.x), "y": int(obj.y),
                            "enemy_type": etype,
                            "speed": obj.properties.get("speed", 0),
                            "start": None, "end": None,
                            "gif_path": gif_path
                        }
                    elif otype == "waypoint":
                        base, key = obj.name.rsplit("_", 1)
                        if base in enemy_spawns:
                            enemy_spawns[base][key] = (int(obj.x), int(obj.y))

                # Move assembled spawns into enemy_data list
                for data in enemy_spawns.values():
                    self.enemy_data.append(data)

            elif layer.name == "Player":
                # Player spawn object
                for obj in layer:
                    if obj.type.lower() == "player_spawn":
                        self.spawn_point = (int(obj.x), int(obj.y))

            elif layer.name == "Doors":
                # Exit portal object
                for obj in layer:
                    if obj.type.lower() == "portal":
                        self.exit_point = (int(obj.x), int(obj.y))

            elif layer.name == "Items":
                # Generic item objects
                for obj in layer:
                    if obj.type:
                        self.item_data.append({
                            "x": int(obj.x),
                            "y": int(obj.y),
                            "type": obj.type,
                            "properties": dict(obj.properties)
                        })

            else:
                # Any other object groups
                for obj in layer:
                    self.other_objects.append({
                        "x": int(obj.x),
                        "y": int(obj.y),
                        "type": obj.type,
                        "properties": dict(obj.properties)
                    })

    def draw_map(self, screen, camera):
        """
        Render map layers in order: background, middle, then foreground.
        camera.apply_pos(x, y) should transform world to screen coords.
        """

        def draw_tiled_layer(layer_name):
            layer = self.tmx_data.get_layer_by_name(layer_name)
            for x, y, gid in layer:
                tile = self.tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    wx, wy = x * self.tile_width, y * self.tile_height
                    sx, sy = camera.apply_pos(wx, wy)
                    screen.blit(tile, (sx, sy))

        # Draw background layers (image and tile)
        for name in self.background_layers:
            layer = self.tmx_data.get_layer_by_name(name)
            if isinstance(layer, pytmx.TiledImageLayer):
                img = layer.image
                ox, oy = getattr(layer, "offsetx", 0), getattr(layer, "offsety", 0)
                screen.blit(img, camera.apply_pos(ox or 0, oy or 0))
            else:
                draw_tiled_layer(name)

        # Draw middle tile layers
        for name in self.middle_layers:
            draw_tiled_layer(name)

        # Draw foreground tile layers
        for name in self.foreground_layers:
            draw_tiled_layer(name)

    # Public getters

    def get_collision_rects(self):
        """Return combined ground and obstacle rectangles."""
        return self.ground_rects + self.obstacle_rects

    def get_player_spawn(self):
        """Return the player spawn point (x, y)."""
        return self.spawn_point

    def get_exit_point(self):
        """Return the level exit/portal point (x, y)."""
        return self.exit_point

    def get_enemy_data(self):
        """Return list of enemy spawn and waypoint data."""
        return self.enemy_data

    def get_item_data(self):
        """Return list of item placement data."""
        return self.item_data

    def get_other_objects(self):
        """Return list of other generic objects."""
        return self.other_objects

    def get_ground_rects(self):
        """Return list of ground collision rectangles."""
        return self.ground_rects

    def get_obstacle_rects(self):
        """Return list of obstacle collision rectangles."""
        return self.obstacle_rects
