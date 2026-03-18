import os
import sys

WIDTH = 960
HEIGHT = 540
FPS = 60
TITLE = "GosShooter"

WHITE = (245, 245, 245)
BLACK = (20, 20, 20)
RED = (200, 50, 50)
GREEN = (60, 200, 100)
YELLOW = (230, 220, 90)
BLUE = (70, 120, 240)
GRAY = (90, 90, 90)
DARK_GREEN = (24, 60, 30)

# define a pasta base correta
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)  # pasta do .exe
else:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # pasta do projeto

ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMAGE_DIR = os.path.join(ASSETS_DIR, "images")
SOUND_DIR = os.path.join(ASSETS_DIR, "sounds")

PLAYER_SPEED = 280
BULLET_SPEED = 620
ZOMBIE_SPEED_MIN = 70
ZOMBIE_SPEED_MAX = 145
SPAWN_INTERVAL = 900
MAX_HP = 100
BULLET_COOLDOWN = 180

FONT_NAME = "arial"