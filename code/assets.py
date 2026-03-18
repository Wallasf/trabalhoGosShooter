import os
import pygame

from .settings import IMAGE_DIR, SOUND_DIR


# =========================================================
# CARREGAMENTO DE IMAGENS
# =========================================================
def load_image(filename, size=None, convert_alpha=True):
    """
    Carrega uma imagem da pasta assets/images.

    :param filename: nome do arquivo
    :param size: tupla (largura, altura) para redimensionar
    :param convert_alpha: usar transparência
    :return: pygame.Surface
    """
    path = os.path.join(IMAGE_DIR, filename)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Imagem não encontrada: {path}")

    image = pygame.image.load(path)

    if convert_alpha:
        image = image.convert_alpha()
    else:
        image = image.convert()

    if size:
        image = pygame.transform.smoothscale(image, size)

    return image


# =========================================================
# CARREGAMENTO DE SONS
# =========================================================
def load_sound(filename, volume=1.0):
    """
    Carrega um som da pasta assets/sounds.

    :param filename: nome do arquivo
    :param volume: volume inicial (0.0 a 1.0)
    :return: pygame.mixer.Sound
    """
    path = os.path.join(SOUND_DIR, filename)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Som não encontrado: {path}")

    sound = pygame.mixer.Sound(path)
    sound.set_volume(volume)

    return sound
