import math
import random
import pygame

from .settings import (
    WIDTH,
    HEIGHT,
    PLAYER_SPEED,
    BULLET_SPEED,
    ZOMBIE_SPEED_MIN,
    ZOMBIE_SPEED_MAX,
    MAX_HP,
)


# =========================================================
# CLASSE DO JOGADOR
# =========================================================
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, image):
        super().__init__()
        self.original_image = image
        self.image = image
        self.rect = self.image.get_rect(center=pos)

        self.pos = pygame.Vector2(self.rect.center)
        self.velocity = pygame.Vector2()
        self.facing = pygame.Vector2(1, 0)
        self.hp = MAX_HP

    def _handle_input(self):
        keys = pygame.key.get_pressed()
        self.velocity.xy = 0, 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.velocity.y = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.velocity.y = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity.x = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity.x = 1

    def _update_facing(self):
        if self.velocity.length_squared() > 0:
            self.velocity = self.velocity.normalize() * PLAYER_SPEED
            self.facing = self.velocity.normalize()

    def _move(self, dt):
        self.pos += self.velocity * dt
        self.rect.center = self.pos
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))
        self.pos = pygame.Vector2(self.rect.center)

    def _rotate_sprite(self):
        angle = -math.degrees(math.atan2(self.facing.y, self.facing.x))
        self.image = pygame.transform.rotozoom(self.original_image, angle, 1)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self, dt):
        self._handle_input()
        self._update_facing()
        self._move(dt)
        self._rotate_sprite()


# =========================================================
# CLASSE DO PROJÉTIL
# =========================================================
class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction, image):
        super().__init__()

        angle = -math.degrees(math.atan2(direction.y, direction.x))
        self.image = pygame.transform.rotozoom(image, angle, 1)
        self.rect = self.image.get_rect(center=pos)

        self.pos = pygame.Vector2(pos)
        self.velocity = direction.normalize() * BULLET_SPEED
        self.spawn_time = pygame.time.get_ticks()

    def _is_outside_screen(self):
        margin_rect = pygame.Rect(-30, -30, WIDTH + 60, HEIGHT + 60)
        return not margin_rect.colliderect(self.rect)

    def _is_expired(self):
        return pygame.time.get_ticks() - self.spawn_time > 1300

    def update(self, dt):
        self.pos += self.velocity * dt
        self.rect.center = self.pos

        if self._is_outside_screen() or self._is_expired():
            self.kill()


# =========================================================
# CLASSE DO ZUMBI
# =========================================================
class Zombie(pygame.sprite.Sprite):
    def __init__(self, target, image):
        super().__init__()
        self.original_image = image
        self.image = image
        self.target = target

        self.speed = random.randint(ZOMBIE_SPEED_MIN, ZOMBIE_SPEED_MAX)
        self.damage = random.randint(8, 15)
        self.last_hit = 0

        self.pos = self._get_spawn_position()
        self.rect = self.image.get_rect(center=self.pos)

    def _get_spawn_position(self):
        side = random.choice(["top", "bottom", "left", "right"])

        if side == "top":
            return pygame.Vector2(random.randint(0, WIDTH), -40)
        if side == "bottom":
            return pygame.Vector2(random.randint(0, WIDTH), HEIGHT + 40)
        if side == "left":
            return pygame.Vector2(-40, random.randint(0, HEIGHT))

        return pygame.Vector2(WIDTH + 40, random.randint(0, HEIGHT))

    def _get_direction_to_target(self):
        direction = pygame.Vector2(self.target.rect.center) - self.pos
        if direction.length_squared() > 0:
            direction = direction.normalize()
        return direction

    def _update_sprite_direction(self, direction):
        if direction.x < 0:
            self.image = pygame.transform.flip(self.original_image, True, False)
        else:
            self.image = self.original_image

    def update(self, dt):
        direction = self._get_direction_to_target()
        self.pos += direction * self.speed * dt

        self._update_sprite_direction(direction)
        self.rect = self.image.get_rect(center=self.pos)


# =========================================================
# TEXTO FLUTUANTE
# =========================================================
class FloatingText:
    def __init__(self, text, pos, color, lifetime=600):
        self.text = text
        self.pos = pygame.Vector2(pos)
        self.color = color
        self.lifetime = lifetime
        self.spawn_time = pygame.time.get_ticks()

    def alive(self):
        return pygame.time.get_ticks() - self.spawn_time < self.lifetime

    def draw(self, surface, font):
        elapsed = pygame.time.get_ticks() - self.spawn_time
        progress = elapsed / self.lifetime

        current_pos = self.pos + pygame.Vector2(0, -25 * progress)
        alpha = max(0, 255 - int(255 * progress))

        text_surface = font.render(self.text, True, self.color)
        text_surface.set_alpha(alpha)

        rect = text_surface.get_rect(center=current_pos)
        surface.blit(text_surface, rect)