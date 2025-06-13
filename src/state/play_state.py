import os
import pygame
from src.state.base_state import GameState
from src.level.level_manager import LevelManager
from src.entities.player import Player
from src.entities.enemy import Enemy, load_gif_frames
from src.entities.gem import Gem
from src.entities.box import Box
from src.persistence import SaveManager
from src.config import TOTAL_LEVELS


class PlayState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.level_manager = LevelManager()
        self.player = None
        self.player_group = None
        self.enemies = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.boxes = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.current_level_index = 1
        self._level_finished = False

        self.heart_full = pygame.image.load(
            os.path.join("assets", "images", "level", "hud", "heart.png")
        ).convert_alpha()
        self.heart_empty = pygame.image.load(
            os.path.join("assets", "images", "level", "hud", "heart_gray.png")
        ).convert_alpha()
        self.gem_full = pygame.image.load(
            os.path.join("assets", "images", "level", "gem", "gem.png")
        ).convert_alpha()
        self.gem_empty = pygame.image.load(
            os.path.join("assets", "images", "level", "gem", "gem_gray.png")
        ).convert_alpha()

        stop0 = pygame.image.load("assets/images/level/buttons/stop.png").convert_alpha()
        stop1 = pygame.image.load("assets/images/level/buttons/stop_hover.png").convert_alpha()
        btn_w = int(self.game.screen.get_width() * 0.0176)
        btn_h = int(self.game.screen.get_height() * 0.029)
        self.stop_img = pygame.transform.smoothscale(stop0, (btn_w, btn_h))
        self.stop_img_hover = pygame.transform.smoothscale(stop1, (btn_w, btn_h))
        margin_x = 76
        margin_y = 10
        x = self.game.screen.get_width() - btn_w - margin_x
        y = margin_y
        self.pause_button_rect = pygame.Rect(x, y, btn_w, btn_h)
        self.pause_hover = False

    def enter(self):
        if not hasattr(self, "_loaded_from_save") or not self._loaded_from_save:
            SaveManager.reset_progress()
        self._loaded_from_save = False

        if self.level_manager.tmx_data is None and self.current_level_index is None:
            self.load_level(1)
        elif self.current_level_index is not None:
            self.load_level(self.current_level_index)
        self._init_level()

    def exit(self):
        self.enemies.empty()
        self.items.empty()
        self.all_sprites.empty()
        self.player_group = None

    def load_level(self, level_index):
        self.level_manager.load_level(level_index)
        self.current_level_index = level_index

    def load_from_save(self, save_meta: dict):
        prog = save_meta.get("progress", {})
        lvl = prog.get("unlocked", 1)
        try:
            lvl = int(lvl)
        except:
            lvl = 1
        num_levels = len(prog.get("ratings", [])) or TOTAL_LEVELS
        lvl = max(1, min(lvl, num_levels))
        self.load_level(lvl)
        self._loaded_from_save = True

    def _init_level(self):
        self.enemies.empty()
        self.items.empty()
        self.boxes.empty()
        self.all_sprites.empty()
        self._level_finished = False

        px, py = self.level_manager.get_player_spawn()
        self.player = Player(px, py)
        self.player.level_manager = self.level_manager
        self.player.start_invincibility()
        self.all_sprites.add(self.player)
        self.player_group = pygame.sprite.GroupSingle(self.player)
        self.player.prev_bottom = self.player.rect.bottom

        for ed in self.level_manager.get_enemy_data():
            frames = load_gif_frames(ed["gif_path"])
            enemy = Enemy(
                frames,
                ed["x"], ed["y"],
                ed["start"][0], ed["end"][0],
                ed["speed"]
            )
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

        for it in self.level_manager.get_item_data():
            kind = it["type"].lower()
            props = dict(it["properties"])
            if kind == "gem":
                value = int(props.get("value", 1))
                image_path = props.get("image_path", None)
                item = Gem(it["x"], it["y"], value=value, image_path=image_path)
                self.items.add(item)
                self.all_sprites.add(item)
            elif kind == "box":
                box = Box(it["x"], it["y"], **props)
                box.level_manager = self.level_manager
                self.boxes.add(box)
                self.all_sprites.add(box)

        self.total_gems = len(self.items)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.pause_button_rect.collidepoint(event.pos):
                self.game.push_state("pause")
                return

        if hasattr(self.player, "handle_event"):
            self.player.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.push_state("pause")

    def update(self, dt):
        mx, my = pygame.mouse.get_pos()
        self.pause_hover = self.pause_button_rect.collidepoint(mx, my)

        self.player.prev_bottom = self.player.rect.bottom
        self.player.update(dt)
        self.player.bullets.update(dt)

        impulse = 400
        for arrow in list(self.player.bullets):
            if not arrow.stuck:
                for box in self.boxes:
                    if arrow.rect.colliderect(box.rect):
                        arrow.stick(box.rect)
                        arrow.parent = box
                        arrow.offset_x = arrow.rect.x - box.rect.x
                        arrow.offset_y = arrow.rect.y - box.rect.y
                        box.vel_x += arrow.direction * impulse
                        break
            if arrow.stuck:
                continue
            for block in self.level_manager.get_obstacle_rects():
                if arrow.rect.colliderect(block):
                    arrow.stick(block)
                    break
            if arrow.stuck:
                continue
            for box in self.boxes:
                if arrow.rect.colliderect(box.rect):
                    arrow.stick_vertical(box.rect)
                    arrow.parent = box
                    arrow.offset_x = arrow.rect.x - box.rect.x
                    arrow.offset_y = arrow.rect.y - box.rect.y
                    break
            if arrow.stuck:
                continue
            for block in self.level_manager.get_ground_rects():
                if arrow.rect.colliderect(block):
                    arrow.stick_vertical(block)
                    break

        attack_bullets = pygame.sprite.Group(
            a for a in self.player.bullets
            if not getattr(a, "stuck_on_ground", False)
        )
        if not self.player.is_dead:
            self.enemies.update(dt, self.player_group, attack_bullets)

        self.items.update(dt)
        self.boxes.update(dt)

        self._check_collisions()

        if self.player.is_dead:
            screen_h = pygame.display.get_surface().get_height()
            if self.player.rect.top > screen_h:
                self.game.change_state("game_over")
                return

        if self._check_level_complete():
            stars = (self.player.health + self.player.gem_count) // 2
            prog = SaveManager.load_progress()
            idx = self.current_level_index - 1
            if stars > prog["ratings"][idx]:
                prog["ratings"][idx] = stars
            num_levels = len(prog["ratings"])
            if self.current_level_index < num_levels and prog["unlocked"] < self.current_level_index + 1:
                prog["unlocked"] = self.current_level_index + 1
            SaveManager.save_progress(prog)

            clear = self.game.states["game_clear"]
            clear.level_index = self.current_level_index
            clear.gem_count = self.player.gem_count
            clear.total_gems = self.total_gems
            clear.remaining_hearts = self.player.health
            clear.max_hearts = self.player.max_health

            self.game.change_state("game_clear")
            return

        self.player.prev_bottom = self.player.rect.bottom

    def draw(self, screen):
        class NoCam:
            def apply_pos(self, x, y): return (x, y)

        self.level_manager.draw_map(screen, NoCam())

        for spr in self.all_sprites:
            if spr is self.player and not self.player.visible:
                continue
            screen.blit(spr.image, spr.rect.topleft)

        for arrow in self.player.bullets:
            if getattr(arrow, "visible", True):
                screen.blit(arrow.image, arrow.rect.topleft)

        self._draw_hud(screen)

        img = self.stop_img_hover if self.pause_hover else self.stop_img
        screen.blit(img, self.pause_button_rect.topleft)

    def _check_collisions(self):
        p = self.player
        if getattr(p, "is_dead", False):
            return
        p.on_ground = False

        for rect in self.level_manager.get_obstacle_rects():
            if p.rect.colliderect(rect):
                if p.vel_x > 0:
                    p.rect.right = rect.left
                elif p.vel_x < 0:
                    p.rect.left = rect.right
                p.vel_x = 0

        if p.vel_y >= 0:
            prev = p.prev_bottom
            platforms = []
            platforms += [arrow.rect for arrow in p.bullets if getattr(arrow, "stuck_on_wall", False)]
            platforms += self.level_manager.get_ground_rects()
            platforms += self.level_manager.get_obstacle_rects()
            platforms += [box.rect for box in self.boxes]
            for plat in platforms:
                if p.rect.right > plat.left and p.rect.left < plat.right:
                    top = plat.top
                    if prev - 10 <= top <= p.rect.bottom:
                        p.rect.bottom = top
                        p.vel_y = 0
                        p.on_ground = True
                        break
        elif p.vel_y < 0:
            for rect in self.level_manager.get_obstacle_rects():
                if p.rect.colliderect(rect):
                    p.rect.top = rect.bottom
                    p.vel_y = 0

        hits = pygame.sprite.spritecollide(
            p, self.enemies, False, collided=pygame.sprite.collide_mask
        )
        for e in hits:
            p.take_damage(getattr(e, "contact_damage", 1), e.rect.centerx)

        collected = pygame.sprite.spritecollide(
            p, self.items, True, collided=pygame.sprite.collide_mask
        )
        for gem in collected:
            gem.apply(p)

        for box in self.boxes:
            if pygame.sprite.collide_mask(p, box) and p.vel_x != 0:
                box.vel_x = p.vel_x
                if p.vel_x > 0:
                    p.rect.right = box.rect.left
                else:
                    p.rect.left = box.rect.right

        exit_pt = self.level_manager.get_exit_point()
        if exit_pt and len(self.enemies) == 0:
            ex, ey = exit_pt
            er = pygame.Rect(ex, ey,
                             self.level_manager.tile_width,
                             self.level_manager.tile_height)
            if p.rect.colliderect(er):
                portal_mask = pygame.Mask(er.size, fill=True)
                offset = (er.x - p.rect.x, er.y - p.rect.y)
                if p.mask.overlap(portal_mask, offset):
                    self._level_finished = True

    def _check_level_complete(self):
        return getattr(self, "_level_finished", False) and len(self.enemies) == 0

    def _draw_hud(self, screen):
        start_x, start_y = 12, 12
        spacing = 6

        for i in range(self.player.max_health):
            img = self.heart_full if i < self.player.health else self.heart_empty
            x = start_x + i * (img.get_width() + spacing)
            screen.blit(img, (x, start_y))

        gem_y = start_y + self.heart_full.get_height() + spacing
        for j in range(self.total_gems):
            img = self.gem_full if j < self.player.gem_count else self.gem_empty
            x = start_x + j * (img.get_width() + spacing)
            screen.blit(img, (x, gem_y))
