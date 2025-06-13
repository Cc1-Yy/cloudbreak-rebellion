# Cloudbreak Rebellion

**Cloudbreak Rebellion** is a 2D side-scrolling RPG built with Pygame. You play as a courageous warrior on a quest through floating islands to reclaim the skies from tyranny. Push boxes, collect gems, shoot arrows, and defeat patrol enemies to clear each level and earn stars!


## Quick Start

1. **Clone the repository**  
   ```bash
   git clone https://github.com/Cc1-Yy/cloudbreak-rebellion.git
   cd cloudbreak-rebellion
    ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate    # macOS/Linux
   venv\Scripts\activate       # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the game**

   ```bash
   python main.py
   ```


## Controls

| Action       | Key(s) |
| ------------ | ------ |
| Move Left    | ← or A |
| Move Right   | → or D |
| Jump         | ↑ or W |
| Shoot Arrow  | Space  |
| Pause / Menu | Esc    |


## Project Structure

```
cloudbreak_rebellion/
├── assets/                # Game assets
│   ├── fonts/             # PixelFun font files
│   ├── images/            # Sprites, backgrounds, buttons
│   ├── levels/            # Tiled TMX map files
│   └── saves/             # Saved progress files (JSON)
├── docs/                  # Project documentation (this README)
├── src/                   # Source code
│   ├── config.py          # Global constants (e.g., TOTAL_LEVELS)
│   ├── engine.py          # Main game loop and state management
│   ├── persistence.py     # Save/load manager for progress
│   ├── projectile.py      # Arrow projectile logic
│   ├── level/             # LevelManager: loads TMX maps and collisions
│   │   └── level_manager.py
│   ├── entities/          # Game entities
│   │   ├── player.py
│   │   ├── enemy.py
│   │   ├── gem.py
│   │   └── box.py
│   └── state/             # Game states (menu, play, pause, etc.)
│       ├── base_state.py
│       ├── main_menu_state.py
│       ├── play_state.py
│       ├── pause_state.py
│       ├── level_select_state.py
│       ├── load_save_state.py
│       ├── game_over_state.py
│       └── game_clear_state.py
├── tests/                 # (Optional) Unit tests
├── main.py                # Entry point
├── README.md              # Project overview (this file)
└── requirements.txt       # Python dependencies
```


## Features

* **State-driven architecture** with push/pop transitions
* **Level selection** with star ratings and unlockable progression
* **Save & Load** progress slots with optional password protection
* **Physics**: gravity, jumping, collision detection, knockback
* **Entities**:

  * Player with animated GIF frames, health, invincibility frames
  * Patrol enemies that hurt on contact and die to arrows
  * Pushable boxes as dynamic platforms
  * Collectible gems with scoring
* **Modular design**: easy to add new levels, enemies, or items


