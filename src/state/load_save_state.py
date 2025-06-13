

import os
import pygame
import json
import time
import hashlib
import base64
from src.state.base_state import GameState
from src.persistence import SaveManager


class LoadSaveState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.screen_width, self.screen_height = self.game.screen.get_size()

        bg_raw = pygame.image.load("assets/images/load_save/background.png").convert_alpha()
        self.background = pygame.transform.smoothscale(bg_raw, (self.screen_width, self.screen_height))
        title_raw = pygame.image.load("assets/images/load_save/title.png").convert_alpha()
        tw = int(self.screen_width * 0.47)
        th = int(self.screen_height * 0.097)
        self.title_image = pygame.transform.smoothscale(title_raw, (tw, th))
        tx = int(self.screen_width * 0.265)
        ty = int(self.screen_height * 0.081)
        self.title_rect = pygame.Rect(tx, ty, tw, th)

        info_raw = pygame.image.load("assets/images/load_save/load_info.png").convert_alpha()
        self.info_w = int(self.screen_width * 0.13)
        self.info_h = int(self.screen_height * 0.195)
        self.info_image = pygame.transform.smoothscale(info_raw, (self.info_w, self.info_h))

        self.save_slots = []
        base_x = int(self.screen_width * 0.17)
        base_y = int(self.screen_height * 0.25)
        col_off = int(self.screen_width * 0.18)
        row_off = int(self.screen_height * 0.29)
        for i in range(8):
            r, c = divmod(i, 4)
            x = base_x + c * col_off
            y = base_y + r * row_off
            rect = pygame.Rect(x, y, self.info_w, self.info_h)
            save_data = {
                "name": "",
                "user": "",
                "saved_at": "",
                "progress": ""
            }
            self.save_slots.append([rect, save_data])

        load0 = pygame.image.load("assets/images/load_save/button/1.png").convert_alpha()
        load1 = pygame.image.load("assets/images/load_save/button/2.png").convert_alpha()
        del0 = pygame.image.load("assets/images/load_save/button/3.png").convert_alpha()
        del1 = pygame.image.load("assets/images/load_save/button/4.png").convert_alpha()
        ld = pygame.image.load("assets/images/load_save/button/5.png").convert_alpha()
        dd = pygame.image.load("assets/images/load_save/button/6.png").convert_alpha()
        bw = int(self.screen_width * 0.06)
        bh = int(self.screen_height * 0.045)
        self.load_btn_img_normal = pygame.transform.smoothscale(load0, (bw, bh))
        self.load_btn_img_hover = pygame.transform.smoothscale(load1, (bw, bh))
        self.load_btn_img_disabled = pygame.transform.smoothscale(ld, (bw, bh))
        self.delete_btn_img_normal = pygame.transform.smoothscale(del0, (bw, bh))
        self.delete_btn_img_hover = pygame.transform.smoothscale(del1, (bw, bh))
        self.delete_btn_img_disabled = pygame.transform.smoothscale(dd, (bw, bh))

        spacing = int(self.screen_width * 0.01)
        self.slot_buttons = []
        for rect, _ in self.save_slots:
            total = bw * 2 + spacing
            lx = rect.centerx - total // 2
            ly = rect.bottom + int(self.screen_height * 0.02)
            lr = pygame.Rect(lx, ly, bw, bh)
            dr = pygame.Rect(lx + bw + spacing, ly, bw, bh)
            self.slot_buttons.append([lr, dr, False, False])

        a0 = pygame.image.load("assets/images/load_save/button/add_0.png").convert_alpha()
        a1 = pygame.image.load("assets/images/load_save/button/add_1.png").convert_alpha()
        sz = int(self.screen_height * 0.056)
        self.add_img_normal = pygame.transform.smoothscale(a0, (sz, sz))
        self.add_img_hover = pygame.transform.smoothscale(a1, (sz, sz))
        ax = int(self.screen_width * 0.486)
        ay = int(self.screen_height * 0.8)
        self.add_rect = pygame.Rect(ax, ay, sz, sz)
        self.add_hover = False

        cross0 = pygame.image.load("assets/images/load_save/button/cross.png").convert_alpha()
        cross1 = pygame.image.load("assets/images/load_save/button/cross_hover.png").convert_alpha()

        self.cross_size = int(self.screen_height * 0.05)
        self.cross_img_normal = pygame.transform.smoothscale(cross0, (self.cross_size, self.cross_size))
        self.cross_img_hover = pygame.transform.smoothscale(cross1, (self.cross_size, self.cross_size))

        b0 = pygame.image.load("assets/images/load_save/back/1.png").convert_alpha()
        b1 = pygame.image.load("assets/images/load_save/back/2.png").convert_alpha()
        bw2 = int(self.screen_width * 0.05)
        bh2 = int(self.screen_height * 0.056)
        self.back_img_normal = pygame.transform.smoothscale(b0, (bw2, bh2))
        self.back_img_hover = pygame.transform.smoothscale(b1, (bw2, bh2))
        bx = int(self.screen_width * 0.11)
        by = int(self.screen_height * 0.8)
        self.back_button_rect = pygame.Rect(bx, by, bw2, bh2)
        self.back_hover = False

        self.info_font = pygame.font.Font("assets/fonts/PixelFun-Regular.ttf", 20)

        self.label_color = pygame.Color("#594842")
        self.value_color = pygame.Color("#998984")

        self.show_dialog = False
        self.dialog_inputs = {"name": "", "user": "", "password": ""}
        self.cur_field = 0
        self.dialog_font = pygame.font.Font("assets/fonts/PixelFun-Regular.ttf", 24)
        self.save_hover = False

        self.dialog_type = None
        self.auth_inputs = {"user": "", "password": ""}
        self.auth_fields = ["user", "password", "confirm"]
        self.auth_field = 0
        self.auth_slot_idx = None
        self.auth_action = None
        self.confirm_hover = False

        self.show_load_result = False
        self.load_result_text = ""
        self.load_result_timer = 0.0

    def enter(self):

        for idx, (_, data) in enumerate(self.save_slots):
            path = SaveManager.get_slot_path(idx)
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                except Exception:
                    continue
                data["name"] = meta.get("name", "")
                data["user"] = meta.get("user", "")
                data["saved_at"] = meta.get("saved_at", "")
                prog = meta.get("progress", {})
                data["progress"] = f"Unlock:{prog.get('unlocked', '')}"
            else:
                data["name"] = ""
                data["user"] = ""
                data["saved_at"] = ""
                data["progress"] = ""

    def exit(self):
        pass

    def handle_event(self, event):

        if self.show_load_result:
            return

        if self.dialog_type == "auth":
            if event.type == pygame.KEYDOWN:
                fld = self.auth_fields[self.auth_field]
                if event.key in (pygame.K_TAB, pygame.K_DOWN):
                    self.auth_field = (self.auth_field + 1) % len(self.auth_fields)
                elif event.key == pygame.K_UP:
                    self.auth_field = (self.auth_field - 1) % len(self.auth_fields)
                elif fld != "confirm":
                    if event.key == pygame.K_BACKSPACE:
                        self.auth_inputs[fld] = self.auth_inputs[fld][:-1]
                    elif event.unicode and len(event.unicode) == 1:
                        self.auth_inputs[fld] += event.unicode
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                w = int(self.screen_width * 0.6)
                h = int(self.screen_height * 0.4)
                x = (self.screen_width - w) // 2
                y = (self.screen_height - h) // 2

                bw, bh = 150, 40
                bx = x + (w - bw) // 2
                by = y + h - bh - 60
                confirm_rect = pygame.Rect(bx, by, bw, bh)

                cross_rect = pygame.Rect(
                    x + w - self.cross_size - 10, y + 10,
                    self.cross_size, self.cross_size
                )

                if confirm_rect.collidepoint(mx, my):
                    self._try_auth()
                elif cross_rect.collidepoint(mx, my):
                    self.show_dialog = False
                    self.dialog_type = None
                return

        if self.show_dialog:
            if event.type == pygame.KEYDOWN:
                fields = ["name", "user", "password", "save_button"]
                fld = fields[self.cur_field]
                if event.key in (pygame.K_TAB, pygame.K_DOWN):
                    self.cur_field = (self.cur_field + 1) % len(fields)
                elif event.key == pygame.K_UP:
                    self.cur_field = (self.cur_field - 1) % len(fields)
                elif fld != "save_button":
                    if event.key == pygame.K_BACKSPACE:
                        self.dialog_inputs[fld] = self.dialog_inputs[fld][:-1]
                    elif event.unicode and len(event.unicode) == 1:
                        if fld == "name" and len(self.dialog_inputs["name"]) > 12:
                            return
                        if fld == "user" and len(self.dialog_inputs["user"]) > 6:
                            return
                        self.dialog_inputs[fld] += event.unicode
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                w = int(self.screen_width * 0.6)
                h = int(self.screen_height * 0.5)
                x = (self.screen_width - w) // 2
                y = (self.screen_height - h) // 2

                cross_rect = pygame.Rect(
                    x + w - self.cross_size - 10, y + 10,
                    self.cross_size, self.cross_size
                )

                bw, bh = 100, 40
                bx = x + (w - bw) // 2
                by = y + h - bh - 60
                save_rect = pygame.Rect(bx, by, bw, bh)

                if cross_rect.collidepoint(mx, my):
                    self.show_dialog = False
                    self.dialog_type = None
                elif save_rect.collidepoint(mx, my):
                    self._on_save()
                return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if self.add_rect.collidepoint(mx, my):
                self.show_dialog = True
                self.dialog_type = "add"
                self.cur_field = 0
                return

            if self.back_button_rect.collidepoint(mx, my) and not (self.show_dialog or self.dialog_type):
                self.game.change_state("main_menu")
                return

            for idx, (lr, dr, _, _) in enumerate(self.slot_buttons):
                has = bool(self.save_slots[idx][1]["saved_at"])
                if lr.collidepoint(mx, my) and has:

                    self.dialog_type = "auth"
                    self.auth_slot_idx = idx
                    self.auth_action = "load"
                    self.auth_inputs = {"user": "", "password": ""}
                    self.auth_field = 0
                    return
                if dr.collidepoint(mx, my) and has:
                    self.dialog_type = "auth"
                    self.auth_slot_idx = idx
                    self.auth_action = "delete"
                    self.auth_inputs = {"user": "", "password": ""}
                    self.auth_field = 0
                    return

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and not (self.show_dialog or self.dialog_type):
                self.game.change_state("main_menu")

    def update(self, dt):

        if self.show_load_result:
            self.load_result_timer -= dt
            if self.load_result_timer <= 0:
                self.show_load_result = False
            return

        mx, my = pygame.mouse.get_pos()

        if self.show_dialog and self.dialog_type == "add":

            w = int(self.screen_width * 0.6)
            h = int(self.screen_height * 0.5)
            x = (self.screen_width - w) // 2
            y = (self.screen_height - h) // 2
            bw, bh = 100, 40
            bx = x + (w - bw) // 2
            by = y + h - bh - 60
            save_rect = pygame.Rect(bx, by, bw, bh)

            self.save_hover = save_rect.collidepoint(mx, my)
            return

        if self.dialog_type == "auth":
            w = int(self.screen_width * 0.6)
            h = int(self.screen_height * 0.4)
            x = (self.screen_width - w) // 2
            y = (self.screen_height - h) // 2
            bw, bh = 150, 40
            bx = x + (w - bw) // 2
            by = y + h - bh - 60
            confirm_rect = pygame.Rect(bx, by, bw, bh)

            self.confirm_hover = confirm_rect.collidepoint(mx, my)
            return

        self.back_hover = self.back_button_rect.collidepoint(mx, my)
        self.add_hover = self.add_rect.collidepoint(mx, my)

        for i, (lr, dr, _, _) in enumerate(self.slot_buttons):
            has = bool(self.save_slots[i][1]["saved_at"])
            self.slot_buttons[i][2] = has and lr.collidepoint(mx, my)
            self.slot_buttons[i][3] = has and dr.collidepoint(mx, my)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))
        screen.blit(self.title_image, self.title_rect)

        for idx, (rect, data) in enumerate(self.save_slots):
            screen.blit(self.info_image, rect.topleft)
            line_h = self.info_font.get_height()
            line_sp = int(line_h)
            y0 = rect.top + int(self.screen_height * 0.003)
            cx = rect.centerx
            lines = [
                ("Name", data["name"] or "-"),
                ("User", data["user"] or "-"),
                ("Date", data["saved_at"].split(" ", 1)[0] if data["saved_at"] and " " in data["saved_at"] else "-"),
                ("Time", data["saved_at"].split(" ", 1)[1] if data["saved_at"] and " " in data["saved_at"] else "-"),
            ]
            pad = 5
            for i, (lbl, val) in enumerate(lines):
                y = y0 + int(2 * i * line_sp)
                s_lbl = self.info_font.render(lbl, True, self.label_color)
                s_val = self.info_font.render(val, True, self.value_color)
                x0 = cx - s_lbl.get_width() // 2
                x1 = cx - s_val.get_width() // 2
                screen.blit(s_lbl, (x0, y))
                screen.blit(s_val, (x1, y + line_sp))

        for idx, (lr, dr, lh, dh) in enumerate(self.slot_buttons):
            has = bool(self.save_slots[idx][1]["saved_at"])
            img_l = (self.load_btn_img_hover if lh else self.load_btn_img_normal) if has else self.load_btn_img_disabled
            img_d = (
                self.delete_btn_img_hover if dh else self.delete_btn_img_normal) if has else self.delete_btn_img_disabled
            screen.blit(img_l, lr.topleft)
            screen.blit(img_d, dr.topleft)

        screen.blit(self.add_img_hover if self.add_hover else self.add_img_normal,
                    self.add_rect.topleft)
        screen.blit(self.back_img_hover if self.back_hover else self.back_img_normal,
                    self.back_button_rect.topleft)

        if self.dialog_type == "auth":
            self._draw_auth_dialog(screen)
        elif self.show_dialog:
            self._draw_dialog(screen)

        if self.show_load_result:
            font = pygame.font.Font("assets/fonts/PixelFun-Regular.ttf", 36)
            surf = font.render(self.load_result_text, True, pygame.Color("white"))
            x = (self.screen_width - surf.get_width()) // 2
            y = (self.screen_height - surf.get_height()) // 2
            bg = pygame.Surface((surf.get_width() + 20, surf.get_height() + 20), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 180))
            screen.blit(bg, (x - 10, y - 10))
            screen.blit(surf, (x, y))

    def _draw_dialog(self, screen):
        """ Draw the Add-new-slot dialog """
        w = int(self.screen_width * 0.6)
        h = int(self.screen_height * 0.5)
        x = (self.screen_width - w) // 2
        y = (self.screen_height - h) // 2

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (255, 255, 255, 230), overlay.get_rect(), border_radius=10)
        screen.blit(overlay, (x, y))

        mx, my = pygame.mouse.get_pos()
        cross_rect = pygame.Rect(x + w - self.cross_size - 10, y + 10, self.cross_size, self.cross_size)
        img = self.cross_img_hover if cross_rect.collidepoint(mx, my) else self.cross_img_normal
        screen.blit(img, cross_rect.topleft)

        labels = ["Save Name:", "User:", "Password:"]
        for i, fld in enumerate(["name", "user", "password"]):
            lbl = self.dialog_font.render(labels[i], True, "#333333")
            sx = x + 100
            sy = y + 100 + i * 100
            screen.blit(lbl, (sx, sy))

            box = pygame.Rect(sx + 150, sy - 5, w - 350, 40)
            bg_col = "#FFFFFF" if self.cur_field == i else "#DDDDDD"
            pygame.draw.rect(screen, pygame.Color(bg_col), box, border_radius=5)
            pygame.draw.rect(screen, pygame.Color("#999999"), box, width=2, border_radius=5)

            txt = self.dialog_inputs[fld]
            disp = "*" * len(txt) if fld == "password" else txt
            txt_s = self.dialog_font.render(disp, True, "#000000")
            screen.blit(txt_s, (box.x + 5, box.y + 5))

        bw, bh = 100, 40
        bx = x + (w - bw) // 2
        by = y + h - bh - 60

        btn_color = (100, 220, 100) if self.save_hover else (0, 160, 0)
        btn_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, btn_color, btn_surf.get_rect(), border_radius=5)
        screen.blit(btn_surf, (bx, by))
        txt = self.dialog_font.render("Save", True, "#FFFFFF")
        screen.blit(txt, txt.get_rect(center=(bx + bw // 2, by + bh // 2)))

    def _draw_auth_dialog(self, screen):
        """ Draw the Load/Delete auth dialog """
        w = int(self.screen_width * 0.6)
        h = int(self.screen_height * 0.4)
        x = (self.screen_width - w) // 2
        y = (self.screen_height - h) // 2

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (255, 255, 255, 230), overlay.get_rect(), border_radius=10)
        screen.blit(overlay, (x, y))

        mx, my = pygame.mouse.get_pos()
        cross_rect = pygame.Rect(x + w - self.cross_size - 10, y + 10, self.cross_size, self.cross_size)
        img = self.cross_img_hover if cross_rect.collidepoint(mx, my) else self.cross_img_normal
        screen.blit(img, cross_rect.topleft)

        labels = ["User:", "Password:"]
        for i, fld in enumerate(["user", "password"]):
            lbl = self.dialog_font.render(labels[i], True, "#333333")
            sx = x + 100
            sy = y + 100 + i * 100
            screen.blit(lbl, (sx, sy))

            box = pygame.Rect(sx + 150, sy - 5, w - 350, 40)
            bg_col = "#FFFFFF" if self.auth_field == i else "#DDDDDD"
            pygame.draw.rect(screen, pygame.Color(bg_col), box, border_radius=5)
            pygame.draw.rect(screen, pygame.Color("#999999"), box, width=2, border_radius=5)

            val = self.auth_inputs[fld]
            disp = "*" * len(val) if fld == "password" else val
            txt_s = self.dialog_font.render(disp, True, "#000000")
            screen.blit(txt_s, (box.x + 5, box.y + 5))

        bw, bh = 150, 40
        bx = x + (w - bw) // 2
        by = y + h - bh - 60
        btn_color = (100, 220, 100) if self.confirm_hover else (0, 160, 0)
        pygame.draw.rect(screen, btn_color, (bx, by, bw, bh), border_radius=5)
        txt = self.dialog_font.render("Confirm", True, "#FFFFFF")
        screen.blit(txt, txt.get_rect(center=(bx + bw // 2, by + bh // 2)))

    def _on_save(self):
        idx = next((i for i, (_, d) in enumerate(self.save_slots) if not d["saved_at"]), None)
        if idx is None:
            self.show_dialog = False
            return

        prog = SaveManager.load_progress()
        pwd = self.dialog_inputs["password"]
        h = base64.b64encode(hashlib.sha256(pwd.encode()).digest()).decode()

        meta = {
            "name": self.dialog_inputs["name"],
            "user": self.dialog_inputs["user"],
            "password_hash": h,
            "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "progress": prog
        }

        slot_path = SaveManager.get_slot_path(idx)
        os.makedirs(os.path.dirname(slot_path), exist_ok=True)
        with open(slot_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        slot = self.save_slots[idx][1]
        slot["name"] = meta["name"]
        slot["user"] = meta["user"]
        slot["saved_at"] = meta["saved_at"]
        slot["progress"] = f"Unlock:{prog['unlocked']}"

        self.show_dialog = False
        self.dialog_type = None

        self.load_result_text = "Save Successful"
        self.show_load_result = True
        self.load_result_timer = 2.0

    def _try_auth(self):
        idx = self.auth_slot_idx
        slot_path = SaveManager.get_slot_path(idx)
        try:
            with open(slot_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:

            self.load_result_text = "Loading Failed"
            self.show_load_result = True
            self.load_result_timer = 2.0
            self.dialog_type = None
            return

        user_ok = (self.auth_inputs["user"] == meta.get("user"))
        pwd_hash = base64.b64encode(
            hashlib.sha256(self.auth_inputs["password"].encode()).digest()
        ).decode("utf-8")
        pass_ok = (pwd_hash == meta.get("password_hash"))

        if not (user_ok and pass_ok):

            self.load_result_text = "Authentication Failed"
            self.show_load_result = True
            self.load_result_timer = 2.0
            self.dialog_type = None
            return

        if self.auth_action == "load":
            SaveManager.save_progress(meta["progress"])
            self.load_result_text = "Loading Successful"
        if self.auth_action == "delete":
            os.remove(slot_path)
            slot = self.save_slots[idx][1]

            slot["name"] = ""
            slot["user"] = ""
            slot["saved_at"] = ""
            slot["progress"] = ""
            self.load_result_text = "Delete Successful"

        self.show_load_result = True
        self.load_result_timer = 2.0
        self.dialog_type = None