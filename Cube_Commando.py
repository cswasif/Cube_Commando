from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import sin, cos, radians
import math
import random

camera_pos = (0, 500, 500)
fovY = 120
GRID_LENGTH = 800  
GRID_WIDTH = 120
rand_var = 423

player_pos = [0, 780, -30]
player_angle = 180

player_life = 10
missed_bullets = 0
game_over = False
death_animation_angle = 0
score = 0

cheat_mode = False
cheat_rotation_speed = 2
cheat_fire_cooldown = 10
cheat_fire_timer = 0

BOUNDARY_WIDTH = GRID_WIDTH  
BOUNDARY_HIGHT = GRID_LENGTH  

enemy_positions = []
new_enemy_positions = []
new_enemy_spawn_timer = 0
NEW_ENEMY_SPAWN_INTERVAL = 500

giant_enemies = []
GIANT_ENEMY_SPAWN_INTERVAL = 1500
giant_enemy_spawn_timer = 0

pickups = []
PICKUP_SPAWN_INTERVAL = 700
pickup_spawn_timer = 0

camera_angle_horizontal = 0.0
camera_height = 500
follow_player = False

pulse_time = 0.0

bullets = []
bullet_speed = 5

spread_shot_cooldown = 0
SPREAD_SHOT_COOLDOWN_MAX = 120

grenades = []
GRENADE_EXPLOSION_RADIUS = 100
GRENADE_DAMAGE = 3

explosions = []
EXPLOSION_DURATION = 30

laser_enemies = []
LASER_ENEMY_SPAWN_INTERVAL = 1200
laser_enemy_spawn_timer = 0
lasers = []
LASER_DURATION = 20
LASER_DAMAGE = 1

kamikaze_enemies = []
KAMIKAZE_SPAWN_INTERVAL = 900
kamikaze_spawn_timer = 0
KAMIKAZE_EXPLOSION_RADIUS = 80
KAMIKAZE_DAMAGE = 2

bridge_cracks = []
MAX_CRACKS = 50

collapse_started = False
collapse_tiles = []
collapse_timer = 0

SPHERE_RADIUS = GRID_WIDTH * 1.2
sphere_markers = [
    {'pos': [0, -GRID_LENGTH +65 - SPHERE_RADIUS, SPHERE_RADIUS//2], 'color': [.8, 1, 0], 'blink_time': 0},
    {'pos': [0, GRID_LENGTH -130+ SPHERE_RADIUS, SPHERE_RADIUS//2], 'color': [1, .8, 0], 'blink_time': 0}
]
BLINK_DURATION = 30

escaped_enemies = 0
MAX_ESCAPED_ENEMIES = 20
game_over_reason = ""

game_started = False
last_score = 0
last_reason = ""
pickup_messages = []
PICKUP_MESSAGE_DURATION = 120

def init_enemies():
    global enemy_positions
    enemy_positions = [spawn_enemy() for _ in range(3)]

def keyboardListener(key, x, y):
    global fovY, player_pos, player_angle, game_over, game_started, game_over_reason, cheat_mode
    if not game_started and key == b' ':
        game_started = True
        glutPostRedisplay()
        return
    
    move_step = 10
    rotate_step = 25

    if key == b'r' and game_over:
        reset_game()
        glutPostRedisplay()
        return

    if game_over:
        return
    
    if not game_started:
        return
    
    if key == b'z':
        fovY = max(10, fovY - 5)
    elif key == b'x':
        fovY = min(170, fovY + 5)
    elif key == b'w':
        new_x = player_pos[0] + move_step * sin(radians(player_angle))
        new_y = player_pos[1] + move_step * cos(radians(player_angle))
        if abs(new_x) > BOUNDARY_WIDTH or abs(new_y) > BOUNDARY_HIGHT:
            if not cheat_mode:
                print("Player fell off the bridge")
                game_over = True
                game_over_reason = "fall"
                return
            else:
                return
        player_pos[0] = new_x
        player_pos[1] = new_y
    elif key == b's':
        new_x = player_pos[0] - move_step * sin(radians(player_angle))
        new_y = player_pos[1] - move_step * cos(radians(player_angle))
        if abs(new_x) > BOUNDARY_WIDTH or abs(new_y) > BOUNDARY_HIGHT:
            if not cheat_mode:
                print("Player fell off the bridge")
                game_over = True
                game_over_reason = "fall"
                return
            else:
                return
        player_pos[0] = new_x
        player_pos[1] = new_y
    elif key == b'a':
        player_angle -= rotate_step
    elif key == b'd':
        player_angle += rotate_step
    elif key == b'c':
        cheat_mode = not cheat_mode
        print("Cheat mode:", "ON" if cheat_mode else "OFF")
    elif key == b'q':
        global spread_shot_cooldown
        if spread_shot_cooldown <= 0:
            fire_spread_shot()
            spread_shot_cooldown = SPREAD_SHOT_COOLDOWN_MAX
            print("Spread Shot fired!")
    elif key == b'g':
        fire_grenade()
        print("Grenade launched!")

    glutPostRedisplay()

def specialKeyListener(key, x, y):
    global camera_angle_horizontal, camera_height, follow_player
    if not game_started or game_over:
        return
    
    if follow_player:
        follow_player = False
        print("Switched to third-person camera view")
    
    if key == GLUT_KEY_LEFT:
        camera_angle_horizontal -= 0.15
    elif key == GLUT_KEY_RIGHT:
        camera_angle_horizontal += 0.15
    elif key == GLUT_KEY_UP:
        camera_height += 30
    elif key == GLUT_KEY_DOWN:
        camera_height -= 30
    glutPostRedisplay()

def mouseListener(button, state, x, y):
    global follow_player
    
    if not game_started or game_over:
        return

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        bx, by, bz = player_pos[0], player_pos[1], player_pos[2] + 75
        bullets.append({'pos': [bx, by, bz], 'angle': player_angle})

    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        follow_player = not follow_player

    glutPostRedisplay()

def spawn_enemy(min_distance=150, is_new_type=False):
    sphere_markers[0]['blink_time'] = BLINK_DURATION
    sphere_markers[0]['color'] = [1, 1, 1]
    
    while True:
        x = random.randint(int(-GRID_WIDTH / 2), int(GRID_WIDTH / 2))
        y = -GRID_LENGTH + 50
        z = 10

        px, py, _ = player_pos
        distance = math.sqrt((x - px)**2 + (y - py)**2)

        if distance >= min_distance:
            if is_new_type:
                return {'pos': [x, y, z], 'health': 5, 'direction': random.choice([-1, 1])}
            else:
                return (x, y, z)

def spawn_giant_enemy():
    sphere_markers[0]['blink_time'] = BLINK_DURATION
    sphere_markers[0]['color'] = [1, 0.5, 0]
    
    x = random.randint(int(-GRID_WIDTH / 2), int(GRID_WIDTH / 2))
    y = -GRID_LENGTH + 50
    z = 10
    
    return {
        'pos': [x, y, z],
        'health': 15,
        'max_health': 15,
        'speed': 0.5
    }

def spawn_pickup():
    x = random.randint(int(-GRID_WIDTH/2), int(GRID_WIDTH/2))
    y = -GRID_LENGTH
    z = 30
    
    pickup_type = random.choice(['health', 'ammo', 'score'])
    speed = random.uniform(0.8, 1.5)
    
    return {'pos': [x, y, z], 'type': pickup_type, 'speed': speed}

def spawn_laser_enemy():
    """Spawn a laser-shooting enemy"""
    sphere_markers[0]['blink_time'] = BLINK_DURATION
    sphere_markers[0]['color'] = [0, 1, 1]
    
    x = random.randint(int(-GRID_WIDTH / 2), int(GRID_WIDTH / 2))
    y = -GRID_LENGTH + 50
    z = 10
    
    return {
        'pos': [x, y, z],
        'health': 3,
        'fire_timer': 0,
        'fire_cooldown': random.randint(60, 120),
        'speed': 0.8
    }

def spawn_kamikaze_enemy():
    """Spawn an exploding kamikaze enemy"""
    sphere_markers[0]['blink_time'] = BLINK_DURATION
    sphere_markers[0]['color'] = [1, 0.5, 0]
    
    x = random.randint(int(-GRID_WIDTH / 2), int(GRID_WIDTH / 2))
    y = -GRID_LENGTH + 50
    z = 10
    
    return {
        'pos': [x, y, z],
        'health': 2,
        'speed': 2.5
    }

def fire_spread_shot():
    """Fire 5 bullets in a spread pattern"""
    angles = [-20, -10, 0, 10, 20]
    bx, by, bz = player_pos[0], player_pos[1], player_pos[2] + 75
    
    for angle_offset in angles:
        bullet_angle = player_angle + angle_offset
        bullets.append({'pos': [bx, by, bz], 'angle': bullet_angle})

def fire_grenade():
    """Launch a grenade that travels in an arc"""
    angle_rad = math.radians(player_angle)
    gx, gy, gz = player_pos[0], player_pos[1], player_pos[2] + 75
    
    speed = 8
    vx = speed * math.sin(angle_rad)
    vy = speed * math.cos(angle_rad)
    vz = 6
    
    grenades.append({
        'pos': [gx, gy, gz],
        'vel': [vx, vy, vz],
        'angle': player_angle
    })

def create_explosion(x, y, z, is_kamikaze=False):
    """Create an explosion at the given position"""
    global bridge_cracks, player_life, game_over, game_over_reason
    
    radius = KAMIKAZE_EXPLOSION_RADIUS if is_kamikaze else GRENADE_EXPLOSION_RADIUS
    
    explosions.append({
        'pos': [x, y, z],
        'radius': radius,
        'time': EXPLOSION_DURATION
    })
    
    if is_kamikaze and not cheat_mode:
        px, py, pz = player_pos
        dist = math.hypot(x - px, y - py)
        if dist < radius:
            player_life -= KAMIKAZE_DAMAGE
            if player_life <= 0:
                game_over = True
                game_over_reason = "life"
    
    if len(bridge_cracks) < MAX_CRACKS:
        bridge_cracks.append({
            'pos': [x, y],
            'size': random.uniform(15, 30),
            'time': 0
        })

def add_bridge_crack(x, y):
    """Add a crack to the bridge at specified position"""
    global bridge_cracks
    if len(bridge_cracks) < MAX_CRACKS:
        bridge_cracks.append({
            'pos': [x, y],
            'size': random.uniform(10, 25),
            'time': 0
        })

def reset_game():
    global player_pos, bullets, player_life, missed_bullets
    global game_over, score, pickup_spawn_timer, new_enemy_positions, pickups
    global escaped_enemies, game_over_reason, giant_enemies, giant_enemy_spawn_timer
    global last_score, last_reason, game_started, pickup_messages
    global grenades, explosions, laser_enemies, laser_enemy_spawn_timer, lasers
    global kamikaze_enemies, kamikaze_spawn_timer, bridge_cracks
    global collapse_started, collapse_tiles, collapse_timer, spread_shot_cooldown
    global death_animation_angle
    
    last_score = score
    last_reason = game_over_reason
    
    player_pos = [0, 780, -30]
    bullets = []
    init_enemies()
    new_enemy_positions = []
    pickups = []
    pickup_messages = []
    player_life = 10
    missed_bullets = 0
    game_over = False
    score = 0
    pickup_spawn_timer = 0
    escaped_enemies = 0
    game_over_reason = ""
    giant_enemies = []
    giant_enemy_spawn_timer = 0
    new_enemy_spawn_timer = 0
    
    grenades = []
    explosions = []
    laser_enemies = []
    laser_enemy_spawn_timer = 0
    lasers = []
    kamikaze_enemies = []
    kamikaze_spawn_timer = 0
    bridge_cracks = []
    collapse_started = False
    collapse_tiles = []
    collapse_timer = 0
    spread_shot_cooldown = 0
    player_angle = 180
    death_animation_angle = 0
    
    global cheat_mode, cheat_fire_timer
    cheat_mode = False
    cheat_fire_timer = 0
    
    game_started = True
    glutPostRedisplay()
    
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_sphere_markers():
    for i, marker in enumerate(sphere_markers):
        if marker['blink_time'] > 0:
            marker['blink_time'] -= 1
            if marker['blink_time'] <= 0:
                marker['color'] = [1, 1, 0]
        
        glPushMatrix()
        glTranslatef(*marker['pos'])
        glColor3f(*marker['color'])
        
        if i == 1:
            glScalef(1.2, 0.1, 1.2)
            glutSolidCube(SPHERE_RADIUS * 1.5)
        else:
            glutSolidSphere(SPHERE_RADIUS, 50, 50)
        
        glPopMatrix()

def draw_player():
    glPushMatrix()
    glTranslatef(*player_pos)

    if game_over:
        fall_angle = min(90, death_animation_angle)
        glRotatef(fall_angle, 1, 0, 0)
        fall_offset = fall_angle / 90.0 * 40
        glTranslatef(0, fall_offset, -fall_offset * 0.5)
    else:
        glRotatef(-player_angle, 0, 0, 1)

    glPushMatrix()
    glColor3f(0.0, 0.8, 0.0)
    glTranslatef(0, 0, 60)
    glScalef(0.6, 0.3, 1.0)
    glutSolidCube(40)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.0, 0.0, 0.0)
    glTranslatef(0, 0, 95)
    glutSolidCube(20)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.9, 0.7, 0.6)
    glTranslatef(13, 10, 75)
    glRotatef(-90, 1, 0, 0)
    glScalef(1.2, 1.2, 5)
    glutSolidCube(5)
    glPopMatrix()
    
    glPushMatrix()
    glColor3f(0.9, 0.7, 0.6)
    glTranslatef(-13, 10, 75)
    glRotatef(-90, 1, 0, 0)
    glScalef(1.2, 1.2, 5)
    glutSolidCube(5)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.75, 0.75, 0.75)
    glTranslatef(0, 25, 75)
    glRotatef(-90, 1, 0, 0)
    glScalef(1.5, 1.5, 8)
    glutSolidCube(5)
    glPopMatrix()

    for dx in [-5, 5]:
        glPushMatrix()
        glColor3f(0.0, 0.0, 1.0)
        glTranslatef(dx, 0, 20)
        gluCylinder(gluNewQuadric(), 2.5, 5, 25, 20, 20)
        glPopMatrix()

    glPopMatrix()

def draw_floor_with_boundaries():
    grid_row = 40
    grid_col = 6
    tile_size = 40
    half_size_col = grid_col * tile_size / 2.0
    half_size_row = grid_row * tile_size / 2.0
    color_r = 1
    color_g = 1
    color_b = 1
    
    for i in range(grid_col):
        for j in range(grid_row):
            color_r -= .0001
            color_g -= .00322
            color_b -= .022
            glColor3f(color_r, color_g, color_b)
            x = i * tile_size - half_size_col
            y = j * tile_size - half_size_row
            
            glBegin(GL_QUADS)
            glVertex3f(x, y, 0)
            glVertex3f(x + tile_size, y, 0)
            glVertex3f(x + tile_size, y + tile_size, 0)
            glVertex3f(x, y + tile_size, 0)
            glEnd()

def draw_enemy(position):
    x, y, z = position
    z = 50  
    scale = 1.0 + 0.2 * math.sin(pulse_time)

    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(scale, scale, scale)

    glColor3f(.5, .5, 1.0)
    gluSphere(gluNewQuadric(), 30, 35, 20)  

    glColor3f(0, 0, 0.501)
    glTranslatef(0, 0, 30)
    gluSphere(gluNewQuadric(), 15, 20, 20)  
    glPopMatrix()

def draw_new_enemy(enemy):
    x, y, z = enemy['pos']
    health = enemy['health']
    pulse = 0.1 * math.sin(pulse_time * 2) if health < 5 else 0
    
    glPushMatrix()
    glTranslatef(x, y, z + 50)
    size_scale = 1.0 + (5 - health) * 0.1 + pulse
    glScalef(size_scale, size_scale, size_scale)
    
    health_color = health / 5.0
    glColor3f(1.0, health_color, health_color)
    gluSphere(gluNewQuadric(), 40, 30, 30) 
   
    glColor3f(0, 0, 0)
    glPushMatrix()
    glTranslatef(15, 15, 30)
    gluSphere(gluNewQuadric(), 8, 10, 10) 
    glTranslatef(-30, 0, 0)
    gluSphere(gluNewQuadric(), 8, 10, 10)
    glPopMatrix()
    glPopMatrix()

def draw_giant_enemy(enemy):
    x, y, z = enemy['pos']
    health_ratio = max(0.1, enemy['health'] / enemy['max_health'])
    
    glPushMatrix()
    glTranslatef(x, y, z + 80)
    
    body_scale = 0.5 + 0.5 * health_ratio
    glPushMatrix()
    glScalef(body_scale, body_scale, body_scale)
    glColor3f(0.7, 0.2, 0.2)
    glutSolidSphere(60, 40, 40)
    glPopMatrix()
    
    glPushMatrix()
    glColor3f(1, 1, 1)
    glTranslatef(20 * body_scale, 20 * body_scale, 40 * body_scale)
    glutSolidSphere(10, 20, 20)
    glTranslatef(-40 * body_scale, 0, 0)
    glutSolidSphere(10, 20, 20)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0, 0, 90 * body_scale)
    glColor3f(0.2/body_scale, 0.2, 0.2)
    glScalef(1.0* body_scale, 0.1 * body_scale, 0.1 * body_scale)
    glutSolidCube(120)
    
    glPushMatrix()
    glTranslatef(-60 * (1 - health_ratio), 0, 0)
    glColor3f(1 - health_ratio, health_ratio, 0)
    glScalef(health_ratio, 1.0, 1.0)
    glutSolidCube(120)
    glPopMatrix()
    
    glPopMatrix()
    
    glPopMatrix()

def draw_pickup(pickup):
    x, y, z = pickup['pos']
    glPushMatrix()
    glTranslatef(x, y, z)
    
    if pickup['type'] == 'health':
        glColor3f(0.0, 1.0, 0.0)
    elif pickup['type'] == 'ammo':
        glColor3f(0.0, 0.0, 1.0)
    else:
        glColor3f(1.0, 0.4, 0.7)
    
    glRotatef(pulse_time * 50, 0, 1, 1)
    glutSolidCube(25)
    glPopMatrix()

def draw_bullet(bullet):
    x, y, z = bullet['pos']
    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(0.3, 0.3, 0.3)
    glColor3f(0.4, 0.2, 0.3)
    glutSolidCube(20)
    glPopMatrix()

def draw_grenade(grenade):
    """Draw a grenade projectile"""
    x, y, z = grenade['pos']
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(0.3, 0.3, 0.3)
    glutSolidCube(15)
    glTranslatef(0, 0, 8)
    glColor3f(1.0, 0.2, 0.0)
    glutSolidCube(8)
    glPopMatrix()

def draw_explosion(explosion):
    """Draw an explosion effect"""
    x, y, z = explosion['pos']
    time_ratio = explosion['time'] / EXPLOSION_DURATION
    current_radius = explosion['radius'] * (1.0 - time_ratio * 0.5)
    
    glPushMatrix()
    glTranslatef(x, y, z + 30)
    
    glColor3f(1.0, 0.4 * time_ratio, 0.0)
    gluSphere(gluNewQuadric(), current_radius * 0.8, 20, 20)
    
    glColor3f(1.0, 1.0, time_ratio)
    gluSphere(gluNewQuadric(), current_radius * 0.4, 15, 15)
    
    glPopMatrix()

def draw_laser_enemy(enemy):
    """Draw a laser-shooting enemy (cyan colored)"""
    x, y, z = enemy['pos']
    pulse = 0.1 * math.sin(pulse_time * 3)
    
    glPushMatrix()
    glTranslatef(x, y, z + 50)
    
    glColor3f(0.0, 0.8 + pulse, 1.0)
    gluSphere(gluNewQuadric(), 35, 30, 30)
    
    glPushMatrix()
    glTranslatef(0, 20, 10)
    glColor3f(1.0, 0.0, 0.0)
    gluSphere(gluNewQuadric(), 10, 15, 15)
    glPopMatrix()
    
    glPushMatrix()
    glColor3f(0.5, 0.5, 0.5)
    glTranslatef(0, 0, 35)
    gluCylinder(gluNewQuadric(), 3, 1, 20, 10, 10)
    glPopMatrix()
    
    glPopMatrix()

def draw_kamikaze_enemy(enemy):
    """Draw an exploding kamikaze enemy (orange pulsing)"""
    x, y, z = enemy['pos']
    pulse = 0.3 * math.sin(pulse_time * 5)
    
    glPushMatrix()
    glTranslatef(x, y, z + 40)
    
    glColor3f(1.0, 0.4 + pulse, 0.0)
    gluSphere(gluNewQuadric(), 30 + pulse * 10, 25, 25)
    
    glPushMatrix()
    glColor3f(0.3, 0.1, 0.0)
    glScalef(1.2, 1.2, 0.3)
    gluSphere(gluNewQuadric(), 25, 20, 20)
    glPopMatrix()
    
    glPushMatrix()
    glTranslatef(0, 0, 30)
    glColor3f(0.2, 0.2, 0.2)
    gluCylinder(gluNewQuadric(), 5, 3, 15, 8, 8)
    glTranslatef(0, 0, 15)
    if int(pulse_time * 10) % 2 == 0:
        glColor3f(1.0, 1.0, 0.0)
    else:
        glColor3f(1.0, 0.5, 0.0)
    gluSphere(gluNewQuadric(), 5, 10, 10)
    glPopMatrix()
    
    glPopMatrix()

def draw_laser(laser):
    """Draw a laser beam"""
    sx, sy, sz = laser['start']
    ex, ey, ez = laser['end']
    
    dx = ex - sx
    dy = ey - sy
    dz = ez - sz
    
    glPushMatrix()
    glTranslatef(sx, sy, sz)
    
    beam_width = 3
    glColor3f(1.0, 0.0, 0.0)
    
    length = math.sqrt(dx*dx + dy*dy + dz*dz)
    
    if length > 0:
        angle = math.degrees(math.atan2(dx, dy))
        glRotatef(angle, 0, 0, 1)
    
    glScalef(beam_width, length, beam_width)
    glTranslatef(0, 0.5, 0)
    glutSolidCube(1)
    
    glPopMatrix()

def draw_bridge_cracks():
    """Draw cracks on the bridge floor"""
    for crack in bridge_cracks:
        x, y = crack['pos']
        size = crack['size']
        
        glPushMatrix()
        glTranslatef(x, y, 1)
        
        glColor3f(0.1, 0.1, 0.1)
        
        glBegin(GL_QUADS)
        glVertex3f(-size/2, -1, 0)
        glVertex3f(size/2, -1, 0)
        glVertex3f(size/2, 1, 0)
        glVertex3f(-size/2, 1, 0)
        glEnd()
        
        glBegin(GL_QUADS)
        glVertex3f(-1, -size/3, 0)
        glVertex3f(-1, size/3, 0)
        glVertex3f(1, size/3, 0)
        glVertex3f(1, -size/3, 0)
        glEnd()
        
        glRotatef(45, 0, 0, 1)
        glBegin(GL_QUADS)
        glVertex3f(-size/4, -0.5, 0)
        glVertex3f(size/4, -0.5, 0)
        glVertex3f(size/4, 0.5, 0)
        glVertex3f(-size/4, 0.5, 0)
        glEnd()
        
        glPopMatrix()

def draw_collapse_animation():
    """Draw bridge collapse animation for game over"""
    global collapse_tiles
    
    for tile in collapse_tiles:
        x, y = tile['pos']
        z = tile.get('z', 0)
        rx, ry, rz = tile['rot']
        
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(rx, 1, 0, 0)
        glRotatef(ry, 0, 1, 0)
        glRotatef(rz, 0, 0, 1)
        
        tile_progress = min(1.0, abs(z) / 500)
        glColor3f(0.5 - tile_progress * 0.3, 0.5 - tile_progress * 0.3, 0.5 - tile_progress * 0.3)
        glScalef(40, 40, 5)
        glutSolidCube(1)
        
        glPopMatrix()

def move_enemy_towards_player():
    global enemy_positions, escaped_enemies, game_over, game_over_reason
    speed = 1
    updated_positions = []
    
    for ex, ey, ez in enemy_positions:
        px, py, _ = player_pos
        dx = px - ex
        dy = py - ey
        distance = math.hypot(dx, dy)

        if distance > 1e-2:
            dx /= distance
            dy /= distance
            ex += dx * speed
            ey += dy * speed

        if ey > GRID_LENGTH - 50:
            sphere_markers[1]['blink_time'] = BLINK_DURATION
            sphere_markers[1]['color'] = [1, 0, 0]
            escaped_enemies += 1
            if escaped_enemies >= MAX_ESCAPED_ENEMIES and not cheat_mode:
                game_over = True
                game_over_reason = "escaped"
            ex, ey, ez = spawn_enemy()
            
        updated_positions.append((ex, ey, ez))
    enemy_positions[:] = updated_positions

def move_new_enemies():
    global new_enemy_positions, score, escaped_enemies, game_over, game_over_reason
    
    speed = 1.5
    
    for enemy in new_enemy_positions[:]:
        enemy['pos'][1] += speed * 0.8
            
        if (abs(enemy['pos'][0]) > BOUNDARY_WIDTH or abs(enemy['pos'][1]) > BOUNDARY_HIGHT):
            new_enemy_positions.remove(enemy)
            score += 100
        elif enemy['pos'][1] > GRID_LENGTH - 50:
            sphere_markers[1]['blink_time'] = BLINK_DURATION
            sphere_markers[1]['color'] = [1, 0, 0]
            new_enemy_positions.remove(enemy)
            escaped_enemies += 1
            if escaped_enemies >= MAX_ESCAPED_ENEMIES and not cheat_mode:
                game_over = True
                game_over_reason = "escaped"

def move_giant_enemies():
    global giant_enemies, score, escaped_enemies, game_over, game_over_reason
    
    for enemy in giant_enemies[:]:
        enemy['pos'][1] += enemy['speed']
        
        if enemy['pos'][1] > GRID_LENGTH - 50:
            sphere_markers[1]['blink_time'] = BLINK_DURATION
            sphere_markers[1]['color'] = [1, 0, 0]
            giant_enemies.remove(enemy)
            escaped_enemies += 1
            if escaped_enemies >= MAX_ESCAPED_ENEMIES and not cheat_mode:
                game_over = True
                game_over_reason = "escaped"

def move_pickups():
    global pickups
    for pickup in pickups[:]:
        pickup['pos'][1] += pickup['speed']
            
        if abs(pickup['pos'][1]) > BOUNDARY_HIGHT:
            pickups.remove(pickup)

def move_laser_enemies():
    """Move laser enemies and handle their firing"""
    global laser_enemies, lasers, player_life, game_over, game_over_reason, escaped_enemies
    
    px, py, pz = player_pos
    
    for enemy in laser_enemies[:]:
        ex, ey, ez = enemy['pos']
        
        dx = px - ex
        dy = py - ey
        distance = math.hypot(dx, dy)
        
        if distance > 200:
            if distance > 1e-2:
                dx /= distance
                dy /= distance
                enemy['pos'][0] += dx * enemy['speed']
                enemy['pos'][1] += dy * enemy['speed']
        
        ex, ey, ez = enemy['pos']
        
        enemy['fire_timer'] += 1
        if enemy['fire_timer'] >= enemy['fire_cooldown']:
            enemy['fire_timer'] = 0
            lasers.append({
                'start': [ex, ey, ez + 60],
                'end': [px, py, pz + 60],
                'time': LASER_DURATION
            })
        
        if ey > GRID_LENGTH - 50:
            sphere_markers[1]['blink_time'] = BLINK_DURATION
            sphere_markers[1]['color'] = [1, 0, 0]
            laser_enemies.remove(enemy)
            escaped_enemies += 1
            if escaped_enemies >= MAX_ESCAPED_ENEMIES and not cheat_mode:
                game_over = True
                game_over_reason = "escaped"

def move_kamikaze_enemies():
    """Move kamikaze enemies toward player"""
    global kamikaze_enemies, player_life, game_over, game_over_reason, escaped_enemies
    
    px, py, pz = player_pos
    
    for enemy in kamikaze_enemies[:]:
        ex, ey, ez = enemy['pos']
        
        dx = px - ex
        dy = py - ey
        distance = math.hypot(dx, dy)
        
        if distance > 1e-2:
            dx /= distance
            dy /= distance
            enemy['pos'][0] += dx * enemy['speed']
            enemy['pos'][1] += dy * enemy['speed']
        
        if distance < 60:
            create_explosion(ex, ey, ez, is_kamikaze=True)
            if not cheat_mode:
                player_life -= KAMIKAZE_DAMAGE
                if player_life <= 0:
                    game_over = True
                    game_over_reason = "life"
            kamikaze_enemies.remove(enemy)
            continue
        
        if ey > GRID_LENGTH - 50:
            sphere_markers[1]['blink_time'] = BLINK_DURATION
            sphere_markers[1]['color'] = [1, 0, 0]
            kamikaze_enemies.remove(enemy)
            escaped_enemies += 1
            if escaped_enemies >= MAX_ESCAPED_ENEMIES and not cheat_mode:
                game_over = True
                game_over_reason = "escaped"

def update_grenades():
    """Update grenade positions with arc trajectory"""
    global grenades
    gravity = 0.2
    
    for grenade in grenades[:]:
        grenade['pos'][0] += grenade['vel'][0]
        grenade['pos'][1] += grenade['vel'][1]
        grenade['pos'][2] += grenade['vel'][2]
        
        grenade['vel'][2] -= gravity
        
        if grenade['pos'][2] <= 0 or abs(grenade['pos'][0]) > GRID_WIDTH or abs(grenade['pos'][1]) > GRID_LENGTH:
            gx, gy, gz = grenade['pos']
            create_explosion(gx, gy, 0, is_kamikaze=False)
            grenade_explosion_damage(gx, gy)
            grenades.remove(grenade)

def grenade_explosion_damage(gx, gy):
    """Apply damage to all enemies within grenade explosion radius"""
    global enemy_positions, new_enemy_positions, giant_enemies, laser_enemies, kamikaze_enemies, score
    
    for i in range(len(enemy_positions) - 1, -1, -1):
        ex, ey, ez = enemy_positions[i]
        dist = math.hypot(gx - ex, gy - ey)
        if dist < GRENADE_EXPLOSION_RADIUS:
            enemy_positions[i] = spawn_enemy()
            score += 3
    
    for enemy in new_enemy_positions[:]:
        ex, ey, ez = enemy['pos']
        dist = math.hypot(gx - ex, gy - ey)
        if dist < GRENADE_EXPLOSION_RADIUS:
            enemy['health'] -= GRENADE_DAMAGE
            if enemy['health'] <= 0:
                new_enemy_positions.remove(enemy)
                score += 10
    
    for enemy in giant_enemies[:]:
        ex, ey, ez = enemy['pos']
        dist = math.hypot(gx - ex, gy - ey)
        if dist < GRENADE_EXPLOSION_RADIUS:
            enemy['health'] -= GRENADE_DAMAGE * 2
            if enemy['health'] <= 0:
                giant_enemies.remove(enemy)
                score += 20
    
    for enemy in laser_enemies[:]:
        ex, ey, ez = enemy['pos']
        dist = math.hypot(gx - ex, gy - ey)
        if dist < GRENADE_EXPLOSION_RADIUS:
            enemy['health'] -= GRENADE_DAMAGE
            if enemy['health'] <= 0:
                laser_enemies.remove(enemy)
                score += 8
    
    for enemy in kamikaze_enemies[:]:
        ex, ey, ez = enemy['pos']
        dist = math.hypot(gx - ex, gy - ey)
        if dist < GRENADE_EXPLOSION_RADIUS:
            create_explosion(ex, ey, ez, is_kamikaze=True)
            kamikaze_enemies.remove(enemy)
            score += 5

def update_explosions():
    """Update explosion timers"""
    global explosions
    for explosion in explosions[:]:
        explosion['time'] -= 1
        if explosion['time'] <= 0:
            explosions.remove(explosion)

def update_lasers():
    """Update laser beam timers and check player damage"""
    global lasers, player_life, game_over, game_over_reason
    
    px, py, pz = player_pos
    
    for laser in lasers[:]:
        if laser['time'] == LASER_DURATION:
            sx, sy, sz = laser['start']
            ex, ey, ez = laser['end']
            
            line_dx = ex - sx
            line_dy = ey - sy
            line_len = math.hypot(line_dx, line_dy)
            
            if line_len > 0:
                t = max(0, min(1, ((px - sx) * line_dx + (py - sy) * line_dy) / (line_len * line_len)))
                closest_x = sx + t * line_dx
                closest_y = sy + t * line_dy
                
                dist = math.hypot(px - closest_x, py - closest_y)
                
                if dist < 40:
                    if not cheat_mode:
                        player_life -= LASER_DAMAGE
                    if player_life <= 0 and not cheat_mode:
                        game_over = True
                        game_over_reason = "life"
        
        laser['time'] -= 1
        if laser['time'] <= 0:
            lasers.remove(laser)

def init_collapse_animation():
    """Initialize bridge collapse animation tiles"""
    global collapse_tiles, collapse_started
    
    collapse_started = True
    grid_row = 40
    grid_col = 6
    tile_size = 40
    half_size_col = grid_col * tile_size / 2.0
    half_size_row = grid_row * tile_size / 2.0
    
    for i in range(grid_col):
        for j in range(grid_row):
            x = i * tile_size - half_size_col + tile_size / 2
            y = j * tile_size - half_size_row + tile_size / 2
            
            delay = (grid_row - j) * 3
            
            collapse_tiles.append({
                'pos': [x, y],
                'z': 0,
                'vel_z': 0,
                'rot': [0, 0, 0],
                'rot_vel': [random.uniform(-5, 5), random.uniform(-5, 5), random.uniform(-5, 5)],
                'delay': delay,
                'falling': False
            })

def update_collapse_animation():
    """Update the bridge collapse animation"""
    global collapse_tiles, collapse_timer
    
    collapse_timer += 1
    
    for tile in collapse_tiles:
        if not tile['falling']:
            if collapse_timer >= tile['delay']:
                tile['falling'] = True
        else:
            tile['vel_z'] -= 0.5
            tile['z'] += tile['vel_z']
            
            tile['rot'][0] += tile['rot_vel'][0]
            tile['rot'][1] += tile['rot_vel'][1]
            tile['rot'][2] += tile['rot_vel'][2]

def check_collisions():
    global bullets, enemy_positions, player_life, game_over, score
    global new_enemy_positions, missed_bullets, pickups, giant_enemies, game_over_reason

    bullet_radius = 10
    enemy_radius = 20
    player_radius = 30
    
    px, py, pz = player_pos
    
    for bullet in bullets[:]:
        bx, by, bz = bullet['pos']
        bullet_hit = False
        
        for i in range(len(enemy_positions)):
            ex, ey, ez = enemy_positions[i]
            dist = math.sqrt((bx - ex)**2 + (by - ey)**2 + (bz - ez)**2)
            if dist < bullet_radius + enemy_radius + 20:
                bullet_hit = True
                enemy_positions[i] = spawn_enemy()
                score += 1
                bullets.remove(bullet)
                break
                
        if bullet_hit:
            continue
                
        for enemy in new_enemy_positions[:]:
            ex, ey, ez = enemy['pos']
            dist = math.sqrt((bx - ex)**2 + (by - ey)**2 + (bz - (ez))**2)
            
            if dist < 50:
                bullet_hit = True
                enemy['health'] -= 1
                score += 1
                
                angle = math.atan2(by - ey, bx - ex)
                knockback = 100
                enemy['pos'][0] -= knockback * math.cos(angle)
                enemy['pos'][1] -= knockback * math.sin(angle)
                
                if (abs(enemy['pos'][0]) > BOUNDARY_WIDTH or 
                    abs(enemy['pos'][1]) > BOUNDARY_HIGHT):
                    new_enemy_positions.remove(enemy)
                    score += 10
                elif enemy['health'] <= 0:
                    new_enemy_positions.remove(enemy)
                    score += 10
                bullets.remove(bullet)
                break
                
        if bullet_hit:
            continue
            
        for enemy in giant_enemies[:]:
            ex, ey, ez = enemy['pos']
            dist = math.sqrt((bx - ex)**2 + (by - ey)**2 + (bz - (ez))**2)
            
            if dist < 70:
                bullet_hit = True
                enemy['health'] -= 3
                score += 1
                
                if enemy['health'] <= 0:
                    giant_enemies.remove(enemy)
                    score += 15
                
                bullets.remove(bullet)
                break
                
        if bullet_hit:
            continue

        for enemy in laser_enemies[:]:
            ex, ey, ez = enemy['pos']
            dist = math.sqrt((bx - ex)**2 + (by - ey)**2 + (bz - ez)**2)
            
            if dist < 55:
                bullet_hit = True
                enemy['health'] -= 1
                score += 2
                
                if enemy['health'] <= 0:
                    laser_enemies.remove(enemy)
                    score += 8
                
                bullets.remove(bullet)
                break
                
        if bullet_hit:
            continue
            
        for enemy in kamikaze_enemies[:]:
            ex, ey, ez = enemy['pos']
            dist = math.sqrt((bx - ex)**2 + (by - ey)**2 + (bz - ez)**2)
            
            if dist < 50:
                bullet_hit = True
                enemy['health'] -= 1
                score += 1
                
                if enemy['health'] <= 0:
                    create_explosion(ex, ey, ez, is_kamikaze=True)
                    kamikaze_enemies.remove(enemy)
                    score += 5
                
                bullets.remove(bullet)
                break
                
        if bullet_hit:
            continue

    for i in range(len(enemy_positions)):
        ex, ey, ez = enemy_positions[i]
        dist = math.sqrt((px - ex)**2 + (py - ey)**2 + (pz - ez)**2)
        if dist < player_radius + enemy_radius:
            if not cheat_mode:
                player_life -= 1
            enemy_positions[i] = spawn_enemy()
            if player_life <= 0 and not cheat_mode:
                game_over = True
                game_over_reason = "life"
    
    for enemy in new_enemy_positions[:]:
        ex, ey, ez = enemy['pos']
        dist = math.sqrt((px - ex)**2 + (py - ey)**2 + (pz - (ez))**2)
        
        if dist < player_radius + 40:
            if not cheat_mode:
                player_life -= 2
            enemy['health'] -= 1
            
            angle = math.atan2(py - ey, px - ex)
            knockback = 100
            enemy['pos'][0] -= knockback * math.cos(angle)
            enemy['pos'][1] -= knockback * math.sin(angle)
            
            if (abs(enemy['pos'][0]) > BOUNDARY_WIDTH or 
                abs(enemy['pos'][1]) > BOUNDARY_HIGHT):
                new_enemy_positions.remove(enemy)
            elif enemy['health'] <= 0:
                new_enemy_positions.remove(enemy)
            
            if player_life <= 0 and not cheat_mode:
                game_over = True
                game_over_reason = "life"
    
    for enemy in giant_enemies[:]:
        ex, ey, ez = enemy['pos']
        dist = math.sqrt((px - ex)**2 + (py - ey)**2 + (pz - (ez))**2)
        
        if dist < player_radius + 60:
            if not cheat_mode:
                player_life -= 3
            if player_life <= 0 and not cheat_mode:
                game_over = True
                game_over_reason = "life"

    player_collision_height = pz + 50
    
    for pickup in pickups[:]:
        pickup_x, pickup_y, pickup_z = pickup['pos']
        
        dx = px - pickup_x
        dy = py - pickup_y
        dz = player_collision_height - pickup_z
        
        distance_sq = dx*dx + dy*dy + dz*dz
        collision_distance_sq = (player_radius + 15)**2
        
        if distance_sq < collision_distance_sq:
            if pickup['type'] == 'health':
                player_life = min(10, player_life + 5)
                pickup_messages.append({'text': "Health +5!", 'time': PICKUP_MESSAGE_DURATION})
            elif pickup['type'] == 'ammo':
                missed_bullets = max(0, missed_bullets - 5)
                pickup_messages.append({'text': "Ammo +5!", 'time': PICKUP_MESSAGE_DURATION})
            else:
                score += 30
                pickup_messages.append({'text': "Score +30!", 'time': PICKUP_MESSAGE_DURATION})
            
            pickups.remove(pickup)

def rotate_gun_cheat_mode():
    global player_angle
    player_angle = (player_angle + cheat_rotation_speed) % 360

def will_bullet_hit(px, py, dir_x, dir_y, ex, ey, hit_radius=15):
    vx = ex - px
    vy = ey - py
    dot = vx * dir_x + vy * dir_y

    if dot < 0:
        return False

    closest_x = px + dot * dir_x
    closest_y = py + dot * dir_y
    dist_sq = (closest_x - ex) ** 2 + (closest_y - ey) ** 2

    return dist_sq <= hit_radius ** 2

def auto_aim_and_fire():
    px, py, pz = player_pos
    angle_rad = radians(player_angle)
    dir_x = math.sin(angle_rad)
    dir_y = math.cos(angle_rad)

    for ex, ey, ez in enemy_positions:
        if will_bullet_hit(px, py, dir_x, dir_y, ex, ey):
            fire_cheat_bullet()
            return True
    return False

def fire_cheat_bullet():
    bx, by, bz = player_pos[0], player_pos[1], player_pos[2] + 75
    bullets.append({'pos': [bx, by, bz], 'angle': player_angle})

def update_bullets():
    global bullets, missed_bullets
    new_bullets = []
    for bullet in bullets:
        angle_rad = math.radians(bullet['angle'])
        bullet['pos'][0] += bullet_speed * math.sin(angle_rad)
        bullet['pos'][1] += bullet_speed * math.cos(angle_rad)

        if abs(bullet['pos'][0]) < GRID_WIDTH and abs(bullet['pos'][1]) < GRID_LENGTH:
            new_bullets.append(bullet)
        else:
            missed_bullets += 1
    bullets = new_bullets

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    look()

def look():
    if follow_player:
        px, py, pz = player_pos
        angle_rad = radians(player_angle)
        eye_x = px + 15* sin(angle_rad)
        eye_y = py + 15 * cos(angle_rad)
        eye_z = pz + 85
        center_x = px + 100 * sin(angle_rad)
        center_y = py + 100 * cos(angle_rad)
        center_z = pz + 75
    else:
        radius = 800
        eye_x = radius * sin(camera_angle_horizontal)
        eye_y = radius * cos(camera_angle_horizontal)
        eye_z = camera_height
        center_x = 0
        center_y = 0
        center_z = 0

    gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, 0, 0, 1)

def idle():
    global pulse_time, game_over, cheat_fire_timer
    global new_enemy_spawn_timer, pickup_spawn_timer, score, giant_enemy_spawn_timer, game_over_reason
    global laser_enemy_spawn_timer, kamikaze_spawn_timer, spread_shot_cooldown
    global collapse_started

    if not game_started:
        glutPostRedisplay()
        return

    if game_over:
        global death_animation_angle
        if death_animation_angle < 90:
            death_animation_angle += 3
        
        if game_over_reason == "escaped" and not collapse_started:
            init_collapse_animation()
        if collapse_started:
            update_collapse_animation()
        glutPostRedisplay()
        return

    pulse_time += 0.05
    
    if spread_shot_cooldown > 0:
        spread_shot_cooldown -= 1
    
    move_enemy_towards_player()
    
    if not game_over:
        new_enemy_spawn_timer += 1
        if new_enemy_spawn_timer >= NEW_ENEMY_SPAWN_INTERVAL:
            new_enemy_positions.append(spawn_enemy(is_new_type=True))
            new_enemy_spawn_timer = 0
        
        giant_enemy_spawn_timer += 1
        if giant_enemy_spawn_timer >= GIANT_ENEMY_SPAWN_INTERVAL:
            giant_enemies.append(spawn_giant_enemy())
            giant_enemy_spawn_timer = 0
        
        laser_enemy_spawn_timer += 1
        if laser_enemy_spawn_timer >= LASER_ENEMY_SPAWN_INTERVAL:
            laser_enemies.append(spawn_laser_enemy())
            laser_enemy_spawn_timer = 0
        
        kamikaze_spawn_timer += 1
        if kamikaze_spawn_timer >= KAMIKAZE_SPAWN_INTERVAL:
            kamikaze_enemies.append(spawn_kamikaze_enemy())
            kamikaze_spawn_timer = 0
        
        move_new_enemies()
        move_giant_enemies()
        move_laser_enemies()
        move_kamikaze_enemies()

        pickup_spawn_timer += 1
        if pickup_spawn_timer >= PICKUP_SPAWN_INTERVAL:
            pickups.append(spawn_pickup())
            pickup_spawn_timer = 0
        move_pickups()
    
    update_grenades()
    update_explosions()
    update_lasers()

    if cheat_mode:
        rotate_gun_cheat_mode()
        cheat_fire_timer += 1
        if cheat_fire_timer >= cheat_fire_cooldown:
            if auto_aim_and_fire():
                cheat_fire_timer = 0

    update_bullets()
    check_collisions()

    if not cheat_mode:
        if player_life <= 0:
            game_over = True
            game_over_reason = "life"
        elif missed_bullets >= 10:
            game_over = True
            game_over_reason = "bullets"
    glutPostRedisplay()

def draw_start_screen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glColor3f(1, 1, 1)
    
    glRasterPos2f(300, 650)
    for char in "CUBE COMMANDO: ALONE WARRIOR":
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))
    
    story_lines = [
        "In a world dominated by evil circles,",
        "you are the last square warrior standing from the Square World.",
        "",
        "Defend your bridge from the invading circles !",
        "",
        "Press SPACE to begin your defense!"
    ]
    
    y_pos = 550
    for line in story_lines:
        glRasterPos2f(350, y_pos)
        for char in line:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        y_pos -= 30
        
    glColor3f(0.1, 0.1, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(1000, 0)
    glVertex2f(1000, 800)
    glVertex2f(0, 800)
    glEnd()
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glutSwapBuffers()

def draw_pickup_notifications():
    if not pickup_messages:
        return
        
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    x_pos = 700
    y_pos = 700
    
    for i, message in enumerate(pickup_messages[:]):
        alpha = min(1.0, message['time'] / (PICKUP_MESSAGE_DURATION/2))
        glColor4f(1, 1, 1, alpha)
        
        draw_text(x_pos, y_pos - i*30, message['text'], GLUT_BITMAP_HELVETICA_12)
        
        message['time'] -= 1
        if message['time'] <= 0:
            pickup_messages.remove(message)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def showScreen():
    global game_started, game_over, game_over_reason
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    if not game_started:
        draw_start_screen()
        return

    glViewport(0, 0, 1000, 800)
    setupCamera()
    
    cooldown_status = "READY" if spread_shot_cooldown <= 0 else f"{spread_shot_cooldown//60 + 1}s"
    draw_text(10, 770, f"Score: {score}  Life: {player_life}  Missed: {missed_bullets}  Escaped: {escaped_enemies}/{MAX_ESCAPED_ENEMIES}")
    draw_text(10, 740, f"Spread Shot[Q]: {cooldown_status}  Grenade[G]: Ready")
    
    draw_bridge_cracks()
    
    draw_floor_with_boundaries()
    
    if collapse_started:
        draw_collapse_animation()
    
    draw_player()
    draw_sphere_markers()

    for enemy in enemy_positions:
        draw_enemy(enemy)
        
    for enemy in new_enemy_positions:
        draw_new_enemy(enemy)
          
    for enemy in giant_enemies:
        draw_giant_enemy(enemy)
    
    for enemy in laser_enemies:
        draw_laser_enemy(enemy)
        
    for enemy in kamikaze_enemies:
        draw_kamikaze_enemy(enemy)
        
    for pickup in pickups:
        draw_pickup(pickup)
        
    for bullet in bullets:
        draw_bullet(bullet)
    
    for grenade in grenades:
        draw_grenade(grenade)
    
    for explosion in explosions:
        draw_explosion(explosion)
    
    for laser in lasers:
        draw_laser(laser)

    draw_pickup_notifications()

    if game_over:
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        m = ""
        if game_over_reason == "escaped":
            glColor3f(1, 0.2, 0.2)
            draw_text(250, 600, "The Square world is destroyed by the circles!", GLUT_BITMAP_TIMES_ROMAN_24)
            m = "The Square world is destroyed by the circles!"
        elif game_over_reason == "life":
            glColor3f(1, 0.2, 0.2)
            draw_text(350, 600, "Game Over! You were defeated!", GLUT_BITMAP_TIMES_ROMAN_24)
            m = "Game Over! You were defeated!"
        elif game_over_reason == "bullets":
            glColor3f(1, 0.2, 0.2)
            draw_text(350, 600, "Game Over! You ran out of ammo!", GLUT_BITMAP_TIMES_ROMAN_24)
            m = "Game Over! You ran out of ammo!"
        elif game_over_reason == "fall":
            glColor3f(1, 0.2, 0.2)
            draw_text(350, 600, "Game Over! You have fallen off the Bridge!", GLUT_BITMAP_TIMES_ROMAN_24)
            m = "Game Over! You have fallen off the Bridge!"
        
        glColor3f(1, 1, 1)
        draw_text(350, 450, f"Final Score: {score}", GLUT_BITMAP_HELVETICA_18)
        draw_text(350, 420, f"Reason: {m}", GLUT_BITMAP_HELVETICA_18)
        
        draw_text(400, 350, "Press 'R' to restart", GLUT_BITMAP_HELVETICA_18)
        glColor4f(0.1, 0.2, 0, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(200, 250)
        glVertex2f(800, 250)
        glVertex2f(800, 550)
        glVertex2f(200, 550)
        glEnd()
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
    glutSwapBuffers()

def init():
    glClearColor(0, 0, 0, 1)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_MODELVIEW)
    init_enemies()

if __name__ == "__main__":
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutCreateWindow(b"Cube Commando - Alone Warrior")
    init()
    glutDisplayFunc(showScreen)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutMainLoop()