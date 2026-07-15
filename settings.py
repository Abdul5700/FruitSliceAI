"""Configuration shared by every Fruit Slice AI module."""
from pathlib import Path

TITLE = "Fruit Slice AI"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
HIGH_SCORES_FILE = DATA_DIR / "high_scores.json"
# Compact enough to remain fully visible on 125% Windows display scaling.
WINDOW_WIDTH, WINDOW_HEIGHT, TARGET_FPS, WEBCAM_INDEX = 1080, 580, 60, 0

BACKGROUND_TOP = (11, 18, 49)
BACKGROUND_BOTTOM = (83, 23, 87)
TEXT_COLOR, MUTED_TEXT, ACCENT_COLOR = (248, 250, 255), (190, 199, 230), (255, 91, 120)
GOOD_COLOR, DANGER_COLOR, GOLD = (81, 224, 159), (255, 78, 92), (255, 207, 73)

DIFFICULTIES = {
    "Easy": {"spawn_interval": 1.05, "speed_multiplier": .88, "bomb_chance": .10},
    "Medium": {"spawn_interval": .78, "speed_multiplier": 1.0, "bomb_chance": .16},
    "Hard": {"spawn_interval": .58, "speed_multiplier": 1.22, "bomb_chance": .23},
}
