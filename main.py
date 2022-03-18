#! /usr/bin/python3

import pygame
import random

pygame.init() 


class Bullets:
    def __init__(self, timer: int, width: int, height: int):
        self.bullets = []
        self.timer = timer
        self.time = self.timer
        self.width = width
        self.height = height
    
    def shoot(self, x: int, y: int):
        if self.timer >= self.time:
            self.bullets.append([x, y])
            self.timer = 0
        else:
            self.timer += 1

    def move(self, move_x, move_y):
        for i in range(len(self.bullets)):
            self.bullets[i][0] += move_x
            self.bullets[i][1] += move_y

    def draw(self, screen, color):
        for i in range(len(self.bullets)):
            pygame.draw.rect(screen, color, pygame.Rect((self.bullets[i][0], self.bullets[i][1]), (self.width, self.height)))

    def remove(self):
        for i in range(len(self.bullets)-1, -1, -1):
            if self.bullets[i][1] < -5:
                self.bullets.pop(i)

    def handle(self, screen, color, move_x, move_y):
        self.move(move_x, move_y)
        self.draw(screen, color)
        self.remove()


class Player:
    def __init__(self, image, x: int, y: int):
        self.player = pygame.image.load(image)
        self.rect = self.player.get_rect()
        self.rect.topleft = [x, y]
        self.player_move = [0, 0]
        self.shot = False
        self.points = 0

    def move(self):
        self.rect.topleft = [self.rect.topleft[0]+self.player_move[0], self.rect.topleft[1]+self.player_move[1]]

    def draw(self, screen: pygame.display.set_mode):
        screen.blit(self.player, self.rect.topleft)

    def shoot(self, bullets: Bullets):
        bullets.shoot(self.rect.topleft[0]+11, self.rect.topleft[1]-22)

    def hit(self, bullets: Bullets, dead_bullets: list[Bullets]):
        for bullet in bullets.bullets:
            if self.rect.collidepoint(bullet[0], bullet[1]):
                return True
        for bullet in dead_bullets:
            for b in bullet.bullets:
                if self.rect.collidepoint(b[0], b[1]):
                    return True
        return False

    def boundaries(self):
        if self.rect.topleft[0] > 1208:
            self.rect.topleft = [1207, self.rect.topleft[1]]
        if self.rect.topleft[0] < 0:
            self.rect.topleft = [1, self.rect.topleft[1]]
        if self.rect.topleft[1] > 850:
            self.rect.topleft = [self.rect.topleft[0], 849]
        if self.rect.topleft[1] < 0: 
            self.rect.topleft = [self.rect.topleft[0], 1]

    def handle(self, screen: pygame.display, player_bullets: Bullets, enemies: list, dead_bullets: list[Bullets]) -> int:
        self.move()
        for enemy_bullets in enemies:
            if self.hit(enemy_bullets[1], dead_bullets):
                print('you lose lol')
                return -1
        if self.shot:
            self.shoot(player_bullets)  

        self.boundaries()
        self.draw(screen)


class Enemy:
    def __init__(self, image, timer: int, x: int, y: int):
        self.enemy = pygame.image.load(image)
        self.enemy = pygame.transform.rotate(self.enemy, 180)
        self.rect = self.enemy.get_rect()
        self.rect.topleft = [x, y]
        self.timer = [timer, timer**3]
        self.time = [timer, timer**3]
        self.move_value = [0, 0]
        self.dead = False

    def hit(self, bullets: Bullets, player: Player) -> bool:
        for i in range(len(bullets.bullets)):
            if self.rect.collidepoint(bullets.bullets[i][0], bullets.bullets[i][1]):
                self.rect.topleft = [random.randint(100, 1180), random.randint(100, 480)]
                player.points += 1
                return True
        return False

    def draw(self, screen):
        screen.blit(self.enemy, self.rect.topleft)

    def shoot(self, bullets: Bullets):
        if self.timer[0] >= self.time[0]:
            bullets.shoot(self.rect.topleft[0]+14, self.rect.topleft[1]+22)
            self.timer[0] = 0

    def move(self):
        if self.timer[1] >= self.time[1]:
            self.move_value = [random.choice([-2, 0, 2]), random.choice([-2, 0, 2])]
            self.timer[1] = 0

        self.rect.topleft = [self.rect.topleft[0]+self.move_value[0], self.rect.topleft[1]+self.move_value[1]]
        self.timer[1] += 1

    def boundaries(self):
        if self.rect.topleft[0] < 0:
            self.move_value[0] = 2
        if self.rect.topleft[0] > 1240:
            self.move_value[0] = -2
        if self.rect.topleft[1] < 0:
            self.move_value[1] = 2
        if self.rect.topleft[1] > 480:
            self.move_value[1] = -2

    def handle(self, player_bullets: Bullets, screen, enemy_bullets: Bullets, player: Player):
        self.boundaries()
        self.move()
        self.draw(screen)
        if not self.hit(player_bullets, player):
            self.shoot(enemy_bullets)
        else:
            self.dead = True
        self.timer[0] += 1


def remove_enemies(enemies: list, dead_bullets: list) -> list:
    for i in range(len(enemies)-1, -1, -1):
        if enemies[i][0].dead:
            dead_bullets.append(enemies[i][1])
            enemies.pop(i)


def append_enemy(enemies: list, timer: int) -> int:
    if timer >= 100:
        enemies.append([Enemy('assets/enemy.png', 4, random.randint(0, 1240), random.randint(0, 480)) , Bullets(6, 5, 26)])
        return 0
    else:
        return timer + 1


def handle_dead_bullets(dead_bullets: list[Bullets], screen):
    for i in range(len(dead_bullets)-1, -1, -1):
        if len(dead_bullets[i].bullets) <= 0:
            dead_bullets.pop(i)
        else:
            dead_bullets[i].move(0, 10)
    for bullet in dead_bullets:
        bullet.draw(screen, (255, 0, 0))


def main(screen: pygame.display.set_mode, clock: pygame.time.Clock()):
    timer = 0

    player_bullets = Bullets(6, 5, 28)
    player = Player('assets/player.png', 607, 740) 
    
    enemies = []
    dead_bullets = []

    font = pygame.font.SysFont('arial', 25)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_RIGHT:
                        player.player_move[0] = 5
                    case pygame.K_LEFT:
                        player.player_move[0] = -5
                    case pygame.K_UP:
                        player.player_move[1] = -5
                    case pygame.K_DOWN:
                        player.player_move[1] = 5
                    case pygame.K_SPACE:
                        player.shot = True
            if event.type == pygame.KEYUP:
                match event.key:
                    case pygame.K_LEFT:
                        player.player_move[0] = 0
                    case pygame.K_RIGHT:
                        player.player_move[0] = 0
                    case pygame.K_UP:
                        player.player_move[1] = 0
                    case pygame.K_DOWN:
                        player.player_move[1] = 0
                    case pygame.K_SPACE:
                        player.shot = False

        screen.fill((0, 0, 0))

        if player.handle(screen, player_bullets, enemies, dead_bullets) == -1:
            break;
        player_bullets.handle(screen, (255, 0, 0), 0, -10)

        remove_enemies(enemies, dead_bullets)
        handle_dead_bullets(dead_bullets, screen)

        timer = append_enemy(enemies, timer)

        for enemy, enemy_bullets in enemies:
            enemy.handle(player_bullets, screen, enemy_bullets, player)
            enemy_bullets.handle(screen, (255, 0, 0), 0, 10)

        screen.blit(font.render(f'Score: {player.points}', True, (255, 255, 255)), (20, 20))

        pygame.display.update()

        clock.tick(60)
    
    print(f"Score: {player.points}")


def menu(screen: pygame.display.set_mode, clock: pygame.time.Clock()):
    running = True
    playing = False

    title_font = pygame.font.SysFont('arial', 55)
    menu_font = pygame.font.SysFont('arial', 35)
    WHITE = (255, 255, 255)

    title = title_font.render('Space Defenders', False, (100, 100, 255))
    
    play = menu_font.render('Play', False, WHITE)
    play_rect = play.get_rect()
    play_rect.topleft = (100, 350)
    
    htp = menu_font.render('How to play', False, WHITE)
    htp_rect = htp.get_rect()
    htp_rect.topleft = (100, 450)

    credits_ = menu_font.render('Credits', False, WHITE)
    credits_rect = credits_.get_rect()
    credits_rect.topleft = (100, 550)

    quit_ = menu_font.render('Quit', False, WHITE)
    quit_rect = quit_.get_rect()
    quit_rect.topleft = (100, 650)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False 
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(pygame.mouse.get_pos()):
                    running = False
                    playing = True

        screen.blit(title, (100, 100))
        screen.blit(play, (100, 350))
        screen.blit(htp, (100, 450))
        screen.blit(credits_, (100, 550))
        screen.blit(quit_, (100, 650))

        pygame.display.update()
        clock.tick(60)

    return True if playing else False


if __name__ == '__main__':
    screen = pygame.display.set_mode((1239, 880))
    pygame.display.set_caption('Space-Defenders')
    pygame.display.set_icon(pygame.image.load('assets/player.png'))

    clock = pygame.time.Clock()

    if menu(screen, clock):
        main(screen, clock)
