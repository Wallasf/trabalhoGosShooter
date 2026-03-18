import random
import pygame
from .settings import *
from .assets import load_image, load_sound
from .entities import Player, Bullet, Zombie, FloatingText


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'menu'

        self.font_small = pygame.font.SysFont(FONT_NAME, 22)
        self.font_medium = pygame.font.SysFont(FONT_NAME, 32, bold=True)
        self.font_big = pygame.font.SysFont(FONT_NAME, 56, bold=True)

        self.load_assets()
        self.reset_game()

    def load_assets(self):
        self.bg = load_image('background_city.png', (WIDTH, HEIGHT), convert_alpha=False)
        self.menu_bg = load_image('menu_background.png', (WIDTH, HEIGHT), convert_alpha=False)
        self.player_img = load_image('player_police.png', (72, 118))
        self.zombie_img = load_image('zombie.png', (58, 58))
        self.bullet_img = load_image('bullet.png', (22, 10))
        self.logo = load_image('logo.png', (420, 130))
        self.button_img = load_image('button.png', (240, 70))
        self.crosshair = load_image('crosshair.png', (28, 28))

        self.snd_shot = load_sound('shot.wav', 0.35)
        self.snd_hit = load_sound('hit.wav', 0.4)
        self.snd_gameover = load_sound('gameover.wav', 0.45)
        self.snd_click = load_sound('click.wav', 0.35)

    def reset_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.zombies = pygame.sprite.Group()

        self.player = Player((WIDTH // 2, HEIGHT // 2), self.player_img)
        self.all_sprites.add(self.player)

        self.score = 0
        self.last_spawn = pygame.time.get_ticks()
        self.last_shot = 0
        self.floaters = []
        self.spawn_interval = SPAWN_INTERVAL
        self.game_over_played = False
        pygame.mouse.set_visible(False)

    def spawn_zombie(self):
        zombie = Zombie(self.player, self.zombie_img)
        self.zombies.add(zombie)
        self.all_sprites.add(zombie)

    def fire_bullet(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot < BULLET_COOLDOWN:
            return

        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        direction = mouse_pos - pygame.Vector2(self.player.rect.center)
        if direction.length_squared() == 0:
            return

        bullet = Bullet(self.player.rect.center, direction, self.bullet_img)
        self.bullets.add(bullet)
        self.all_sprites.add(bullet)
        self.last_shot = now
        self.snd_shot.play()

    def update(self, dt):
        if self.state != 'playing':
            return

        now = pygame.time.get_ticks()
        if now - self.last_spawn >= self.spawn_interval:
            self.spawn_zombie()
            self.last_spawn = now
            self.spawn_interval = max(400, self.spawn_interval - 5)

        self.all_sprites.update(dt)

        hits = pygame.sprite.groupcollide(self.zombies, self.bullets, True, True)
        for _zombie, _bullets in hits.items():
            self.score += 10
            self.floaters.append(FloatingText('+10', _zombie.rect.center, YELLOW))
            self.snd_hit.play()

        touching = pygame.sprite.spritecollide(self.player, self.zombies, False)
        for zombie in touching:
            if now - zombie.last_hit > 500:
                self.player.hp -= zombie.damage
                zombie.last_hit = now
                self.floaters.append(FloatingText(f'-{zombie.damage}', self.player.rect.midtop, RED))

        self.floaters = [f for f in self.floaters if f.alive()]

        if self.player.hp <= 0:
            self.player.hp = 0
            self.state = 'gameover'
            if not self.game_over_played:
                self.snd_gameover.play()
                self.game_over_played = True

    def draw_button(self, center, text):
        rect = self.button_img.get_rect(center=center)
        self.screen.blit(self.button_img, rect)
        label = self.font_medium.render(text, True, WHITE)
        self.screen.blit(label, label.get_rect(center=rect.center))
        return rect

    def draw_hud(self):
        hp_ratio = self.player.hp / MAX_HP
        pygame.draw.rect(self.screen, GRAY, (20, 20, 220, 24), border_radius=12)
        pygame.draw.rect(self.screen, GREEN, (20, 20, int(220 * hp_ratio), 24), border_radius=12)
        hp_text = self.font_small.render(f'Vida: {self.player.hp}/{MAX_HP}', True, WHITE)
        score_text = self.font_small.render(f'Pontuação: {self.score}', True, WHITE)
        help_text = self.font_small.render('WASD/Setas para mover | Mouse para mirar | Clique esquerdo para atirar', True, WHITE)
        self.screen.blit(hp_text, (26, 20))
        self.screen.blit(score_text, (20, 52))
        self.screen.blit(help_text, (20, HEIGHT - 34))

    def draw_playing(self):
        self.screen.blit(self.bg, (0, 0))
        self.all_sprites.draw(self.screen)
        self.draw_hud()
        for floater in self.floaters:
            floater.draw(self.screen, self.font_small)

        mouse_pos = pygame.mouse.get_pos()
        cross_rect = self.crosshair.get_rect(center=mouse_pos)
        self.screen.blit(self.crosshair, cross_rect)

    def draw_menu(self):
        self.screen.blit(self.menu_bg, (0, 0))
        self.screen.blit(self.logo, self.logo.get_rect(center=(WIDTH // 2, 120)))

        subtitle = self.font_medium.render('Policial vs Zumbis', True, YELLOW)
        text1 = self.font_small.render('WASD/Setas para mover | Mouse para mirar | Clique esquerdo para atirar', True, YELLOW)
        text2 = self.font_small.render('Pressione ENTER ou clique em JOGAR.', True, YELLOW)
        self.screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 215)))
        self.screen.blit(text1, text1.get_rect(center=(WIDTH // 2, 255)))
        self.screen.blit(text2, text2.get_rect(center=(WIDTH // 2, 282)))

        self.play_button = self.draw_button((WIDTH // 2, 370), 'JOGAR')
        self.quit_button = self.draw_button((WIDTH // 2, 455), 'SAIR')

    def draw_gameover(self):
        self.draw_playing()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        game_over = self.font_big.render('GAME OVER', True, WHITE)
        score = self.font_medium.render(f'Pontuação final: {self.score}', True, YELLOW)
        retry = self.font_small.render('Pressione R para reiniciar ou ESC para voltar ao menu', True, WHITE)

        self.screen.blit(game_over, game_over.get_rect(center=(WIDTH // 2, 180)))
        self.screen.blit(score, score.get_rect(center=(WIDTH // 2, 250)))
        self.screen.blit(retry, retry.get_rect(center=(WIDTH // 2, 310)))

        self.retry_button = self.draw_button((WIDTH // 2, 390), 'REINICIAR')
        self.menu_button = self.draw_button((WIDTH // 2, 470), 'MENU')

    def draw(self):
        if self.state == 'menu':
            self.draw_menu()
        elif self.state == 'playing':
            self.draw_playing()
        elif self.state == 'gameover':
            self.draw_gameover()
        pygame.display.flip()

    def start_game(self):
        self.reset_game()
        self.state = 'playing'

    def handle_menu_click(self, pos):
        if self.play_button.collidepoint(pos):
            self.snd_click.play()
            self.start_game()
        elif self.quit_button.collidepoint(pos):
            self.running = False

    def handle_gameover_click(self, pos):
        if self.retry_button.collidepoint(pos):
            self.snd_click.play()
            self.start_game()
        elif self.menu_button.collidepoint(pos):
            self.snd_click.play()
            self.state = 'menu'
            pygame.mouse.set_visible(True)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if self.state == 'menu':
                    if event.key == pygame.K_RETURN:
                        self.snd_click.play()
                        self.start_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                elif self.state == 'playing':
                    if event.key == pygame.K_ESCAPE:
                        self.state = 'menu'
                        pygame.mouse.set_visible(True)
                elif self.state == 'gameover':
                    if event.key == pygame.K_r:
                        self.snd_click.play()
                        self.start_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'menu'
                        pygame.mouse.set_visible(True)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == 'menu':
                    self.handle_menu_click(event.pos)
                elif self.state == 'playing':
                    self.fire_bullet()
                elif self.state == 'gameover':
                    self.handle_gameover_click(event.pos)

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update(dt)
            self.draw()

        pygame.quit()
