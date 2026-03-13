import os
import pygame
from .settings import IMAGE_DIR, SOUND_DIR


def load_image(filename, size=None, convert_alpha=True):
    path = os.path.join(IMAGE_DIR, filename)
    image = pygame.image.load(path)
    image = image.convert_alpha() if convert_alpha else image.convert()
    if size:
        image = pygame.transform.smoothscale(image, size)
    return image


def load_sound(filename, volume=1.0):
    path = os.path.join(SOUND_DIR, filename)
    sound = pygame.mixer.Sound(path)
    sound.set_volume(volume)
    return sound
