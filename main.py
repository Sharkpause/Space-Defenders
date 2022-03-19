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


def main(screen: pygame.display.set_mode, clock: pygame.time.Clock):
    timer = 0

    player_bullets = Bullets(6, 5, 28)
    player = Player('assets/player.png', 607, 740) 
    
    enemies = []
    dead_bullets = []

    r_down = False
    l_down = False
    u_down = False
    d_down = False

    font = pygame.font.SysFont('arial', 25)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_RIGHT:
                        player.player_move[0] = 5
                        r_down = True
                    case pygame.K_LEFT:
                        player.player_move[0] = -5
                        l_down = True
                    case pygame.K_UP:
                        player.player_move[1] = -5
                        u_down = True
                    case pygame.K_DOWN:
                        player.player_move[1] = 5
                        d_down = True
                    case pygame.K_SPACE:
                        player.shot = True
            if event.type == pygame.KEYUP:
                match event.key:
                    case pygame.K_LEFT:
                        player.player_move[0] = 0
                        l_down = False
                    case pygame.K_RIGHT:
                        player.player_move[0] = 0
                        r_down = False
                    case pygame.K_UP:
                        player.player_move[1] = 0
                        u_down = False
                    case pygame.K_DOWN:
                        player.player_move[1] = 0
                        d_down = False
                    case pygame.K_SPACE:
                        player.shot = False

                if r_down: player.player_move[0] = 5
                if l_down: player.player_move[0] = -5
                if u_down: player.player_move[1] = -5
                if d_down: player.player_move[1] = 5

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

    return (running, player.points)


def menu(screen: pygame.display.set_mode, clock: pygame.time.Clock):
    running = True
    playing = False

    code = 0

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

    quit_ = menu_font.render('Quit', False, WHITE)
    quit_rect = quit_.get_rect()
    quit_rect.topleft = (100, 550)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                code = 4
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(pygame.mouse.get_pos()):
                    running = False
                    playing = True
                    code = 1
                if htp_rect.collidepoint(pygame.mouse.get_pos()):
                    running = False
                    code = 2
                if quit_rect.collidepoint(pygame.mouse.get_pos()):
                    running = False
                    code = 3

        screen.fill((0, 0, 0))

        screen.blit(title, (100, 150))
        screen.blit(play, play_rect.topleft)
        screen.blit(htp, htp_rect.topleft)
        screen.blit(quit_, quit_rect.topleft)

        pygame.display.update()
        clock.tick(60)

    return code


def htp_screen(screen: pygame.display.set_mode, clock: pygame.time.Clock):
    running = True
    code = 0

    font = pygame.font.SysFont('arial', 30)

    htp_text0 = font.render('Shoot the enemies to get a point, avoid the enemies bullet in order not to die',  True, (255, 255, 255))
    htp_text1 = font.render('Arrow keys to move', True, (255, 255, 255))
    htp_text2 = font.render('Spacebar to shoot', True, (255, 255, 255))

    back = font.render('<- Back',  True, (255, 255, 255))
    back_rect = back.get_rect()
    back_rect.topleft = (80, 800)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_rect.collidepoint(pygame.mouse.get_pos()):
                    code = 1
                    running = False

        screen.fill((0, 0, 0))
        
        screen.blit(htp_text0, (170, 300))
        screen.blit(htp_text1, (480, 400))
        screen.blit(htp_text2, (490, 500))
        screen.blit(back, (40, 800))

        pygame.display.update()
        clock.tick(60)
    
    return code


def game_over(screen: pygame.display.set_mode, clock: pygame.time.Clock, points: int):
    font = pygame.font.SysFont('arial', 50)
    
    text = font.render('Game Over!', True, (255, 255, 255))
    score = font.render(f'Score: {points}', True, (255, 255, 255))
    
    again = font.render('Play again', True, (255, 255, 255))
    again_rect = again.get_rect()
    again_rect.topleft = (520, 420)

    menu = font.render('Back to Menu', True, (255, 255, 255))
    menu_rect = menu.get_rect()
    menu_rect.topleft = (490, 520)

    quit_ = font.render('Quit', True, (255, 255, 255))
    quit_rect = quit_.get_rect()
    quit_rect.topleft = (570, 620)

    running = True
    code = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                code = 3
            if event.type == pygame.MOUSEBUTTONDOWN:
                if again_rect.collidepoint(pygame.mouse.get_pos()):
                    running = False
                    code = 1
                if menu_rect.collidepoint(pygame.mouse.get_pos()):
                    running = False
                    code = 2
                if quit_rect.collidepoint(pygame.mouse.get_pos()):
                    running = False
                    code = 3

        screen.fill((0, 0, 0))

        screen.blit(text, (510, 150))
        screen.blit(score, (540, 220))
        screen.blit(again, again_rect.topleft)
        screen.blit(menu, menu_rect.topleft)
        screen.blit(quit_, quit_rect.topleft)

        pygame.display.update()
        clock.tick(60)

    return code


if __name__ == '__main__':
    screen = pygame.display.set_mode((1239, 880))
    pygame.display.set_caption('Space-Defenders')
    pygame.display.set_icon(pygame.image.load('assets/player.png'))

    clock = pygame.time.Clock()
    
    quit = False

    while not quit:
        match menu(screen, clock):
            case 1:
                running = True
                while running:
                    result = main(screen, clock)
                    if result[0]:
                        match game_over(screen, clock, result[1]):
                            case 1:
                                continue
                            case 2:
                                break
                            case 3:
                                running = False
                                quit = True
            case 2:
                if not htp_screen(screen, clock):
                    break
            case 3:
                quit = True
