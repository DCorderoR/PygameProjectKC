import pygame
import random

WIDTH = 800
HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)


pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Travel")
clock = pygame.time.Clock()


def drawText(surface, text, size, x, y):
    font = pygame.font.SysFont("./resources/font/astro.TTF", size)
    textSurface = font.render(text, True, WHITE)
    textRect = textSurface.get_rect()
    textRect.midtop = (x, y)
    surface.blit(textSurface, textRect)


def drawShieldBar(surface, x, y, percentage):
    bLenght = 100
    bHeight = 10
    fill = (percentage / 100) * bLenght
    border = pygame.Rect(x, y, bLenght, bHeight)
    fill = pygame.Rect(x, y, fill, bHeight)
    pygame.draw.rect(surface, GREEN, fill)
    pygame.draw.rect(surface, WHITE, border, 2)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("./resources/images/ship.png")
        self.rect = self.image.get_rect()
        self.rect.centerx = 100
        self.rect.bottom = 300
        self.speed_y = 0
        self.Vy = 0
        self.Vx = 0
        self.shield = 100

    def update(self):
        self.dir_y = 0
        keyState = pygame.key.get_pressed()
        if keyState[pygame.K_UP]:
            self.dir_y = -5

        if keyState[pygame.K_DOWN]:
            self.dir_y = 5
        self.rect.y += self.dir_y

        if self.rect.top <= 0:
            self.rect.top = 0
        if self.rect.bottom >= 600:
            self.rect.bottom = 600


class Meteor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = random.choice(meteorImages)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        # position X inicial del meteorito
        self.rect.x = WIDTH + random.randrange(0, 100)
        # posicion inicial Y del meteorito
        self.rect.y = random.randrange(0, HEIGHT)
        self.speedy = 0  # velocidad Y a 0, van rectas hacia la izquierda
        # velocidad negativa para ir hacia la izq
        self.speedx = random.randrange(-20, -1)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.x < 0 or self.rect.y > HEIGHT or self.rect.y < 0:
            # si esto pasa, reinicializamos el meteorito
            self.rect.x = WIDTH + random.randrange(0, 100)
            self.rect.y = random.randrange(0, HEIGHT)
            self.speedx = random.randrange(-20, -1)
            self.speedy = 0


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.image = explosionAnim[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 40  # Velocidad explosion

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosionAnim):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosionAnim[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


def showGoScreen():
    screen.blit(menuImage, [0, 0])
    drawText(screen, "Space Travel", 100, WIDTH // 2, HEIGHT // 4)
    drawText(screen, "keyUP  keyDOWN", 30, WIDTH // 2, HEIGHT // 2)
    drawText(screen, "Press any key", 50, WIDTH // 2, HEIGHT * 3/4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False


meteorImages = []
meteorList = ["./resources/images/meteorBrown_small1.png", "./resources/images/meteorBrown_big2.png",
              "./resources/images/meteorDebris.png", "./resources/images/jupiter.png", "./resources/images/meteor.png"]

for img in meteorList:
    meteorImages.append(pygame.image.load(img))

###Explosion###
explosionAnim = []
for i in range(9):
    file = "./resources/images/explosion/regularExplosion0{}.png".format(i)
    img = pygame.image.load(file).convert()
    img.set_colorkey(BLACK)
    img_scale = pygame.transform.scale(img, (70, 70))
    explosionAnim.append(img_scale)


# Cargar sonido
pygame.mixer.music.load("./resources/sounds/music.ogg")
pygame.mixer.music.set_volume(0.5)

# Cargar imagen de fondo
background = pygame.image.load("./resources/images/backGround.jpg")
menuImage = pygame.image.load("./resources/images/menu.png")

x = 0

all_sprites = pygame.sprite.Group()
meteor_list = pygame.sprite.Group()

player = Player()
all_sprites.add(player)
for i in range(5):
    meteor = Meteor()
    all_sprites.add(meteor)
    meteor_list.add(meteor)

score = 0
pygame.mixer.music.play(loops=-1)

###Game Over###
gameOver = True
running = True
while running:
    if gameOver:
        showGoScreen()

        gameOver = False
        all_sprites = pygame.sprite.Group()
        meteor_list = pygame.sprite.Group()

        player = Player()
        all_sprites.add(player)
        for i in range(5):
            meteor = Meteor()
            all_sprites.add(meteor)
            meteor_list.add(meteor)

        score = 0

    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()

    # Colisiones Player - Meteor
    hits = pygame.sprite.spritecollide(player, meteor_list, True)
    for hit in hits:
        player.shield -= 25
        explosion = Explosion(hit.rect.center)
        all_sprites.add(explosion)
        if player.shield <= 0:
            gameOver = True

    screen.blit(background, (x, 0))
    screen.blit(background, (x+1600, 0))
    all_sprites.draw(screen)

    # Marcador
    drawText(screen, str(score), 30, 20, 20)

    # BarraSalud
    drawShieldBar(screen, 5, 5, player.shield)

    pygame.display.flip()
    x -= 5
    if x <= -1600:
        x = 0


pygame.quit()
