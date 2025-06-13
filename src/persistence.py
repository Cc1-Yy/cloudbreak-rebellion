import os
import json

from src.config import TOTAL_LEVELS


class SaveManager:

    SAVE_DIR = os.path.join("assets", "saves")
    SAVE_FILE = os.path.join(SAVE_DIR, "progress.json")

    os.makedirs(SAVE_DIR, exist_ok=True)

    @staticmethod
    def get_slot_path(slot_index: int) -> str:
        return os.path.join(SaveManager.SAVE_DIR, f"save_slot_{slot_index + 1}.json")

    @staticmethod
    def load_progress(num_levels: int = TOTAL_LEVELS) -> dict:
        default = {
            "unlocked": 1,
            "ratings": [0] * num_levels
        }

        if not os.path.exists(SaveManager.SAVE_FILE):
            return default

        try:
            with open(SaveManager.SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return default

        unlocked = data.get("unlocked", 1)
        ratings = data.get("ratings", default["ratings"])

        try:
            unlocked = int(unlocked)
        except Exception:
            unlocked = 1
        unlocked = max(1, min(unlocked, num_levels))

        if not isinstance(ratings, list) or len(ratings) != num_levels:
            ratings = default["ratings"]
        else:
            clean = []
            for r in ratings:
                try:
                    ri = int(r)
                except Exception:
                    ri = 0
                clean.append(max(0, min(ri, 3)))
            ratings = clean

        return {
            "unlocked": unlocked,
            "ratings": ratings
        }

    @staticmethod
    def save_progress(progress: dict):
        os.makedirs(SaveManager.SAVE_DIR, exist_ok=True)

        try:
            with open(SaveManager.SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(progress, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving progress: {e}")

    @staticmethod
    def reset_progress(num_levels: int = TOTAL_LEVELS):
        default = {
            "unlocked": 1,
            "ratings": [0] * num_levels
        }
        SaveManager.save_progress(default)