from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math 
import time
fovY = 80
camera_pos = (0,800,800)
camera_angle = 0
player_position = [-900,900,0]
player_angle = 90
player_health= 3
player_life = 2
coin_radius=30
coins = []  
coin_color = (1, 1, 0) 
num_coins = 0
alive = True
level = 1
game_won = False


#player leg
left_leg_angle = 5
left_calf_angle = -10

right_leg_angle = -5
right_calf_angle = 10

wall_positions = []
door_coordinate = None

enemies = []
bullets = []
bullets_miss = 0

score = 0
coins_collected = 0
power_up_damage = None
power_up_health = None
power_up_wall = None
dpu_collected = False
dpu_start_time = 0
wpu_collected = False
wpu_start_time = 0

reached_door = False
cheat_mode = False

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top

    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
def setupCamera():
    if cheat_mode == True:
        global camera_pos, camera_angle
        glMatrixMode(GL_PROJECTION)  
        glLoadIdentity() 
        gluPerspective(fovY, 1.25, 1, 5000) #(field of view, aspect ratio, near clip, far clip)
        glMatrixMode(GL_MODELVIEW)  # Switch to model-view matrix mode
        glLoadIdentity()  # Reset the model-view matrix
        x, y, z = camera_pos
        x = 800* math.sin(math.radians(camera_angle))
        y = 800* math.cos(math.radians(camera_angle))
        z = camera_pos[2]
        gluLookAt(x,y,z, 
                0, 0, 0,  # Look-at target
                0, 0, 1)
    else:

        #First person mode
        global player_position, player_angle

        # Player's eye position
        eye_x = player_position[0]
        eye_y = player_position[1]
        eye_z = player_position[2] + 180  

        # Direction the player is facing
        rad = math.radians(player_angle)
        center_x = eye_x + math.sin(rad)*100
        center_y = eye_y - math.cos(rad)*100
        center_z = 120

        # Up vector remains pointing up
        up_x, up_y, up_z = 0, 0, 1

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(fovY, 1.25, 0.1, 1500)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(eye_x, eye_y, eye_z,
                center_x, center_y, center_z,
                up_x, up_y, up_z)

def specialKeyListener(key, x, y):
    global camera_pos, camera_angle
    x, y, z = camera_pos
    # Move camera up (UP arrow key)
    if key == GLUT_KEY_UP:
       z+=20
       z = min(z, 2500)
    # # Move camera down (DOWN arrow key)
    if key == GLUT_KEY_DOWN:
        z-=20
        z=max(z,10)
    # moving camera left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        camera_angle += 5
        camera_angle %= 360
    # moving camera right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        camera_angle -= 5
        camera_angle %= 360

    camera_pos = (x, y, z)
    glutPostRedisplay()
def keyboardListener(key, x, y):
    global player_angle, player_position, door_coordinate, alive, score, player_life, player_health, enemies, bullets, wall_positions, coins_collected, cheat_mode, level, game_won
    move_step = 5
    new_x, new_y = player_position[0], player_position[1]
    if alive == True or game_won == False:
        if key == b'w':
            new_x += math.sin(math.radians(player_angle)) * move_step
            new_y -= math.cos(math.radians(player_angle)) * move_step
        elif key == b's':
            new_x -= math.sin(math.radians(player_angle)) * move_step
            new_y += math.cos(math.radians(player_angle)) * move_step

        # Check if new position would cause collision
        
        if not check_position_collision(new_x, new_y) or wpu_collected == True:

                if -1000 < new_x < 1000:
                    player_position[0] = new_x
                if -1000 < new_y < 1000:
                    player_position[1] = new_y
        if key == b'a':   
            player_angle += 5
            player_angle %= 360
        if key == b'd':  
            player_angle -= 5
            player_angle %= 360
    if key == b'r':
        if alive==False or game_won == True:
            score = 0
            coins_collected = 0
            player_life = 2
            player_health = 3
            alive = True
            num_new_coins = 2 
            level = 1
            player_position = [-900,900,0]
            player_angle = 90
            game_won = False
            wall_positions.clear()
            enemies.clear()
            bullets.clear()
            generate_coins(num_new_coins)
            door_coordinate = None
        print(alive)

    if key == b'c':  #Rotate right (R key)
            cheat_mode = not cheat_mode

    glutPostRedisplay()    
def mouseListener(button, state, x, y):

    global first_person_mode
    """
    Handles mouse inputs for firing bullets (left click) and toggling camera mode (right click).
    """
        # # Left mouse button fires a bullet
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        shoot()

def draw_player():
    global player_position,player_angle, left_calf_angle,left_leg_angle,right_calf_angle,right_leg_angle
    glPushMatrix()
    glTranslatef(*player_position)
    glScalef(.5,.5,.5)
    glRotatef(player_angle,0,0,1)

    if alive == False:
        glRotatef(90,1,0,0)
    # legs (thigh and calf)
    # LEFT LEG
    glPushMatrix()
    glColor3f(1, 195/255, 170/255)
    glTranslatef(-25, 0, 0)  # Move to leg position
    glRotatef(left_leg_angle, 1, 0, 0)  # Rotate thigh
    # Thigh
    gluCylinder(gluNewQuadric(), 10, 10, 30, 10, 10)

    # Move to knee joint
    glTranslatef(0, 0, 30)
    glRotatef(left_calf_angle, 1, 0, 0)  # Rotate calf
    # Calf
    gluCylinder(gluNewQuadric(), 10, 10, 30, 10, 10)
    glPopMatrix()

    # RIGHT LEG
    glPushMatrix()
    glColor3f(1, 195/255, 170/255)
    glTranslatef(25, 0, 0)
    glRotatef(right_leg_angle, 1, 0, 0)
    # Thigh
    gluCylinder(gluNewQuadric(), 10, 10, 30, 10, 10)

    # Move to knee
    glTranslatef(0, 0, 30)
    glRotatef(right_calf_angle, 1, 0, 0)
    # Calf
    gluCylinder(gluNewQuadric(), 10, 10, 30, 10, 10)
    glPopMatrix()

    # pants (covering thighs)
    glPushMatrix()
    glColor3f(1, 1, 1)
    glTranslatef(-25, 0, 60) 
    gluCylinder(gluNewQuadric(), 15, 15, 40, 10, 10) 
    glPopMatrix()

    glPushMatrix()
    glColor3f(1, 1, 1)
    glTranslatef(25, 0, 60) 
    gluCylinder(gluNewQuadric(), 15,15, 40, 10, 10)
    glPopMatrix()
    #shoes
    glPushMatrix()
    glColor3f(.5, 0, 1)
    glTranslatef(-25, 0, 0) 
    glScalef(1,1,0.5)
    glutSolidCube(20)
    glPopMatrix()

    glPushMatrix()
    glColor3f(.5, 0, 1)
    glTranslatef(25, 0, 0) 
    glScalef(1,1,0.5)
    glutSolidCube(20)

    glPopMatrix()
        #body
    glPushMatrix()
    glColor3f(0.9,0.2,0.8)
    glTranslatef(0,0,100)
    gluCylinder(gluNewQuadric(), 40, 40, 80, 10, 10)
    glPopMatrix()
    glPushMatrix()
    glColor3f(0.9,0.2,0.8)
    glTranslatef(-50,0,140)
    gluCylinder(gluNewQuadric(), 12, 12, 40, 10, 10)
    glPopMatrix()
    glPushMatrix()
    glColor3f(0.9,0.2,0.8)
    glTranslatef(50,0,140)
    gluCylinder(gluNewQuadric(), 12, 12, 40, 10, 10)
    glPopMatrix()
    #hands
    glPushMatrix()
    glColor3f(1, 195/255, 170/255)
    glTranslatef(-50, 0, 160) 
    glRotatef(80, 1, 0, 0) 
    gluCylinder(gluNewQuadric(), 8, 6, 60, 10, 10)  
    glPopMatrix()
    glPushMatrix()
    glColor3f(1, 230/255, 170/255)
    glTranslatef(50, 0, 160) 
    glRotatef(140, 1, 0, 0) 
    gluCylinder(gluNewQuadric(), 8, 6, 60, 10, 10) 
    glPopMatrix()
    #gun
    glPushMatrix()
    glColor3f(.4, .4, .4)
    glTranslatef(-50, -60, 170) 
    glRotatef(80, 1, 0, 0) 
    gluCylinder(gluNewQuadric(), 8, 6, 30, 10, 10)  
    glPopMatrix()
    glPushMatrix()
    glColor3f(198/255, 136/255, 66/255)
    glTranslatef(-50, -60, 170) 
    glRotatef(120, 1, 0, 0) 
    gluCylinder(gluNewQuadric(), 8, 6, 10, 10, 10)  
    glPopMatrix()
    #neck
    glPushMatrix()
    glColor3f(1, 195/255, 170/255)
    glTranslatef(0, 0, 180) 
    gluCylinder(gluNewQuadric(), 10,10, 10, 10, 10) 
    glPopMatrix()
     # head (now skin color)
    glPushMatrix()
    glColor3f(1, 195/255, 170/255)
    glTranslatef(0, 0, 220)
    gluSphere(gluNewQuadric(), 35, 10, 10)
    glPopMatrix()

    # hair (a dark cap)
    glPushMatrix()
    glColor3f(0.1, 0.1, 0.1)  # black hair
    glTranslatef(0, 0, 240)
    glScalef(1.0, 1.0, 0.5)  # flatten to make it look like a cap
    gluSphere(gluNewQuadric(), 35, 10, 10)
    glPopMatrix()
    #healthbar
    glPushMatrix()
    glColor3f(.4, .4, .4)
    glTranslatef(-35, 0, 250)
    glRotatef(90,0,1,0)
    gluCylinder(gluNewQuadric(), 5,5,75, 10, 10)
    glPopMatrix()
    glPushMatrix()
    glColor3f(0, .7, 0)
    glTranslatef(-35, 0, 250)
    glRotatef(90,0,1,0)
    height = 75*(player_health/3)
    gluCylinder(gluNewQuadric(), 5,5,height, 10, 10)
    glPopMatrix()
    
    glPopMatrix()  

    
    
def draw_floor():
    glBegin(GL_QUADS)
    glColor3f(0,0.2,0.1)
    glVertex3f(-3600,-3600,0)
    glVertex3f(3600,-3600,0)
    glVertex3f(3600, 3600, 0)
    glVertex3f(-3600, 3600, 0)
    glEnd()

    glBegin(GL_QUADS)
    glColor3f(0.2,0.4,0.1)
    glVertex3f(-1000,-1000,0)
    glVertex3f(1000,-1000,0)
    glVertex3f(1000, 1000, 0)
    glVertex3f(-1000, 1000, 0)
    glEnd()
    glBegin(GL_QUADS)
    glColor3f(0.5,0.3,0.05)
    glVertex3f(-1000,-1000,0)
    glVertex3f(1000,-1000,0)
    glVertex3f(1000,-1000,200)
    glVertex3f(-1000,-1000,200)

    
    glVertex3f(-1000,-1000,0)
    glVertex3f(-1000,1000,0)
    glVertex3f(-1000,1000,200)
    glVertex3f(-1000,-1000,200)
    
    glVertex3f(1000,-1000,0)
    glVertex3f(1000,1000,0)
    glVertex3f(1000,1000,200)
    glVertex3f(1000,-1000,200)
    
    glVertex3f(1000,1000,0)
    glVertex3f(-1000,1000,0)
    glVertex3f(-1000,1000,200)
    glVertex3f(1000,1000,200)
    glEnd()

# def draw_door(coordinates):
#     glBegin(GL_QUADS)
#     glColor3f(0,0,.2)
#     glVertex3f(*coordinates[0])   
#     glVertex3f(*coordinates[1])   
#     glVertex3f(*coordinates[2]) 
#     glVertex3f(*coordinates[3]) 
#     glEnd()
def draw_door(coordinates):
    x1, y1, z1 = coordinates[0]
    x2, y2, z2 = coordinates[1]
    x3, y3, z3 = coordinates[2]
    x4, y4, z4 = coordinates[3]

    # Draw outer frame
    glBegin(GL_QUADS)
    glColor3f(0.5,0.3,0.05)
    glVertex3f(x1 , y1 , z1)
    glVertex3f(x2 , y2 , z2)
    glVertex3f(x3 , y3 , z3+50)
    glVertex3f(x4 , y4 , z4+50)
    glEnd()
    glBegin(GL_QUADS)
    glColor3f(0, 0, 0.2)
    for vertex in coordinates:
        glVertex3f(*vertex)
    glEnd()

    

    # Calculate text position (centered horizontally, a bit above the top edge)
    text_x = (x1 + x2) / 2
    text_y = (y1 + y2) / 2
    text_z = max(z3, z4) + 20  # 20 units above the door

    # Draw 'ENTER' text
    glColor3f(1, 1, 1)
    glRasterPos3f(text_x , text_y, text_z)  # Adjust for centering text width
    for ch in "ENTER":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
   
def draw_wall(x, y, width, height, depth=100):
    glPushMatrix()
    glColor3f(85/255, 53/255, 16/255)  
    glTranslatef(x, y, depth )  
    glScalef(width, height, depth)  
    glutSolidCube(1) 
    glPopMatrix()


def draw_axes_with_labels(length=1000, interval=100, font=GLUT_BITMAP_HELVETICA_12):
    glLineWidth(3)
    glBegin(GL_LINES)

    # X axis – Red
    glColor3f(1, 0, 0)
    glVertex3f(-length, 0, 0)
    glVertex3f(length, 0, 0)

    # Y axis – Green
    glColor3f(0, 1, 0)
    glVertex3f(0, -length, 0)
    glVertex3f(0, length, 0)

    # Z axis – Blue
    glColor3f(0, 0, 1)
    glVertex3f(0, 0, -length)
    glVertex3f(0, 0, length)

    glEnd()
    glLineWidth(1)

    # Draw tick marks and labels on all axes
    def draw_label(x, y, z, text, color=(1, 1, 1)):
        glColor3f(*color)
        glRasterPos3f(x, y, z)
        for ch in text:
            glutBitmapCharacter(font, ord(ch))

    # Draw ticks and labels along each axis
    for i in range(-length, length + 1, interval):
        if i == 0:
            continue  # Skip origin

        # X-axis ticks and labels
        glColor3f(1, 0, 0)
        glBegin(GL_LINES)
        glVertex3f(i, -5, 0)
        glVertex3f(i, 5, 0)
        glEnd()
        draw_label(i, 10, 0, str(i), (1, 0.5, 0.5))

        # Y-axis ticks and labels
        glColor3f(0, 1, 0)
        glBegin(GL_LINES)
        glVertex3f(-5, i, 0)
        glVertex3f(5, i, 0)
        glEnd()
        draw_label(10, i, 0, str(i), (0.5, 1, 0.5))

        # Z-axis ticks and labels
        glColor3f(0, 0, 1)
        glBegin(GL_LINES)
        glVertex3f(0, -5, i)
        glVertex3f(0, 5, i)
        glEnd()
        draw_label(0, 10, i, str(i), (0.5, 0.5, 1))

    # Label the origin
    draw_label(0, 0, 0, "0", (1, 1, 1))

def generate_walls():
    global wall_positions, level
    wall_height = 100
    wall_thickness = 20
    
    wall_positions = [
    # Outer box
    (-1000, 0, wall_thickness, 2000, wall_height),  # right
    (1000, 0, wall_thickness, 2000, wall_height),   # left
    (0, 1000, 2000, wall_thickness, wall_height),   # Top
    (0, -1000, 2000, wall_thickness, wall_height),  # Bottom


    (-400 + 125, 800, 1300 , wall_thickness, wall_height),   
    (500, 650, wall_thickness, 700, wall_height),                               
    (0, 300, 650, wall_thickness, wall_height),                     
    (-450, 350, wall_thickness, 700, wall_height),     
    (-450 + 125, 600, 1000 , wall_thickness, wall_height) ,
    (-500 + 125, -500, 1200 , wall_thickness, wall_height) ,
    (-750 + 125, -250, 800 , wall_thickness, wall_height) ,
    (400 + 125, 100, -600 , wall_thickness, wall_height) ,
    (300 + 125, -200, -300 , wall_thickness, wall_height) ,
    (-700, 100, wall_thickness, 700, wall_height), 
    (370 + 125, -800, -500 , wall_thickness, wall_height) , 
    (-400 + 125, -800, 1100 , wall_thickness, wall_height) ,                                                                                                                                                                                                                                                                                                                                                                                             # Left Vertical
    (-800, -650, wall_thickness, 300, wall_height),
 
    (-350 + 125, 0, 600, wall_thickness, wall_height),     
    (0, -150, wall_thickness, 300, wall_height),                               
    (100 + 125, -300, 150, wall_thickness, wall_height),   
    (300, -150, wall_thickness, 300, wall_height),
    (750, -300, wall_thickness, 1000, wall_height),                                                                     
    
    (300, 150, wall_thickness, 300, wall_height),                               
    (100 + 125, 300, 150, wall_thickness, wall_height),    

    (0, 450, 300, wall_thickness, wall_height),                                 
    (120, 550, wall_thickness, 180, wall_height),                              
]




def draw_maze():
    for wall in wall_positions:
        draw_wall(*wall)

def generate_coins(coins_num):
    global coins, wall_positions, power_up_damage, power_up_health, power_up_wall
    
    coins = []  
    power_up_damage = None  
    power_up_health = None 
    power_up_wall = None 

    min_wall_distance = 100
    min_coin_distance = 500

    def is_position_valid(x, y, z, existing_positions):
        # Check wall collision
        for wall in wall_positions:
            wx, wy, ww, wh, wd = wall
            x_dist = max(abs(x - wx) - ww / 2, 0)
            y_dist = max(abs(y - wy) - wh / 2, 0)
            if x_dist < min_wall_distance and y_dist < min_wall_distance:
                return False

        # Check distance to other objects
        for obj in existing_positions:
            ox, oy, oz = obj
            dist = math.sqrt((x - ox) ** 2 + (y - oy) ** 2)
            if dist < min_coin_distance:
                return False
        return True

    # Generate coins
    for _ in range(coins_num):
        valid = False
        attempts = 0
        while not valid and attempts < 300:
            attempts += 1
            x = random.randint(-900, 900)
            y = random.randint(-900, 900)
            z = 10
            if is_position_valid(x, y, z, coins):
                coins.append((x, y, z))
                valid = True

    # Combine coins as existing positions to avoid overlap with power-ups
    all_positions = coins.copy()

    # generate damage power-up
    valid = False
    attempts = 0
    while not valid and attempts < 300:
        attempts += 1
        x = random.randint(-900, 900)
        y = random.randint(-900, 900)
        z = 10
        if is_position_valid(x, y, z, all_positions):
            power_up_damage = (x, y, z)
            all_positions.append(power_up_damage)
            valid = True

    # generate health power-up
    valid = False
    attempts = 0
    while not valid and attempts < 300:
        attempts += 1
        x = random.randint(-900, 900)
        y = random.randint(-900, 900)
        z = 10
        if is_position_valid(x, y, z, all_positions):
            power_up_health = (x, y, z)
            valid = True

    #generate wall power-up
    valid = False
    attempts = 0
    while not valid and attempts < 300:
        attempts += 1
        x = random.randint(-900, 900)
        y = random.randint(-900, 900)
        z = 10
        if is_position_valid(x, y, z, all_positions):
            power_up_wall = (x, y, z)
            valid = True


def draw_coins():
    glColor3f(*coin_color)
    for coin in coins:
        x, y, z = coin
        glPushMatrix()
        glTranslatef(x, y, z)
        gluSphere(gluNewQuadric(), coin_radius, 20, 20)
        glPopMatrix()

def draw_power_up():
    
    x, y, z = power_up_damage
    glPushMatrix()
    glPushMatrix()
    glColor3f(170/255,215/255,0)
    glTranslatef(x, y, z)
    glRotatef(90,1,0,0)
    glScalef(.45,1,1)
    glutSolidCube(50)
    glPopMatrix()
    glPushMatrix()
    glColor3f(79/255,215/255,242/255)
    glTranslatef(x, y, z)
    glRotatef(90,1,0,0)
    glScalef(.4,1,1)
    glutSolidCube(40)
    glPopMatrix()
    glPopMatrix()

def draw_power_up_health():
    x, y, z = power_up_health
    glPushMatrix()
    glPushMatrix()
    glColor3f(1,0,0)
    glTranslatef(x, y, z)
    glScalef(.25,.25,1)
    glutSolidCube(50)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(1,.25,.25)
    glutSolidCube(50)
    glPopMatrix()
    glPopMatrix()

def draw_power_up_wall():
    x, y, z = power_up_wall
    glPushMatrix()
    glPushMatrix()
    glColor3f(56/255,67/255,219/255)
    glTranslatef(x, y, z)
    glRotatef(90,0,1,1)
    glScalef(.5,.5,1)
    glutSolidCube(50)
    glPopMatrix()
    
    glPopMatrix()




def draw_enemy(enemy_pos):
    glPushMatrix()
    glTranslatef(enemy_pos[0],enemy_pos[1],enemy_pos[2])
    
    glPushMatrix()
    glColor3f(200/255, 212/255, 245/255)
    glTranslatef(0, 0, 120)
    gluSphere(gluNewQuadric(), 50, 10, 10)
    glPopMatrix()
    glPushMatrix()
    glColor3f(200/255, 212/255, 245/255)
    glTranslatef(0, 0, 35)
    gluCylinder(gluNewQuadric(), 70,50,80, 10, 10)
    glPopMatrix()

     #eyes
    glPushMatrix()
    glColor3f(.35, .35, .35)
    glTranslatef(-15, 50, 142)
    glScalef(.7,1,1)
    gluSphere(gluNewQuadric(), 7, 10, 10)
    glPopMatrix()
    glPushMatrix()
    glColor3f(.35, .35, .35)
    glTranslatef(15, 50, 142)
    glScalef(.7,1,1)
    gluSphere(gluNewQuadric(), 7, 10, 10)
    glPopMatrix()
    glPushMatrix()
    glColor3f(.35, .35, .35)
    glTranslatef(0, 50, 122)
    gluSphere(gluNewQuadric(), 10, 10, 10)
    glPopMatrix()

    #healthbar
    glPushMatrix()
    glColor3f(.4, .4, .4)
    glTranslatef(-35, 0, 185)
    glRotatef(90,0,1,0)
    gluCylinder(gluNewQuadric(), 5,5,75, 10, 10)
    glPopMatrix()
    glPushMatrix()
    glColor3f(.6, 0, 0)
    glTranslatef(-35, 0, 185)
    glRotatef(90,0,1,0)
    height = 75*(enemy_pos[3]/3)
    gluCylinder(gluNewQuadric(), 5,5,height, 10, 10)
    glPopMatrix()
   
    glPopMatrix()

def spawn_enemy():
    global enemies, level
    while len(enemies)<3+level:
        x = random.uniform(-1000 + 50, 1000 - 50)
        y = random.uniform(-1000 + 50, 1000 - 50)
        while abs(x - player_position[0]) < 150:
            x = random.uniform(-1000 + 50, 1000 - 50)
        while abs(y - player_position[1]) < 150:
            y = random.uniform(-1000 + 50, 1000 - 50)
        enemies.append([x, y,random.uniform(20,30),3])

def enemy_mov():
    global enemies, player_position, player_life, alive, player_health
    speed = 0.05
    px, py, pz = player_position
    if alive == True or game_won == False:
        for enemy in enemies[:]:  # Use a copy to safely remove enemies
            ex, ey, _, _ = enemy
            dx, dy = px - ex, py - ey
            distance = math.hypot(dx, dy)  

            if distance < 50:
                player_health -= 1
                print('player health', player_health)
                if player_health == 0:
                    player_life -= 1
                    player_health = 3
                print("remaining life",player_life)
                enemies.remove(enemy)
            elif distance != 0:
                enemy[0] += (dx / distance) * speed
                enemy[1] += (dy / distance) * speed
def check_position_collision(x, y):
    global wall_positions
    min_wall_distance = 10
    for wall in wall_positions:
        wx, wy, ww, wh, _ = wall
        x_dist = max(abs(x - wx) - ww/2, 0)
        y_dist = max(abs(y - wy) - wh/2, 0)
        if x_dist < min_wall_distance and y_dist < min_wall_distance:
            return True
    return False

def collect_coin():
    global player_position, coins, num_coins, level, coins_collected, reached_door, game_won,door_coordinate, player_angle
    min_distance = 50  
    px, py, pz = player_position

    new_coins = []
    for coin in coins:
        cx, cy, cz = coin
        distance = math.sqrt((px - cx)**2 + (py - cy)**2)
        if distance >= min_distance:
            
            new_coins.append(coin)
        else:
            num_coins -= 1
            coins_collected +=1
            print(f"Collected coin at ({cx}, {cy}, {cz})")

    coins[:] = new_coins
    if not coins and reached_door:
        if level<3:
            show_level_transition_screen("New level beginning...")
            level += 1
            reached_door = False  
            print(f"Level up! Welcome to Level {level}")
            print('reached door:',reached_door)
            num_new_coins = 2 
            wall_positions.clear()
            enemies.clear()
            bullets.clear()
            player_position = [-900,900,0]
            player_angle = 90
            generate_coins(num_new_coins)
            door_coordinate = None
        else:
            game_won = True
            show_level_transition_screen("Conratulations!! You Won!!\nPress 'r' to Restart")
            print("game won")
def show_level_transition_screen(message, duration=5):
    fade_duration = 2.0  # Time for fade in and fade out in seconds
    steady_time = duration - 2 * fade_duration
    steps = 60  # Number of frames for fade
    delay = fade_duration / steps

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def draw_text_with_alpha(alpha):
        glClearColor(0,0,.35,1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Setup orthographic projection
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        glColor4f(1, 1, 1, alpha)
        text_x = 370
        text_y = 400
        glRasterPos2f(text_x, text_y)
        for ch in message:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

        glutSwapBuffers()

    # Fade in
    for i in range(steps):
        alpha = i / steps
        draw_text_with_alpha(alpha)
        time.sleep(delay)

    # Steady display
    draw_text_with_alpha(1.0)
    time.sleep(steady_time)

    # Fade out
    for i in range(steps):
        alpha = 1.0 - (i / steps)
        draw_text_with_alpha(alpha)
        time.sleep(delay)

    # Disable blending after done
    glDisable(GL_BLEND)
def collect_power_up_damage():
    global player_position, power_up_damage, dpu_collected, dpu_start_time
    if power_up_damage!= None:
        min_distance = 50
        px, py, pz = player_position
        x, y, z = power_up_damage
        distance = math.sqrt((px - x)**2 + (py - y)**2)
        if distance < min_distance:
            dpu_collected = True
            dpu_start_time = time.time()
            power_up_damage = None
            print("power up collected")

def check_power_up_duration():
    global dpu_collected, dpu_start_time
    if dpu_collected:
        elapsed = time.time() - dpu_start_time
        if elapsed >= 10:
            dpu_collected = False
            print("damage power up expired")

def collect_power_up_health():
    global player_position, power_up_health,  player_life
    if power_up_health!=None:
        min_distance = 50
        px, py, pz = player_position
        x, y, z = power_up_health
        distance = math.sqrt((px - x)**2 + (py - y)**2)
        if distance < min_distance:
            power_up_health = None
            player_life += 1
            print("power up health collected")

def collect_power_up_wall():
    global player_position, power_up_wall, wpu_collected, wpu_start_time
    if power_up_wall!= None:
        min_distance = 50
        px, py, pz = player_position
        x, y, z = power_up_wall
        distance = math.sqrt((px - x)**2 + (py - y)**2)
        if distance < min_distance:
            wpu_collected = True
            wpu_start_time = time.time()
            power_up_wall = None
            print("power up wall collected")

def check_wpu_duration():
    global wpu_collected, wpu_start_time
    if wpu_collected:
        elapsed = time.time() - wpu_start_time
        if elapsed >= 20:
            wpu_collected = False
            print("wall power up expired")

def generate_door_coordinates():
    global door_coordinate
    if door_coordinate==None:
        wall = random.choice(['back', 'left', 'right', 'front'])
        z = 0 

        if wall == 'back':  
            x = random.randint(-700, 700)
            y = -1000
            door_coordinate = [(x, y, z),(x+200,y,0),(x+200,y,200),(x,y,200)]
        elif wall == 'left':  
            x = -1000
            y = random.randint(-700, 700)
            door_coordinate = [(x, y, z),(x,y+200,0),(x,y+200,200),(x,y,200)]
        elif wall == 'right':  
            x = 1000
            y = random.randint(-700, 700)
            door_coordinate = [(x, y, z),(x,y+200,0),(x,y+200,200),(x,y,200)]
        elif wall == 'front':  
            x = random.randint(-700, 700)
            y = 1000
            door_coordinate = [(x, y, z),(x+200,y,0),(x+200,y,200),(x,y,200)]
        

class Bullet:
    
    def __init__(self, position, direction, speed=3.85):
        self.position = list(position)  
        self.direction = direction  
        self.speed = speed
        self.active = True

    def move(self):
        new_x, new_y=self.position[0],self.position[1]
        angle_rad = math.radians(self.direction)
        new_x += self.speed * math.sin(angle_rad)
        new_y -= self.speed * math.cos(angle_rad)
        if not check_position_collision(new_x, new_y):

                if -1000 < new_x < 1000:
                    self.position[0] = new_x
                if -1000 < new_y < 1000:
                    self.position[1] = new_y
        else:
            self.active = False
    def draw(self):
        if not self.active:
            return
        glPushMatrix()
        glColor3f(.7, 0, 0)  
        glTranslatef(*self.position)
        glutSolidSphere(5, 10, 10)
        glPopMatrix()  

def shoot():
    if alive == True or game_won == False:
        global bullets
        start_x = player_position[0]-30
        start_y = player_position[1]-10
        start_z = player_position[2] + 150
        bullets.append(Bullet([start_x, start_y, start_z], player_angle ))

# def collision_wall():
#     global bullets, bullets_miss, enemies, score
#     for ind,bullet in enumerate(bullets):
#         if (bullet.position[0] < -1000 or bullet.position[0] > 1000 or
#         bullet.position[1] < -1000 or bullet.position[1] > 1000):
#             del bullets[ind]
#             bullets_miss +=1
#             print("missed",bullets_miss) 

def collision_enemy():
    global bullets, bullets_miss, enemies, score, dpu_collected

    bullets_to_remove = []
    enemies_to_remove = []

    for bullet in bullets:
        for enemy in enemies:
            dx = enemy[0] - bullet.position[0]
            dy = enemy[1] - bullet.position[1]
            if (dx * dx + dy * dy)**.5 < 50:
                
                bullets_to_remove.append(bullet)
                if dpu_collected == False:
                    enemy[3]-=1
                else:
                    enemy[3] -= 3
                if enemy[3]<=0:
                    score += 1
                    enemies_to_remove.append(enemy)
                print("enemy health", enemy[3])
                break  
    for enemy in enemies_to_remove:
        if enemy in enemies:
            enemies.remove(enemy)

    for bullet in bullets_to_remove:
        if bullet in bullets:
            bullets.remove(bullet)     

def check_alive():
    global player_life, alive
    if player_life<=0:
        alive = False

def check_door_reached():
    global player_position, door_coordinate, reached_door

    if door_coordinate is None:
        return

    # Calculate the center of the door
    door_center_x = sum([v[0] for v in door_coordinate]) / 4
    door_center_y = sum([v[1] for v in door_coordinate]) / 4

    player_x, player_y, _ = player_position
    distance = math.sqrt((player_x - door_center_x)**2 + (player_y - door_center_y)**2)

    if distance < 100:
        if not reached_door:
            print("Player reached the door!")
        reached_door = True
    else:
        if reached_door:
            print("Player left the door area.")
        reached_door = False

def get_direction_to_door(player_pos, door_coords, player_angle):
    
    door_center = door_coords[0]

    dx = door_center[0] - player_pos[0]
    dz = door_center[2] - player_pos[2]

    absolute_angle = math.degrees(math.atan2(dz, dx))

    relative_angle = absolute_angle - player_angle

    relative_angle = (relative_angle + 360) % 360

    return relative_angle

def draw_arrow_to_door(player_pos, door_coords, player_angle):
    angle = get_direction_to_door(player_pos, door_coords, player_angle)

    glPushMatrix()
    # Move arrow to player position
    glTranslatef(player_pos[0], player_pos[1] - 80, player_pos[2])  # Raise above player
    glRotatef(angle, 0, 0, 1)  # Rotate around Y-axis


    glColor3f(1, .9, 1)  # Red arrow
    glBegin(GL_TRIANGLES)
    glVertex3f(0, 40,0)       # tip
    glVertex3f(40, 0, 0)    # base top
    glVertex3f(-40, 0, 0)   # base bottom
    glEnd()
    glBegin(GL_QUADS)
    glVertex3f(25, 0,0)       # tip
    glVertex3f(-25, 0, 0)    # base top
    glVertex3f(-25, -45, 0) 
    glVertex3f(25, -45, 0)  # base bottom
    glEnd()

    glPopMatrix()

def showScreen():
    global wall_positions, door_coordinate
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0,0,.35,1)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1000, 800)  # Set viewport size
    setupCamera()

    

    draw_floor()
    draw_axes_with_labels()
    
    
    draw_maze()
    for enemy_pos in enemies:
           draw_enemy([enemy_pos[0], enemy_pos[1],enemy_pos[2],enemy_pos[3]])
    if door_coordinate != None:
        draw_door(door_coordinate)
    if alive == True or game_won == False:
        draw_coins()

        if power_up_damage!= None:
            draw_power_up()

        if power_up_health!= None:
            draw_power_up_health()

        if power_up_wall!= None:
            draw_power_up_wall()

        
        # if door_coordinate != None:    
        #     draw_arrow_to_door(player_position, door_coordinate, player_angle)
    draw_player()
    for bullet in bullets:
        if (-1000 < bullet.position[0] < 1000 and
            -1000 < bullet.position[1] < 1000):
            bullet.draw()
    if alive == True and game_won == False:
        draw_text(10, 770, f"Enemies killed: {score}    Coins Collected: {coins_collected}")
        draw_text(10, 740, f"Life remaining: {player_life}   Health: {player_health}")
        draw_text(10, 710, f"Level: {level}")
        if dpu_collected == True:
            draw_text(10, 690, f"DAMAGE POWER UP ACTIVATED!!")
        if wpu_collected == True:
            draw_text(670, 740, f"You can WALK THROUGH WALLS!")
    elif alive == True and game_won == True:
        draw_text(10, 770, f"You won!!!")
        draw_text(10, 740, f"Press 'r' to Restart")
    else:
        draw_text(10, 770, f"GAME OVER!!")
        draw_text(10, 740, f"Press 'r' to Restart")
    if cheat_mode == True:
        draw_text(800, 770, f"Cheat Mode ON!")
    

    glutSwapBuffers()


def idle():
    global num_coins, level, wall_positions, enemies, bullets

    generate_walls()
    generate_door_coordinates()
    collect_coin()
    collect_power_up_damage()
    collect_power_up_health()
    collect_power_up_wall()
    spawn_enemy()
    if alive == True:
        enemy_mov()
    check_alive()
    check_power_up_duration()
    check_wpu_duration()
    check_door_reached()

    for bullet in bullets:
        bullet.move()

    collision_enemy()
    #collision_wall()

    
    glutPostRedisplay()
def main():
    global num_coins, level
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(1000, 800)  # Window size
    glutInitWindowPosition(0, 0)  # Window position
    wind = glutCreateWindow(b"3D OpenGL Intro")
    generate_coins(num_coins)
    
    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)  # Register the idle function to move the bullet automatically

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()