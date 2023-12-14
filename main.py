import pygame
import os
import random
import time
pygame.font.init() # for font
pygame.mixer.init()


WIDTH, HEIGHT = 600, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Impact")

#music
bg_music_path = os.path.join("assets", "bgmusic_space_impact.mp3")
pygame.mixer.music.load(bg_music_path)
pygame.mixer.music.play(-1)

#load images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

#PLAYER SHIP
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

#laSERS
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
                                                  
#background #SCALING THE IMAGE TO FILL THE ENTIRE SCREEN USED pygame.transform.scale function
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")),(WIDTH, HEIGHT))                                            

#laser class
class Laser:
    def __init__(self, x, y, img):
        self.x =x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel): #laser movement
        self.y += vel

    def off_screen(self, height):
        return not(self.y <= height and self.y >= 0)
    
    def collision(self, obj):
        return collide(self, obj) # call the function of collision
    
        
    
#characters class

class Ship:
    COOLDOWN = 15
    
    def __init__(self, x, y, health = 100): #designating position of ships
        self.x = x
        self.y = y # seting up attributes for the class
        self.health = health
        self.ship_img = None   #allows to draw the sips and lasers
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0 #prevents shooting spams

    def draw(self, window):
       window.blit(self.ship_img,(self.x,self.y)) #draws ship
       for laser in  self.lasers:
           laser.draw(window)

    def move_lasers(self, vel, obj): #laser movement #checks if the lasers hit the player
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT): #lasers off sccreen will be removed
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)# when it hits the player it will disappear
    

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0: #if not 0 will not increment
            self.cool_down_counter += 1 #cooldwon counter increments by 1
        

    
    def shoot(self): #creates the laser
        if self.cool_down_counter == 0:
            laser = Laser(self.x,self.y, self.laser_img) #laser cooldown counter
            self.lasers.append(laser)
            self.cool_down_counter = 1 #cooldown counter reset    
            

    def get_width(self): #border restriction fix
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship): #uses the ship class aboce

    def __init__(self, x, y, health=100):
        super().__init__(x, y, health) #initializes class ship
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img) #enables pixel perfect collision
        self.max_health = health #defining health maximum

        
    def move_lasers(self, vel, objs): #laser movement #checks if the lasers hit the enemies
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT): #lasers off sccreen will be removed
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
        

    def healthbar(self, window): #healthbar
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width()*(self.health/self.max_health), 10))
        
        
        
class Enemy(Ship):
    COLOR_MAP = { #dictionary for enemy color
                "red":  (RED_SPACE_SHIP, RED_LASER),
                "green": (GREEN_SPACE_SHIP, GREEN_LASER),
                "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
                }
    
    def __init__(self, x, y, color, health=100): 
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color] #using the dictionary
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel): #enemy ship movement
        self.y += vel

        
        

    
    def shoot(self): #creates the laser
        if self.cool_down_counter == 0:
            laser = Laser(self.x-20,self.y, self.laser_img) #laser cooldown counter
            self.lasers.append(laser)
            self.cool_down_counter = 1 #cooldown counter reset    
            

    
        
def collide(obj1, obj2): #mask object ot tell if the pixels really collide
    offset_x = obj2.x - obj1.x # distance between two obj
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None #did the two objects collide?
    

#main game loop
def main():
    run = True
    fps = 60
    level = 0 #count of level
    lives = 5 # lives, can be decreased
    main_font = pygame.font.SysFont("comicsans", 40)
    lost_font = pygame.font.SysFont("comicsans", 60)


    enemies = [] #store all the enemies
    wave_length = 5 #every level generates new enemy wave moving down
    enemy_vel = 1 #enemy movement 1px
    
    player_vel = 5 #allows key to move 5px
    laser_vel = 5

    player = Player(275, 490) # position of ship
    
    clock = pygame.time.Clock()

    lost = False
    lost_count = 0
    

    def redraw_window():
        WIN.blit(BG, (0,0)) #blit takes the images place want
        #draw text
        lives_label = main_font.render(f"Lives: {lives}", 1,(255,255,255))
        level_label = main_font.render(f"Level: {level}", 1,(255,255,255))

        WIN.blit(lives_label, (10,10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10)) #positions level on the top right of screen

        for enemy in enemies:
            enemy.draw(WIN)
        
        player.draw(WIN) #displays ship

        if lost:
            lost_label = lost_font.render("You Lost!", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/ 2, 350)) #display lost
            
            
        
        pygame.display.update()
        
    while run:
        clock.tick(fps)

        redraw_window()


        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > fps * 3: #pause and quit the game when player lost
                run = False
            else:
                continue
                
            
        
        #spawn enemies
        if len(enemies) == 0:
            level += 1 #as soon as no more enemies are in the screen increments level
            wave_length += 3 #increment the spawn
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-500, -100), random.choice(["red","blue","green"]))#rand position of enemy
                enemies.append(enemy)              

            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        #key tracker # movment of character
        key = pygame.key.get_pressed() #key dictionary allows user to press any key in certain diraction
        if key[pygame.K_a] and player.x - player_vel > 0: #allows to indetify key designation #move left
            player.x -= player_vel
        if key[pygame.K_d] and player.x + player_vel + player.get_width() < WIDTH: #right
            player.x += player_vel
        if key[pygame.K_w] and player.y - player_vel > 0: #up
            player.y -= player_vel 
        if key[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: #down #RESTRICTS MOVEMENT
            player.y += player_vel
        if key[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies: #enemy movement #enemies lasers
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            #enemy shoots randomly prob %50 enemy shoots
            if random.randrange(0, 4*60) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10 #enemy collision will reduce health
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                    lives -= 1
                    enemies.remove(enemy)#remove enemy obj and decrement life

            
        

         #negative vel makes lasers go up                   
        player.move_lasers(-laser_vel, enemies)#check if lasers collided with enemies
    pygame.mixer.music.stop()
    
#main menu loop
def main_menu():
    title_font = pygame.font.SysFont("comicsans", 40)
    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
        
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()
        
        
main_menu() # update: balance enemy shoot pprobabiloty, increased player laser spam
            











                
