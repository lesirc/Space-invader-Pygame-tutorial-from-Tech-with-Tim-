
# Python project
# Pygame
# Members:
# C0879976 - Ishant 
# C0881810 - Ma Criselda Martirez 
# C0863836 - Michelle Hementera
import os
import time
import random
import pygame
import pygame_gui
pygame.font.init()
pygame.freetype.init()
import mysql.connector

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space invader by Ishant && Crisel && Michi")

# enemy ship
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# player ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# lasers of ships
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# load background as same size the window load
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "space.png")), (WIDTH, HEIGHT))

# class Laser: #super class for laser
#     def __init__(self, x, y, img):
#         self.x = x 
#         self.y = y
#         self.img = img
#         self.mask = pygame.mask.from_surface(self.img)
class Laser:
    def __init__(self, x, y, img, win_width, win_height, img_width, img_height):
        # self.x = x + (img_width // 2) - (YELLOW_LASER.get_width() // 2)
        self.x = x + (img_width // 2) - (img.get_width() // 2)

        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
        self.win_width = win_width
        self.win_height = win_height
        self.img_width = img_width
        self.img_height = img_height

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Cat: #super class for cats
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            # laser = Laser(self.x, self.y, self.laser_img)
            laser = Laser(self.x, self.y, self.laser_img, WIDTH, HEIGHT, self.get_width(), self.get_height())

            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Cat): #inherits Cat class
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Cat): #inherits Cat class
    COLOR_MAP = {
                "red": (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }

    def __init__(self, x, y, color, health=100):
        # "red", "green", "blue"
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            # player_laser = Laser(player.x, player.y, YELLOW_LASER, WIDTH, HEIGHT, player.get_width(), player.get_height())
            laser = Laser(self.x, self.y, self.laser_img, WIDTH, HEIGHT, self.get_width(), self.get_height())

            # laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main(manager, name):
    run = True
    FPS = 60
    level = 0
    lives = 3
    main_font = pygame.font.SysFont("timesnewroman", 20)
    lost_font = pygame.font.SysFont("timesnewroman", 60)

    enemies = []
    wave_length = 5
    enemy_vel = 1

#pixel move
    player_vel = 5
    laser_vel = 5
    player = Player(300, 630)
    clock = pygame.time.Clock()
    lost = False
    lost_count = 0

    def redraw_window():
        WIN.blit(BG, (0,0)) #display background

        # display level and lives
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))

        #level and lives on the same side
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (10, 40))
        # WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

        pygame.display.update() #refresh display

    while run:
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
        
#connect to mysql db with credentials to save player info        
                connection = None
                try:
                    connection = mysql.connector.connect(
                        # host="localhost",
                        # user="root",
                        # password="sql123@",
                        # database="ishantdb1",
                        # auth_plugin='mysql_native_password'
                        host="localhost",
                        user="root",
                        password="root",
                        database="testdatabase"
                    )   
                    cursor = connection.cursor()
                    #save player info
                    cursor.execute(f"INSERT INTO score (name, level) VALUES ('{name}', {level})")
                    connection.commit()
                except mysql.connector.Error as error:
                    print("Failed to insert record into MySQL table:", error)
                finally:
                    if connection is not None and connection.is_connected():
                        cursor.close()
                        connection.close()
                        print("MySQL connection is closed")
                
                    run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

# loop when something happens
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit() #end game

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

#number of enemy ship and laser frequency
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

       # redraw_window()
        player.move_lasers(-laser_vel, enemies)


def main_menu(manager):
    title_font = pygame.font.SysFont("timesnewroman", 70)
    input_font = pygame.font.SysFont("timesnewroman", 30)
    run = True
    name = ""
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Enter Your Name:", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 200))
        
        # create input box
        input_box = pygame.Rect(WIDTH/2 - 100, 300, 200, 50)
        pygame.draw.rect(WIN, (255,255,255), input_box, 2)
        input_label = input_font.render(name, 1, (255,255,255))
        WIN.blit(input_label, (input_box.x + 10, input_box.y + 10))

        submit_label = input_font.render("Submit", 1, (255,255,255))
        submit_button = pygame.Rect(WIDTH/2 - 50, 400, 100, 50)
        pygame.draw.rect(WIN, (0, 255, 0), submit_button)
        WIN.blit(submit_label, (submit_button.x + 10, submit_button.y + 10))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                # pygame.quit()
                # sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if submit_button.collidepoint(mouse_pos):
                    if len(name) > 0:
                        main(manager, name)
                    else:
                        error_font = pygame.font.SysFont("timesnewroman", 40)
                        error_label = error_font.render("Please enter your name!", 1, (255,0,0))
                        WIN.blit(error_label, (WIDTH/2 - error_label.get_width()/2, 500))
                        pygame.display.update()

    pygame.quit()
    sys.exit()

# library ui
manager = pygame_gui.UIManager((WIDTH, HEIGHT))
main_menu(manager)