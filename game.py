import pygame
import random
import os
from spritesheet import SpriteSheet
from enemy import Enemy

pygame.init()

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zenith Jump")

# ! TUTAJ ZALADUJ WSZYSTKIE OBRAZKI
bg_image = pygame.image.load('assets/bg.png').convert_alpha()
player_image = pygame.image.load('assets/jump.png').convert_alpha() 
platform_image = pygame.image.load('assets/wood.png').convert_alpha()
enemy_image = pygame.image.load('assets/bird.png').convert_alpha()
enemy_sheet = SpriteSheet(enemy_image)

clock = pygame.time.Clock()
FPS = 60

SCROLL_THRESH = 200
GRAVITY = 1
MAX_PLATFORMS = 10
scroll = 0
bg_scroll = 0
game_over = False
score = 0

if os.path.exists('score.txt'):
    with open('score.txt', 'r') as file:
        high_score = int(file.read())
else:
    high_score = 0


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PANEL = (101,165,221)

font_small = pygame.font.SysFont('Lucida Sans', 20)
font_big = pygame.font.SysFont('Lucida Sans', 24)



def draw_bg(bg_scroll):
    screen.blit(bg_image, (0, 0 + bg_scroll))
    screen.blit(bg_image, (0, -600 + bg_scroll))

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_panel():
    pygame.draw.rect(screen, PANEL, (0, 0, SCREEN_WIDTH, 30))
    pygame.draw.line(screen, BLACK, (0, 30), (SCREEN_WIDTH, 30), 2)
    draw_text('SCORE: ' + str(score), font_small, BLACK, 0, 0)


class Player():
    def __init__(self, x, y):
        self.image = pygame.transform.scale(player_image, (45, 45))
        self.width = 25
        self.height = 40
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = (x, y)
        self.vel_y = 0
        self.flip = False

    
    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - 12, self.rect.y - 5))
        # pygame.draw.rect(screen, RED, self.rect, 2)

    def move(self):

        scroll = 0
        dx = 0
        dy = 0

        key = pygame.key.get_pressed()

        if key[pygame.K_LEFT]:
            dx =- 10
            self.flip = True
        if key[pygame.K_RIGHT]:
            dx =+ 10
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

        if self.moving == True:
            self.move_counter += 1
            self.rect.x += self.direction * self.speed

        if self.move_counter >= 100 or self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.direction *= -1
            self.move_counter = 0 
            
        self.rect.y += scroll

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()




player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150 )

platform_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

platform = Platform(SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT-50, 100, False)
platform_group.add(platform)

run = True
while run:

    clock.tick(FPS)

    if game_over == False:
        scroll = player.move()

        bg_scroll += scroll
        if bg_scroll >= 600:
            bg_scroll = 0
        draw_bg(bg_scroll)

        # pygame.draw.line(screen, WHITE, (0, SCROLL_THRESH), (SCREEN_WIDTH, SCROLL_THRESH))

        if len(platform_group) < MAX_PLATFORMS:
            p_w = random.randint(40, 60)
            p_x = random.randint(0, SCREEN_WIDTH - p_w)
            p_y = platform.rect.y - random.randint(80, 120)
            p_type = random.randint(1, 2)
            if p_type == 1 and score > 500:
                p_moving = True
            else:
                p_moving = False
            platform = Platform(p_x, p_y, p_w, p_moving)
            platform_group.add(platform)

        platform_group.update(scroll)

        if len(enemy_group) == 0: # and score > 100:
            enemy = Enemy(SCREEN_WIDTH, 100, enemy_sheet, 1.5)
            enemy_group.add(enemy)

        enemy_group.update(scroll, SCREEN_WIDTH)

        if scroll > 0:
            score += scroll

        pygame.draw.line(screen, BLACK, (0, score - high_score + SCROLL_THRESH), (SCREEN_WIDTH, score - high_score + SCROLL_THRESH), 2)
        draw_text('HIGH SCORE: ' + str(high_score), font_small, BLACK, SCREEN_WIDTH - 130, score - high_score + SCROLL_THRESH - 25)
        platform_group.draw(screen)
        enemy_group.draw(screen)
        player.draw()

        draw_panel()

        if player.rect.top > SCREEN_HEIGHT:
            game_over = True
        if pygame.sprite.spritecollide(player, enemy_group, False):
            if pygame.sprite.spritecollide(player, enemy_group, False, pygame.sprite.collide_mask):
                game_over = True
    else:
        draw_text('GAME OVER!', font_big, BLACK, 130, 200)
        draw_text('SCORE: ' + str(score), font_big, BLACK, 130, 250)
        draw_text('PRESS SPACE TO PLAY AGAIN', font_big, BLACK, 40, 300)  
        if score > high_score:
            high_score = score
            with open('score.txt', 'w') as file:
                file.write(str(high_score))     
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE]:
            game_over = False
            score = 0
            scroll = 0
            player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
            enemy_group.empty()
            platform_group.empty()
            platform = Platform(SCREEN_WIDTH//2 - 50, SCREEN_HEIGHT-50, 100, False)
            platform_group.add(platform)
            

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        

    pygame.display.update()


pygame.quit()