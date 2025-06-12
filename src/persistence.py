import os
import json

from src.config import TOTAL_LEVELS


class SaveManager:
    """
    Manages reading and writing level progress, including the highest unlocked level
    and star ratings for each level. Progress files are stored under assets/saves/.
    """

    # Directory and file for storing progress data
    SAVE_DIR = os.path.join("assets", "saves")
    SAVE_FILE = os.path.join(SAVE_DIR, "progress.json")

    # Ensure the save directory exists
    os.makedirs(SAVE_DIR, exist_ok=True)

    @staticmethod
    def get_slot_path(slot_index: int) -> str:
        """
        Return the file path for the given save slot (0-based index).
        Example: slot_index=0 -> assets/saves/save_slot_1.json
        """
        return os.path.join(SaveManager.SAVE_DIR, f"save_slot_{slot_index + 1}.json")

    @staticmethod
    def load_progress(num_levels: int = TOTAL_LEVELS) -> dict:
        """
        Load progress data from disk. If the file is missing or malformed,
        return default progress: unlocked=1, ratings list of zeros length num_levels.

        Args:
            num_levels: Total number of levels to validate ratings list length.

        Returns:
            A dict with keys:
              - "unlocked": int, the highest unlocked level.
              - "ratings": List[int], star ratings for each level.
        """
        default = {"unlocked": 1, "ratings": [0] * num_levels}

        if not os.path.exists(SaveManager.SAVE_FILE):
            return default

        try:
            with open(SaveManager.SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return default

        # Extract and validate unlocked level
        unlocked = data.get("unlocked", 1)
        try:
            unlocked = int(unlocked)
        except Exception:
            unlocked = 1
        unlocked = max(1, min(unlocked, num_levels))

        # Extract and validate ratings list
        ratings = data.get("ratings", default["ratings"])
        if not isinstance(ratings, list) or len(ratings) != num_levels:
            ratings = default["ratings"]
        else:
            clean_ratings = []
            for r in ratings:
                try:
                    ri = int(r)
                except Exception:
                    ri = 0
                # Clamp rating to range 0–3
                clean_ratings.append(max(0, min(ri, 3)))
            ratings = clean_ratings

        return {"unlocked": unlocked, "ratings": ratings}

    @staticmethod
    def save_progress(progress: dict):
        """
        Write the given progress dict to the progress file.
        Progress format must match load_progress return:
          {"unlocked": int, "ratings": [int, ...]}

        Args:
            progress: Dictionary containing "unlocked" and "ratings".
        """
        os.makedirs(SaveManager.SAVE_DIR, exist_ok=True)
        try:
            with open(SaveManager.SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(progress, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving progress: {e}")

    @staticmethod
    def reset_progress(num_levels: int = TOTAL_LEVELS):
        """
        Reset progress to default state: only level 1 unlocked, all star ratings zero,
        and save to disk.
        """
        default = {"unlocked": 1, "ratings": [0] * num_levels}
        SaveManager.save_progress(default)
