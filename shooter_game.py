from pygame import *
from random import randint

win_width, win_height = 700, 500
window = display.set_mode((win_width, win_height))
display.set_caption("Shooter 2D")

clock = time.Clock()

fps = 60  # ? 1 секунда = 60 тиков
game_run = True
game_finished = False

# ! Створення звуків
mixer.init()
mixer.music.load("space.ogg")
mixer.music.play()
mixer.music.set_volume(0.025)

fire_sound = mixer.Sound("fire.ogg")
fire_sound.set_volume(0.025)

# ! Створення шрифтів
font.init()
stats_font = font.SysFont("Arial", 32)
main_font = font.SysFont("Arial", 72)
hp_font = font.SysFont("Arial", 18)

# ! Створюю текст поразки та перемоги
win_text = main_font.render("You win!", True, (50, 200, 0))
lose_text = main_font.render("You lose!", True, (200, 50, 0))


class GameSprite(sprite.Sprite):
    def __init__(self, img, x, y, w, h, speed):
        super().__init__()

        self.image = transform.smoothscale(
            image.load(img),
            (w, h)
        )

        self.speed = speed

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):
    fire_delay = fps * 0.1
    fire_timer = fire_delay
    can_fire = True
    health = 3

    def update(self):
        
        hp_txt = hp_font.render(f"HP: {self.health}", True, (0, 200, 25))

        if not self.can_fire:
            if self.fire_timer > 0:
                self.fire_timer -= 1
            else:
                self.fire_timer = self.fire_delay
                self.can_fire = True

        keys = key.get_pressed()
        
        if keys[K_w] or keys[K_UP]:
            self.rect.y -= self.speed
        
        if keys[K_s] or keys[K_DOWN]:
            self.rect.y += self.speed
            
        if keys[K_a] or keys[K_LEFT]:
            self.rect.x -= self.speed
            
        if keys[K_d] or keys[K_RIGHT]:
            self.rect.x += self.speed   
        
        if keys[K_SPACE]:
            if self.can_fire:
                self.fire()
                self.can_fire = False
                
        window.blit(hp_txt, (self.rect.x + self.image.get_width() / 2 - hp_txt.get_width() / 2, self.rect.y - 25))

    def fire(self):
        new_bullet = Bullet(levels[level_now]["bullet"], self.rect.centerx -
                            7.5, self.rect.y, 15, 25, 15)
        bullet_group.add(new_bullet)
        fire_sound.play()


class Enemy(GameSprite):
    health = randint(1, 3)
    
    def update(self):
        global lost
        
        hp_txt = hp_font.render(f"HP: {self.health + 1}", True, (200, 200, 200))

        if self.rect.y >= win_height: # ! Якщо торкнувся нижньої границі
            lost += 1
            self.kill()
        elif sprite.collide_rect(self, player): # ! Якщо торкнувся гравця
            player.health -= 1
            self.kill()
        else: # ! Якщо просто летить
            self.rect.y += self.speed
        
        window.blit(hp_txt, (self.rect.x + self.image.get_width() / 2 - hp_txt.get_width() / 2, self.rect.y - 25))
        
class Boss(GameSprite):
    def update(self):
        pass
        
class Asteroid(GameSprite):
    def update(self):
        if self.rect.y >= win_height: # ! Якщо торкнувся нижньої границі
            self.kill()
        elif sprite.collide_rect(self, player): # ! Якщо торкнувся гравця
            player.health -= 1
            self.kill()
        else: # ! Якщо просто летить
            self.rect.y += self.speed

class Bullet(GameSprite):
    def update(self):
        global kills

        if self.rect.y <= 0:
            self.kill()
            
        enemy = sprite.spritecollide(self, enemys_group, False) # ! Список ворогів, з якими зіткнулись
        
        if sprite.spritecollide(self, asteroid_group, False):
            self.kill()

        if enemy: # ! Якщо зіткнулись з ворогом
            enemy = enemy[0] # ! Отримуємо ворога, з яким зіткнулись
            if enemy.health <= 0: # ! Якщо у ворога нема ХП
                kills += 1 
                enemy.kill()
            else: # ! Якщо у ворога є ХП
                enemy.health -= 1
            self.kill() # ! В будь якому разі виділяємо кулю

        self.rect.y -= self.speed

# ! Для таймера спавна ворогів
enemy_respawn_delay = fps * 0.75  # ? між спавном ворогів чекаємо 2 секунди
enemy_respawn_timer = enemy_respawn_delay  # ? таймер

# ! Для таймера спавна астероїдів
asteroid_respawn_delay = fps * 2.25  # ? між спавном ворогів чекаємо 2 секунди
asteroid_respawn_timer = asteroid_respawn_delay  # ? таймер

# ! Змінні для лічильників
lost, kills = 0, 0

# ! Створення спрайтів
background = GameSprite("galaxy.jpg", 0, 0, win_width, win_height, 0)
player = Player("rocket.png", win_width / 2, win_height - 100, 50, 70, 5)
super_enemy = Enemy("ufo.png", 250, 250, 150, 150, 6)

# ! Рівні гри
levels = [
    {
        "background": "bg.jpg",
        "player": "bullet.png",
        "enemy": "asteroid.png",
        "bullets": "bullet.png"
    }, 
    {
        "background": "bg.jpg",
        "player": "ufo.png",
        "enemy": "ufo.png",
        "bullets": "bullet.png"
    }, 
    {   
        "background": "bg.jpg",
        "player": "asteroid.png",
        "enemy": "rocket.png",
        "bullets": "bullet.png"
    }
]
level_now = 0

# ! Створення груп спрайтів
enemys_group = sprite.Group()
bullet_group = sprite.Group()
asteroid_group = sprite.Group()

while game_run:

    for ev in event.get():
        if ev.type == QUIT:
            game_run = False

    if not game_finished:
        
        player.image = transform.smoothscale(
            image.load(levels[level_now]["player"]),
            (50, 70)
        )
        
        background.image = transform.smoothscale(
            image.load(levels[level_now]["background"]),
            (50, 70)
        )

        kills_text = stats_font.render(
            f"Рахунок: {kills}", True, (220, 220, 220))
        lost_text = stats_font.render(
            f"Пропущено: {lost}", True, (220, 220, 220))

        # ! Спавн ворогів
        if enemy_respawn_timer > 0:
            enemy_respawn_timer -= 1
        else:
            new_enemy = Enemy(levels[level_now]["enemy"], randint(
                0, win_width - 72), -72, 72, 64, randint(2, 5))
            new_enemy.health = randint(0, 2)
            enemys_group.add(new_enemy)
            enemy_respawn_timer = enemy_respawn_delay

        background.reset()

        player.reset()
        enemys_group.draw(window)
        bullet_group.draw(window)
        asteroid_group.draw(window)

        player.update()
        enemys_group.update()
        bullet_group.update()
        asteroid_group.update()

        window.blit(kills_text, (5, 5))
        window.blit(lost_text, (5, 38))

        # ! Умови кінця гри
        if kills > 1:
            level_now += 1
            kills = 0
            
        display.update()

    clock.tick(fps)
