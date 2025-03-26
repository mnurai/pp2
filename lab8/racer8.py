import pygame, sys
from pygame.locals import *
import random, time
pygame.init()

# Setting up FPS
FPS = 60
FramePerSec = pygame.time.Clock()

# Define colors
BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0
COINS_COLLECTED = 0

# Setting up Fonts
font = pygame.font.SysFont("Verdana", 60)
font_small = pygame.font.SysFont("Verdana", 20)
game_over = font.render("Game Over", True, BLACK)

# Load background image
background = pygame.image.load("AnimatedStreet.png")

# Create game screen
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
DISPLAYSURF.fill(WHITE)
pygame.display.set_caption("Game")

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__() 
        self.image = pygame.image.load("Enemy.png")
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)  

    def move(self):
        global SCORE
        self.rect.move_ip(0, SPEED)
        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1
            self.rect.top = 0
            self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Player.png")
        self.rect = self.image.get_rect()
        self.rect.center = (160, 520)
       
    def move(self):
        pressed_keys = pygame.key.get_pressed()
        if self.rect.left > 0 and pressed_keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH and pressed_keys[K_RIGHT]:        
            self.rect.move_ip(5, 0)

# Coin class ADDED
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("Coin.png")  # Load coin image
        self.image = pygame.transform.scale(self.image, (30, 30))  # Resize coin image
        self.rect = self.image.get_rect()
        self.respawn()
    
    def respawn(self):
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -random.randint(50, SCREEN_HEIGHT))
    
    def move(self):
        self.rect.move_ip(0, SPEED // 2)
        if self.rect.top > SCREEN_HEIGHT:
            self.respawn()

# Setting up Sprites        
P1 = Player()
E1 = Enemy()
C1 = Coin()

# Creating Sprite Groups
enemies = pygame.sprite.Group()
enemies.add(E1)
coins = pygame.sprite.Group()
coins.add(C1)
all_sprites = pygame.sprite.Group()
all_sprites.add(P1, E1, C1)

# Adding a new User event to increase speed
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# Game Loop
while True:
    for event in pygame.event.get():
        if event.type == INC_SPEED:
            SPEED += 0.5      
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    # Draw background
    DISPLAYSURF.blit(background, (0, 0))
    
    # Display scores
    scores = font_small.render(str(SCORE), True, BLACK)
    DISPLAYSURF.blit(scores, (10, 10))
    coins_score = font_small.render(f"Coins: {COINS_COLLECTED}", True, BLACK)
    DISPLAYSURF.blit(coins_score, (SCREEN_WIDTH - 100, 10))

    # Move and redraw all sprites
    for entity in all_sprites:
        DISPLAYSURF.blit(entity.image, entity.rect)
        entity.move() if hasattr(entity, 'move') else None

    # Check for collision with enemy
    if pygame.sprite.spritecollideany(P1, enemies):
        pygame.mixer.Sound('crash.wav').play()
        time.sleep(0.5)
        DISPLAYSURF.fill(RED)
        DISPLAYSURF.blit(game_over, (30, 250))
        pygame.display.update()
        time.sleep(2)
        pygame.quit()
        sys.exit()
    
    # Check for collision with coin
    if pygame.sprite.spritecollideany(P1, coins):
        COINS_COLLECTED += 1
        C1.respawn()
    
    pygame.display.update()
    FramePerSec.tick(FPS)
