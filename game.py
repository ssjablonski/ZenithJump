import pygame
import random
import os
from spritesheet import SpriteSheet

# Inicjalizacja Pygame
pygame.init()

# Stałe
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SCROLL_THRESH = 200
GRAVITY = 1
MAX_PLATFORMS = 10
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PANEL = (101, 165, 221)
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zenith Jump")

# Ładowanie zasobów
bg_image = pygame.image.load('assets/bg.png').convert_alpha()
player_image = pygame.image.load('assets/jump.png').convert_alpha()
platform_image = pygame.image.load('assets/wood.png').convert_alpha()
enemy_image = pygame.image.load('assets/bird.png').convert_alpha()
enemy_sheet = SpriteSheet(enemy_image)

# Fonty
font_small = pygame.font.SysFont('Lucida Sans', 20)
font_big = pygame.font.SysFont('Lucida Sans', 24)

# Klasy
class Player:
    def __init__(self, x, y):
        self.image = pygame.transform.scale(player_image, (45, 45))
        self.width = 25
        self.height = 40
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.vel_y = 0
        self.flip = False

    def draw(self, screen):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - 12, self.rect.y - 5))

    def move(self, platform_group, action=None, is_training=False):
        scroll = 0
        dx = 0
        dy = 0

        if not is_training:
            key = pygame.key.get_pressed()
            if key[pygame.K_LEFT]:
                action = 0
            elif key[pygame.K_RIGHT]:
                action = 1
            else:
                action = 2

        if action == 0:  # Lewo
            dx = -10
            self.flip = True
        elif action == 1:  # Prawo
            dx = 10
            self.flip = False

        self.vel_y += GRAVITY
        dy += self.vel_y

        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rect.right

        for platform in platform_group:
            if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.rect.bottom < platform.rect.centery:
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        dy = 0
                        self.vel_y = -20

        if self.rect.top <= SCROLL_THRESH:
            if self.vel_y < 0:
                scroll = -dy

        self.rect.x += dx
        self.rect.y += dy + scroll
        self.mask = pygame.mask.from_surface(self.image)

        return scroll

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, moving):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(platform_image, (width, 10))
        self.moving = moving
        self.move_counter = random.randint(0, 50)
        self.direction = random.choice([-1, 1])
        self.speed = random.randint(1, 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, scroll):
        if self.moving:
            self.move_counter += 1
            self.rect.x += self.direction * self.speed
        if self.move_counter >= 100 or self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.direction *= -1
            self.move_counter = 0
        self.rect.y += scroll
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, SCREEN_WIDTH, y, sprite_sheet, scale):
        pygame.sprite.Sprite.__init__(self)
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.direction = random.choice([-1, 1])
        self.flip = self.direction == 1

        animation_steps = 8
        for animation in range(animation_steps):
            image = sprite_sheet.get_image(animation, 32, 32, scale, (0, 0, 0))
            image = pygame.transform.flip(image, self.flip, False)
            image.set_colorkey((0, 0, 0))
            self.animation_list.append(image)

        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = 0 if self.direction == 1 else SCREEN_WIDTH
        self.rect.y = y

    def update(self, scroll, SCREEN_WIDTH):
        ANIMATION_COOLDOWN = 50
        self.image = self.animation_list[self.frame_index]

        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list):
            self.frame_index = 0

        self.rect.x += self.direction * 2
        self.rect.y += scroll

        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

class Game:
    def __init__(self):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
        self.platform_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.platform_group.add(Platform(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 50, 100, False))
        self.scroll = 0
        self.bg_scroll = 0
        self.game_over = False
        self.score = 0
        self.high_score = self.load_high_score()

    def load_high_score(self):
        if os.path.exists('score.txt'):
            with open('score.txt', 'r') as file:
                return int(file.read())
        return 0

    def save_high_score(self):
        with open('score.txt', 'w') as file:
            file.write(str(self.high_score))

    def draw_bg(self):
        self.screen.blit(bg_image, (0, 0 + self.bg_scroll))
        self.screen.blit(bg_image, (0, -600 + self.bg_scroll))

    def draw_text(self, text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        self.screen.blit(img, (x, y))

    def draw_background_rect(self, x, y, width, height, color):
        pygame.draw.rect(self.screen, color, (x, y, width, height))


    def draw_panel(self):
        pygame.draw.rect(self.screen, PANEL, (0, 0, SCREEN_WIDTH, 30))
        pygame.draw.line(self.screen, BLACK, (0, 30), (SCREEN_WIDTH, 30), 2)
        self.draw_text('SCORE: ' + str(self.score), font_small, BLACK, 0, 0)

    def update(self, action=None):
        if not self.game_over:
            self.scroll = self.player.move(self.platform_group, action, is_training=False)
            self.bg_scroll += self.scroll
            if self.bg_scroll >= 600:
                self.bg_scroll = 0

            self.draw_bg()

            # Dodawanie nowych platform
            if len(self.platform_group) < MAX_PLATFORMS:
                last_platform_y = min(platform.rect.y for platform in self.platform_group)
                while len(self.platform_group) < MAX_PLATFORMS:
                    p_w = random.randint(40, 60)
                    p_x = random.randint(0, SCREEN_WIDTH - p_w)
                    p_y = last_platform_y - random.randint(80, 120)
                    p_type = random.randint(1, 2)
                    p_moving = p_type == 1 and self.score > 500
                    self.platform_group.add(Platform(p_x, p_y, p_w, p_moving))
                    last_platform_y = p_y

            self.platform_group.update(self.scroll)

            if len(self.enemy_group) == 0 and self.score > 1000:
                self.enemy_group.add(Enemy(SCREEN_WIDTH, 100, enemy_sheet, 1.5))

            self.enemy_group.update(self.scroll, SCREEN_WIDTH)

            if self.scroll > 0:
                self.score += self.scroll

            pygame.draw.line(self.screen, BLACK, (0, self.score - 10), (SCREEN_WIDTH, self.score - 10), 1)

            self.platform_group.draw(self.screen)
            self.enemy_group.draw(self.screen)
            self.player.draw(self.screen)

            if pygame.sprite.spritecollide(self.player, self.enemy_group, False, pygame.sprite.collide_mask):
                self.game_over = True

            if self.player.rect.top > SCREEN_HEIGHT:
                self.game_over = True

            self.draw_panel()
            
            if self.game_over:
                self.draw_background_rect(100, 180, 250, 200, WHITE)
                self.draw_text('GAME OVER', font_big, BLACK, 130, 200)
                self.draw_text('SCORE: ' + str(self.score), font_big, BLACK, 130, 250)
                self.draw_text('PRESS SPACE TO PLAY AGAIN', font_big, BLACK, 40, 300)
        return self.get_state(), self.get_reward(), self.game_over

    def reset(self):
        self.__init__()
        return self.get_state()

    def get_state(self):
        return [self.player.rect.x, self.player.rect.y, self.player.vel_y]

    def get_reward(self):
        if self.game_over:
            return -10
        else:
            return self.scroll

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if self.game_over:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.reset()
                        self.game_over = False

            self.update()
            pygame.display.update()

        pygame.quit()


# Inicjalizacja i uruchomienie gry
if __name__ == "__main__":
    game = Game()
    game.run()
