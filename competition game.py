# Nathan Gorman
# 13 June 2025 (edit because I forgot header)
# Mini game contest
# Use left and right arrow keys to move and space bar or up arrow to jump

import sys, random
from pygame import *
import math

scale: int

class Entity:
    def draw(self, screen: Surface):
        pass

    def tick(self, scroll_speed, size):
        pass

class Scroller(Entity):
    images: list[Surface]
    speed: float
    list: list[Entity]

    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.img = self.images[size]
        self.list.append(self)

    def draw(self, screen: Surface):
        screen.blit(self.img, (self.x, self.y, self.img.width, self.img.height))

    def tick(self, scroll_speed, size) -> bool:
        self.x += scroll_speed + self.speed
        return self.x > -self.img.width

Cloud = type("Cloud", (Scroller,), {"speed": -0.5, "list": []})
Bush = type("Bush", (Scroller,), {"speed": 0, "list": []})

class Goomba(Entity):
    images: list[Surface]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.squished = False
        self.squished_time = 0
        self.dead = False

    def tick(self, scroll_speed, size):
        self.frame += 1
        self.x += scroll_speed - 0.5*scale
        img = Goomba.images[((self.frame // 8) % 2)]
        if self.squished:
            self.squished_time += 1
        if self.squished_time >= 2:
            self.dead = True
        return self.x > -img.get_width() and not self.dead

    def draw(self, screen: Surface):
        img = Goomba.images[((self.frame//8)%2)] if not self.squished else Goomba.images[2]
        screen.blit(img, (self.x, self.y, img.get_width(), img.get_height()))

class Spawner:
    def __init__(self, range, units_per):
        self.range = range
        self.units_per = units_per
        self.units_per_this = units_per + random.randint(int(-units_per/range), int(units_per/range))
        self.units_since = 0

    def spawn(self, units_advanced) -> bool:
        self.units_since += abs(units_advanced)
        spawn = self.units_since >= self.units_per_this

        if spawn:
            self.units_since -= self.units_per_this
            self.units_per_this = self.units_per + random.randint(int(-self.units_per/self.range), int(self.units_per/self.range))

        return spawn

def load_scaled_image(name: str): #, scale: int):
    result = image.load(name)
    return transform.scale(result, (result.get_width()*scale, result.get_height()*scale))

def load_scaled_flipped_image(name: str): #, scale: int):
    result = load_scaled_image(name)
    return result, transform.flip(result, True, False)


def add_non_colliding_position(class_type: type, size, entities: list[Entity], x_pos: int = None, y_pos: int = None, x_start = 0, x_end = None, y_start = 0, y_end = None):
    img = random.randint(0, 1)

    x_end = size[0] - class_type.images[img].width if x_end is None else x_end
    y_end = size[1] - class_type.images[img].height - (scale*128) if y_end is None else y_end

    x = random.randint(x_start, x_end)//4 * 4 if x_pos is None else x_pos
    y = random.randint(y_start, y_end) if y_pos is None else y_pos
    collision = True

    i = 0
    while collision:
        for scrollable in class_type.list:
            if Rect(x, y, class_type.images[img].width, class_type.images[img].height).colliderect((scrollable.x, scrollable.y, scrollable.img.width, scrollable.img.height)):
                collision = True
                if x_pos is None: x = random.randint(0, size[0] - class_type.images[img].width)//4 * 4
                if y_pos is None: y = random.randint(0, size[1] - class_type.images[img].height - (scale*128))//4 * 4
                break
        else:
            collision = False

        i += 1

        if i > 10: return

    entities.append(class_type(x, y, img))

def init_scrollable(class_type: type, size, scroll_speed, entities, starting_amount, x_pos = None, y_pos = None):
    for i in range(starting_amount):
        add_non_colliding_position(class_type, size, entities, x_pos, y_pos)

    return size[0]/((scroll_speed + class_type.speed)*-starting_amount)

def main():
    global scale

    # Initiate pygame
    init()

    font_name = font.get_default_font()

    # Timing
    timer = time.Clock()
    fps = 60

    # Set up display
    desktop_size = display.get_desktop_sizes()[0]

    height = int(desktop_size[0] * (9/16))
    if height < desktop_size[1]:
        size = (desktop_size[0], height)
    else:
        size = (int(desktop_size[1] * 16/9), desktop_size[1])

    # Some weird bugs that I'm too lazy to debug happen when scale is not even
    scale = size[0]//480
    #scale = 4
    Cloud.speed = -0.125 * scale

    if size == desktop_size:
        screen = display.set_mode(size, FULLSCREEN)
    else:
        screen = display.set_mode(size)

    display.set_caption("Game")

    score_font = font.Font(font_name, scale*8)

    mario_image_right, mario_image_left = load_scaled_flipped_image("mario.png")

    mario_image_r1_right, mario_image_r1_left = load_scaled_flipped_image("mario_r1.png")
    mario_image_r2_right, mario_image_r2_left = load_scaled_flipped_image("mario_r2.png")
    mario_image_r3_right, mario_image_r3_left = load_scaled_flipped_image("mario_r3.png")

    mario_image_j_right, mario_image_j_left = load_scaled_flipped_image("mario_j.png")
    mario_image_t_right, mario_image_t_left = load_scaled_flipped_image("mario_t.png")

    floor_brick = load_scaled_image("floor_brick.png")

    cloud_1 = load_scaled_image("cloud_1.png")
    cloud_2 = load_scaled_image("cloud_2.png")
    Cloud.images = [cloud_1, cloud_2]

    bush_1 = load_scaled_image("bush_1.png")
    bush_2 = load_scaled_image("bush_2.png")
    Bush.images = [bush_1, bush_2]

    goomba_1 = load_scaled_image("goomba_1.png")
    goomba_2 = load_scaled_image("goomba_2.png")
    goomba_3 = load_scaled_image("goomba_3.png")
    Goomba.images = [goomba_1, goomba_2, goomba_3]

    # Player vars
    player_width = mario_image_right.get_width()
    player_height = mario_image_right.get_height()
    player_x = 96*scale
    player_y = size[1] - (32*scale) - player_height
    player_vx = 0
    player_vy = 0
    player_jump_strength = -(4*scale)
    player_on_ground = False
    gravity = 0.25*scale
    ground_height = size[1]-(48*scale)
    player_x_speed = 1.5*scale
    player_x_dir = 0
    left = False
    right = False
    player_facing_right = True
    to_jump = False
    mario_running_anim_left = [mario_image_r1_left, mario_image_r2_left, mario_image_r3_left, mario_image_r2_left]
    mario_running_anim_right = [mario_image_r1_right, mario_image_r2_right, mario_image_r3_right, mario_image_r2_right]
    player_running_frame = 0
    player_x_acceleration = 0.125*scale

    scroll_speed = -0.25 * scale
    entities: list[Entity] = []
    frame = 0

    cloud_spawner = Spawner(2, init_scrollable(Cloud, size, scroll_speed, entities, 5))
    bush_spawner = Spawner(2, init_scrollable(Bush, size, scroll_speed, entities, 2, y_pos = size[1]-(64*scale)))
    goomba_spawner = Spawner(2, 64*scale)

    squished = 0
    units = 0
    floor_sub = 0

    while True:
        # fill background
        screen.fill((125, 175, 255))

        # Check events for exit
        for ev in event.get():
            if ev.type == QUIT:
                quit_g()

            elif ev.type == KEYDOWN:
                if ev.key == K_ESCAPE:
                    quit_g()

                elif ev.key == K_SPACE or ev.key == K_UP:
                    to_jump = True

                elif ev.key == K_LEFT:
                    left = True
                    player_x_dir = -1
                    player_facing_right = False

                elif ev.key == K_RIGHT:
                    right = True
                    player_x_dir = 1
                    player_facing_right = True

            elif ev.type == KEYUP:
                if ev.key == K_LEFT:
                    left = False

                    if right:
                        player_x_dir = 1
                        player_facing_right = True
                    else:
                        player_x_dir = 0

                elif ev.key == K_RIGHT:
                    right = False

                    if left:
                        player_x_dir = -1
                        player_facing_right = False
                    else:
                        player_x_dir = 0

                elif ev.key == K_SPACE or ev.key == K_UP:
                    to_jump = False


        """ Player Update """
        scroll_speed = (((size[0] - player_width - (192*scale)) - player_x) // (32*scale))/(4/scale) if player_x > size[0] - player_width - (192*scale) else -0.25*scale
        units += scroll_speed

        player_running = left or right

        if player_running and not frame % 6:
            player_running_frame += 1 if player_running_frame < 3 else -3

        player_was_on_ground = player_on_ground
        player_on_ground = player_y >= ground_height

        if to_jump and player_on_ground:
            player_vy = player_jump_strength

        if player_on_ground and not player_was_on_ground:
            player_vy = 0
            player_y = ground_height

        if not player_on_ground:
            player_vy += gravity

        if player_x_dir != 0:
            if (player_x_dir == -1 and player_vx > -player_x_speed) or (player_x_dir == 1 and player_vx < player_x_speed):
                player_vx += player_x_dir * player_x_acceleration
        elif player_vx != 0:
            player_vx -= abs(player_vx)/(player_vx*scale)
            if abs(player_vx) < 1:
                player_vx = 0

        if player_vx == 0 and math.floor(player_x) + floor_sub != player_x:
            player_x = math.floor(player_x) + floor_sub

        prev_player_x = player_x
        prev_player_y = player_y
        player_x = min(player_x + player_vx + scroll_speed, size[0] - player_width)
        player_y += player_vy
        player_rect = Rect(player_x, player_y, player_width, player_height)

        """  """
        if cloud_spawner.spawn(scroll_speed):
            add_non_colliding_position(Cloud, size, entities, size[0], x_start=size[0], x_end=size[0]*2)

        if bush_spawner.spawn(scroll_speed):
            add_non_colliding_position(Bush, size, entities, size[0], size[1]-(64*scale), x_start=size[0], x_end=size[0]*2)

        if goomba_spawner.spawn(scroll_speed):
            entities.append(Goomba(size[0], size[1]-(48*scale)))

        i = 0
        while i < len(entities):
            entity = entities[i]
            if not entity.tick(scroll_speed, size):
                entities.pop(i)
                continue

            if type(entity) == Goomba and player_rect.colliderect(Rect(entity.x, entity.y, 16*scale, 16*scale)):
                    if prev_player_y+player_height-(8*scale) <= entity.y and not entity.squished and player_vy > 0:
                        entity.squished = True
                        squished += 1
                    elif not entity.squished:
                        print("You squished", squished, "goombas")
                        quit_g()

            entity.draw(screen)
            i += 1

        if player_x < 0:
            print("You squished", squished, "goombas")
            quit_g()

        if player_on_ground:
            if player_running:
                if (player_facing_right and player_vx < 0) or (not player_facing_right and player_vx > 0):
                    player_image = mario_image_t_right if player_facing_right else mario_image_t_left
                else:
                    player_image = mario_running_anim_right[player_running_frame] if player_facing_right else mario_running_anim_left[player_running_frame]
            elif not player_running and abs(player_vx) > 0:
                player_image = mario_image_t_right if player_facing_right else mario_image_t_left
                print("p")
            else:
                player_image = mario_image_right if player_facing_right else mario_image_left
        else:
            player_image = mario_image_j_right if player_facing_right else mario_image_j_left


        screen.blit(player_image, (player_x, player_y, player_width, player_height))

        score_text_string = "Score: " + str(squished)
        score_text = score_font.render(score_text_string, True, (0, 0, 0))
        score_text_rect = score_text.get_rect()
        score_text_rect.center = (size[0] - score_text_rect.width, 50)
        screen.blit(score_text, score_text_rect)

        floor_sub = -(-(units) % (512*scale)) + (1024*scale)*i + 2/scale - math.floor(-(-(units) % (512*scale)) + (1024*scale)*i + 2/scale)

        for i in range(size[0]//(1024*scale) + math.ceil(size[0]/(512*scale))):

            #x = -(-(units) % (512*scale)) + (1024*scale)*i + 2/scale
            #if x < 0:
            #    print(x, "t:",(x * scale * 4) % (scale * 2))
            #    if (x * scale * 4) % (scale * 2):
            #        x += 1/(scale*4)
            #        print(x)


            screen.blit(floor_brick, (math.floor(-(-units % (512*scale)) + (1024*scale)*i + 2/scale), size[1]-(16*scale), 1024*scale, 16*scale))
            screen.blit(floor_brick, (math.floor(-(-units % (512*scale)) + (1024*scale)*i + 2/scale), size[1]-(32*scale), 1024*scale, 16*scale))


        # Show frame and fix framerate
        display.flip()
        timer.tick(fps)
        frame += 1


# Simple end
def quit_g():
    quit()
    sys.exit()

# Run
main()