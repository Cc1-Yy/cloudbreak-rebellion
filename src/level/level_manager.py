import os
import pygame
import pytmx
from pytmx.util_pygame import load_pygame


class LevelManager:

    def __init__(self):
        self.tmx_data = None
        self.tile_width = self.tile_height = 0
        self.map_width = self.map_height = 0
        self.width = self.height = 0

        self.background_layers = []
        self.middle_layers = []
        self.foreground_layers = []

        self.ground_rects = []
        self.obstacle_rects = []

        self.spawn_point = (0, 0)
        self.exit_point = None
        self.enemy_data = []
        self.item_data = []
        self.other_objects = []

    def load_level(self, level_index: int):
        tmx_path = os.path.normpath(
            os.path.join(
                os.path.dirname(__file__), os.pardir, os.pardir,
                "assets", "levels", f"level_{level_index:02d}.tmx"
            )
        )
        self.tmx_data = load_pygame(tmx_path)

        self.tile_width = self.tmx_data.tilewidth
        self.tile_height = self.tmx_data.tileheight
        self.map_width = self.tmx_data.width
        self.map_height = self.tmx_data.height
        self.width = self.map_width * self.tile_width
        self.height = self.map_height * self.tile_height

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

        enemy_spawns = {}

        for layer in self.tmx_data.layers:

            if isinstance(layer, pytmx.TiledImageLayer):
                self.background_layers.append(layer.name)

            elif isinstance(layer, pytmx.TiledTileLayer):
                lname = layer.name.lower()
                if "bg" in lname or "background" in lname:
                    self.background_layers.append(layer.name)
                elif "fg" in lname or "foreground" in lname:
                    self.foreground_layers.append(layer.name)
                else:
                    self.middle_layers.append(layer.name)

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

        for layer in self.tmx_data.layers:
            if not isinstance(layer, pytmx.TiledObjectGroup):
                continue

            if layer.name == "Enemies":
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
                            "x": int(obj.x),
                            "y": int(obj.y),
                            "enemy_type": etype,
                            "speed": obj.properties.get("speed", 0),
                            "start": None,
                            "end": None,
                            "gif_path": gif_path
                        }

                    elif otype == "waypoint":

                        base, kind = obj.name.rsplit("_", 1)
                        if base in enemy_spawns:
                            enemy_spawns[base][kind] = (int(obj.x), int(obj.y))

                for data in enemy_spawns.values():
                    self.enemy_data.append(data)

            elif layer.name == "Player":
                for obj in layer:
                    if obj.type.lower() == "player_spawn":
                        self.spawn_point = (int(obj.x), int(obj.y))

            elif layer.name == "Doors":
                for obj in layer:
                    if obj.type.lower() == "portal":
                        self.exit_point = (int(obj.x), int(obj.y))

            elif layer.name == "Items":
                for obj in layer:
                    if obj.type:
                        self.item_data.append({
                            "x": int(obj.x),
                            "y": int(obj.y),
                            "type": obj.type,
                            "properties": dict(obj.properties)
                        })

            else:
                for obj in layer:
                    self.other_objects.append({
                        "x": int(obj.x),
                        "y": int(obj.y),
                        "type": obj.type,
                        "properties": dict(obj.properties)
                    })

    def draw_map(self, screen, camera):
        """ 按：背景 → 中间 → 前景 的顺序绘制所有瓦片与背景图 """

        def draw_tiled_layer(name):
            layer = self.tmx_data.get_layer_by_name(name)
            for x, y, gid in layer:
                tile = self.tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    wx, wy = x * self.tile_width, y * self.tile_height
                    sx, sy = camera.apply_pos(wx, wy)
                    screen.blit(tile, (sx, sy))

        for name in self.background_layers:
            layer = self.tmx_data.get_layer_by_name(name)
            if isinstance(layer, pytmx.TiledImageLayer):
                img = layer.image
                ox = getattr(layer, "offsetx", 0) or 0
                oy = getattr(layer, "offsety", 0) or 0
                screen.blit(img, camera.apply_pos(ox, oy))
            else:
                draw_tiled_layer(name)

        for name in self.middle_layers:
            draw_tiled_layer(name)

        for name in self.foreground_layers:
            draw_tiled_layer(name)


    def get_collision_rects(self):
        return self.ground_rects + self.obstacle_rects

    def get_player_spawn(self):
        return self.spawn_point

    def get_exit_point(self):
        return self.exit_point

    def get_enemy_data(self):
        return self.enemy_data

    def get_item_data(self):
        return self.item_data

    def get_other_objects(self):
        return self.other_objects

    def get_ground_rects(self):
        return self.ground_rects

    def get_obstacle_rects(self):
        return self.obstacle_rects
