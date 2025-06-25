# Nathan Gorman
# 13 June 2025 (edit because I forgot header)
# Mini game contest
# Use left and right arrow keys to move and space bar or up arrow to jump

# Note: this uses the colors from nestopia
import queue
import sys, random
from pygame import *
import math

scale: int

class Entity:
    images: list[Surface]

    def draw(self, screen: Surface):
        pass

    def tick(self, scroll_speed, size):
        pass

    def set_palette(self, palette):
        for image in self.images:
            image.set_palette(palette)

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

# "There's no such thing as compile time in python" - an idiot
Cloud = type("Cloud", (Scroller,), {"speed": -0.5, "list": []})
Bush = type("Bush", (Scroller,), {"speed": 0, "list": []})
Hill = type("Hill", (Scroller,), {"speed": 0, "list": []})

class Goomba(Entity):
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

def load_scaled_indexed_image(name: str): #, scale: int):
    result = image.load(name)
    palette = result.get_palette()
    result = transform.scale(result, (result.width*scale, result.height*scale))
    result.set_palette(palette)
    return result

def load_scaled_indexed_image_palette(name: str): #, scale: int):
    result = image.load(name)
    palette = result.get_palette()
    result = transform.scale(result, (result.width*scale, result.height*scale))
    result.set_palette(palette)
    return result, palette

def load_scaled_flipped_image(name: str): #, scale: int):
    result = load_scaled_image(name)
    return result, transform.flip(result, True, False)

def load_scaled_flipped_indexed_image(name: str): #, scale: int):
    result = image.load(name)
    palette = result.get_palette()
    result = transform.scale(result, (result.width*scale, result.height*scale))
    result_flipped = transform.flip(result, True, False)
    result.set_palette(palette)
    result_flipped.set_palette(palette)
    return result, result_flipped

def load_scaled_flipped_indexed_image_palette(name: str): #, scale: int):
    result = image.load(name)
    palette = result.get_palette()
    result = transform.scale(result, (result.width*scale, result.height*scale))
    result_flipped = transform.flip(result, True, False)
    result.set_palette(palette)
    result_flipped.set_palette(palette)
    return result, result_flipped, palette

def add_non_colliding_position(class_type: type, size, entities: list[Entity], scrollables: list[Scroller], x_pos: int = None, y_pos: int = None, x_start = 0, x_end = None, y_start = 0, y_end = None):
    img = random.randint(0, 1)
    offset = 0

    if class_type is Hill and img == 1:
        offset += scale*3

    x_end = size[0] - class_type.images[img].width if x_end is None else x_end
    y_end = size[1] - class_type.images[img].height - scale*128 if y_end is None else y_end

    x = random.randint(x_start, x_end)//4 * 4 if x_pos is None else x_pos
    y = random.randint(y_start, y_end) if y_pos is None else y_pos - offset
    collision = True

    i = 0
    while collision:
        for scrollable in scrollables:
            if Rect(x, y, class_type.images[img].width, class_type.images[img].height).colliderect((scrollable.x, scrollable.y, scrollable.img.width, scrollable.img.height)):
                collision = True
                if x_pos is None: x = random.randint(0, size[0] - class_type.images[img].width)//4 * 4
                if y_pos is None: y = random.randint(0, size[1] - class_type.images[img].height - (scale*128))//4 * 4
                break
        else:
            collision = False

        i += 1

        if i > 10: return

    result = class_type(x, y, img)
    entities.append(result)
    scrollables.append(result)

def init_scrollable(class_type: type, size, scroll_speed, entities, scrollables, starting_amount, x_pos = None, y_pos = None) -> int:
    for i in range(starting_amount):
        add_non_colliding_position(class_type, size, entities, scrollables, x_pos, y_pos)

    return size[0]/((scroll_speed + class_type.speed)*-starting_amount)

def main():
    global scale

    # Initiate pygame
    init()

    font_name = "font/super-mario-bros-nes.ttf"

    # Timing
    timer = time.Clock()
    fps = 60

    # Set up display
    desktop_size = display.get_desktop_sizes()[0]

    # height = int(desktop_size[0] * (9/16))
    # if height < desktop_size[1]:
    #     size = (desktop_size[0], height)
    # else:
    #     size = (int(desktop_size[1] * 16/9), desktop_size[1])

    # Some weird bugs that I'm too lazy to debug happen when scale is not even
    # scale = size[0]//480
    # scale = 4

    screen_ratio = 4/3
    #screen_ratio = 16/9
    tiles_width = 16
    tiles_height = int(tiles_width*(1/screen_ratio))

    width = desktop_size[0] // (16*tiles_width)
    height = desktop_size[1] // (16*tiles_height)

    # print(desktop_size, width, height)

    scale = 2**math.floor(math.log2(min(width, height)))
    scale = 4
    size = (16*tiles_width*scale, 16*tiles_height*scale)
    # print(size)

    Cloud.speed = -0.125 * scale

    if size == desktop_size:
        screen = display.set_mode(size, FULLSCREEN)
    else:
        screen = display.set_mode(size)

    display.set_caption("Game")

    score_font = font.Font(font_name, scale*8)

    mario_image_right, mario_image_left = load_scaled_flipped_indexed_image("mario.gif")
    #mario_image_right.set_palette([(255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255), (255, 255, 0, 255), (255, 0, 255, 255), (0, 255, 255, 255), (255, 255, 255, 255)])

    mario_image_r1_right, mario_image_r1_left = load_scaled_flipped_indexed_image("mario_r1.gif")
    mario_image_r2_right, mario_image_r2_left = load_scaled_flipped_indexed_image("mario_r2.gif")
    mario_image_r3_right, mario_image_r3_left = load_scaled_flipped_indexed_image("mario_r3.gif")

    mario_image_j_right, mario_image_j_left = load_scaled_flipped_indexed_image("mario_j.gif")
    mario_image_t_right, mario_image_t_left = load_scaled_flipped_indexed_image("mario_t.gif")

    mario_d_image = load_scaled_indexed_image("mario_d.gif")

    mario_palettes = (((107, 107, 0), (181, 49, 33), (230, 156, 33)),)

    mario_images = [mario_image_right, mario_image_left, mario_image_r1_right, mario_image_r2_right, mario_image_r3_right, mario_image_r1_left, mario_image_r2_left, mario_image_r3_left, mario_image_j_right, mario_image_j_left, mario_image_t_right, mario_image_t_left, mario_d_image]

    for mario_image in mario_images:
        mario_image.set_palette(mario_palettes[0])

    floor_brick = load_scaled_indexed_image("floor_brick.gif")
    brick_1 = load_scaled_indexed_image("brick_1.gif")
    brick_2 = load_scaled_indexed_image("brick_2.gif")
    palette_1 = (((0, 0, 0), (156, 74, 0), (255, 204, 197)), ((0, 0, 0), (0, 123, 139), (181, 235, 242)), ((99, 99, 99), (173, 173, 173), (255, 255, 255)), ((0, 0, 0), (16, 148, 0), (189, 244, 171)))
    floor_brick.set_palette(palette_1[0])
    brick_1.set_palette(palette_1[0])
    brick_2.set_palette(palette_1[0])

    cloud_1 = load_scaled_indexed_image("cloud_1.gif")
    cloud_2 = load_scaled_indexed_image("cloud_2.gif")
    palette_2 = (((0, 0, 0), (99, 173, 255), (255, 255, 255)), ((0, 123, 140), (99, 173, 255), (255, 255, 255)), ((99, 99, 99), (181, 49, 33), (255, 255, 255)), ((0, 0, 0), (66, 66, 255), (255, 255, 255)), ((0, 0, 0), (99, 173, 255), (255, 255, 255)), ((0, 0, 0), (99, 173, 255), (255, 255, 255)))
    cloud_1.set_palette(palette_2[0])
    cloud_2.set_palette(palette_2[0])
    Cloud.images = [cloud_1, cloud_2]

    bush_1 = load_scaled_indexed_image("bush_1.gif")
    bush_2 = load_scaled_indexed_image("bush_2.gif")
    palette_0 = (((0, 0, 0), (16, 148, 0), (140, 214, 0)), ((8, 74, 0), (16, 148, 0), (140, 214, 0)), ((99, 99, 99), (172, 172, 172), (255, 255, 255)), ((255, 107, 206), (66, 66, 255), (181, 33, 123)), ((0, 0, 0), (181, 49, 33), (230, 156, 33)), ((173, 173,  173), (99, 99, 99), (255, 255, 255)))
    # hill_palettes = (((8, 74, 0, 255), (8, 74, 0, 255), (16, 148, 0, 255)))
    # bush_2.set_palette(((0, 0, 0, 255), (71, 193, 49, 255), (3, 229, 3, 255)))
    bush_1.set_palette(palette_0[0])
    bush_2.set_palette(palette_0[0])
    Bush.images = [bush_1, bush_2]

    hill_1 = load_scaled_indexed_image("hill_1.gif")
    hill_2 = load_scaled_indexed_image("hill_2.gif")
    hill_1.set_palette(palette_0[0])
    hill_2.set_palette(palette_0[0])
    Hill.images = [hill_1, hill_2]

    goomba_1 = load_scaled_indexed_image("goomba_1.gif")
    goomba_2 = load_scaled_indexed_image("goomba_2.gif")
    goomba_3 = load_scaled_indexed_image("goomba_3.gif")
    Goomba.images = [goomba_1, goomba_2, goomba_3]

    coin = load_scaled_indexed_image("coin.gif")
    palette_3 = ((((0, 0, 0), (156, 74, 0), (230, 156, 33)), ((0, 0, 0), (156, 74, 0), (156, 74, 0)), ((0, 0, 0), (156, 74, 0), (82, 33, 0))), (((0, 123, 140), (156, 74, 0), (230, 156, 33)), ((0, 123, 140), (156, 74, 0), (156, 74, 0)), ((0, 123, 140), (156, 74, 0), (82, 33, 0))), (((99, 99, 99), (156, 74, 0), (230, 156, 33)), ((99, 99, 99), (156, 74, 0), (156, 74, 0)), ((99, 99, 99), (156, 74, 0), (82, 33, 0))), (((0, 0, 0), (66, 66, 255), (230, 156, 33)), ((0, 0, 0), (66, 66, 255), (156, 74, 0)), ((0, 0, 0), (66, 66, 255), (82, 33, 0))))
    palette_3_anim = (0, 0, 1, 2, 1)
    coin.set_palette(palette_3[0][0])

    tile_images = [brick_1, brick_2, coin]
    collidable = [0, 1, 1, 0]

    # Player vars
    player_width = mario_image_right.get_width()
    player_height = mario_image_right.get_height()
    player_x = 96*scale
    player_y = size[1] - (32*scale) - player_height
    prev_player_x = player_x
    prev_player_y = player_y
    player_vx = 0
    player_vy = 0

    # 3.741657386776, 4.472135955
    player_min_jump_strength = -(65/3) * (scale/4) #(4*scale)
    player_max_jump_strength = -13 * (scale/2)
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
    scrollables: list[Scroller] = []
    frame = 0
    palette02 = 0
    palette13 = 0
    palette = 0
    #collided = False

    cloud_spawner = Spawner(2, init_scrollable(Cloud, size, scroll_speed, entities, scrollables, 5))
    bush_spawner = Spawner(2, init_scrollable(Bush, size, scroll_speed, entities, scrollables, 2, y_pos = size[1]-(64*scale)))
    hill_spawner = Spawner(2, init_scrollable(Hill, size, scroll_speed, entities, scrollables, 2, y_pos = size[1]-(64*scale)))
    goomba_spawner = Spawner(2, 64*scale)

    score = 0
    units = 0
    floor_sub = 0

    #world = [(0, 16, 10, 5, 2)]
    world_x = 0
    # tiles_per_section = 4
    # tiles_since_section = 0

    player_tiles = (int((player_x + player_vx - world_x) // (scale*16)), int((player_y + player_vy) // (scale*16))), (int((player_x + player_vx + player_width - world_x) // (scale*16)), int((player_y + player_vy) // (scale*16))), (int((player_x + player_vx + player_width - world_x) // (scale*16)), int((player_y + player_vy + player_height) // (scale*16))), (int((player_x + player_vx - world_x) // (scale*16)), int((player_y + player_vy + player_height) // (scale*16)))

    sections = [

        [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 3, 3, 0],
            [0, 0, 0, 0],
            [0, 2, 2, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
        [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 2, 2, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ],
    ]

    max_section_width = 0
    for section in sections:
        if len(section[0]) > max_section_width:
            max_section_width = len(section[0])

    tiles: queue[queue[int]] = [[0] * (tiles_width + 1 + max_section_width) for i in range(tiles_height)]
    #tiles[2][2] = 1
    print(tiles)

    next_section = random.randint(0, len(sections)-1)
    tiles_until_section = len(sections[next_section][0])

    time_since_start = 0
    dead = False

    while True:
        # fill background
        screen.fill((136, 134, 255))

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

                elif ev.key == K_p:
                    palette02 = (palette02+1) % len(palette_0)
                    palette13 = palette02 if palette02 < 4 else 0
                    Bush.set_palette(Bush, palette_0[palette02])
                    Hill.set_palette(Hill, palette_0[palette02])
                    Cloud.set_palette(Cloud, palette_2[palette02])
                    floor_brick.set_palette(palette_1[palette13])
                    brick_1.set_palette(palette_1[palette13])

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

        """ Tick """
        if not dead:
            """ Player Update """
            # scroll_speed = (((size[0] - player_width - ((size[0]/10)*scale)) - player_x) // (32*scale))/(4/scale) if player_x > size[0] - player_width - ((size[0]/10)*scale) else -0.25*scale

            scroll_speed = (((size[0] - player_width - ((size[0]/10)*scale)) - player_x) // (32*scale))*2 if player_x > size[0] - player_width - ((size[0]/10)*scale) else -0.25*scale
            units += scroll_speed

            player_running = left or right

            if player_running and not frame % 6:
                player_running_frame += 1 if player_running_frame < 3 else -3

            if to_jump and player_on_ground:
                speed = abs(player_vx)/player_x_speed
                player_vy = speed*player_max_jump_strength + (1-speed)*player_min_jump_strength

            if not player_on_ground:
                player_vy += gravity

            if player_y + player_vy >= ground_height and player_vy >= 0:# and not player_was_on_ground and not collided:
                player_vy = 0
                player_y = ground_height

            if player_x_dir != 0:
                if (player_x_dir == -1 and player_vx > -player_x_speed) or (player_x_dir == 1 and player_vx < player_x_speed):
                    player_vx += player_x_dir * player_x_acceleration
            elif player_vx != 0:
                player_vx -= abs(player_vx)/(player_vx*scale)
                if abs(player_vx) < 1:
                    player_vx = 0

            if player_vx == 0 and math.floor(player_x) + floor_sub != player_x and player_on_ground:
                #print("i", math.floor(player_x) + floor_sub)
                player_x = math.floor(player_x) + floor_sub

            #prev_tiles = player_tiles
            player_tiles = (int((player_x + player_vx - world_x) // (scale*16)), int((player_y + player_vy) // (scale*16))), (int((player_x + player_vx + player_width - world_x) // (scale*16)), int((player_y + player_vy) // (scale*16))), (int((player_x + player_vx + player_width - world_x) // (scale*16)), int((player_y + player_vy + player_height) // (scale*16))), (int((player_x + player_vx - world_x) // (scale*16)), int((player_y + player_vy + player_height) // (scale*16)))
            # tiles_to_check: set = {player_tiles[0], player_tiles[1], player_tiles[2], player_tiles[3]}

            #draw.polygon(screen, (0, 255, 0), ((player_tiles[0][0]*16*scale + world_x, player_tiles[0][1]*16*scale), (player_tiles[1][0]*16*scale + world_x, player_tiles[1][1]*16*scale), (player_tiles[2][0]*16*scale + world_x, player_tiles[2][1]*16*scale), (player_tiles[3][0]*16*scale + world_x, player_tiles[3][1]*16*scale)))

            #for player_tile in player_tiles:
            #    for i in range(3):
            #        for j in range(3):
            #            tiles_to_check.add((player_tile[0] + i-1, player_tile[1] + j-1))



            #collided = False
            player_on_ground = False

            for i in range(len(player_tiles)):
                tile = player_tiles[i]
                #prev_tile = prev_tiles[i]
                was_to_left = player_x + player_width <= (tile[0])*16*scale + world_x
                was_to_right = player_x >= (tile[0]+1)*16*scale + world_x
                was_below = player_y >= (tile[1]+1)*16*scale
                was_above = player_y + player_height <= tile[1]*16*scale
                num_true = was_to_left + was_to_right + was_below + was_above
                block_type = tiles[tile[1]][tile[0]]

                if collidable[block_type]:
                    #collided = True
                    # if num_true == 2: print(num_true, was_to_left, was_to_right, was_below, was_above, player_x, (tile[0]+1)*16*scale + world_x, player_x + player_width, (tile[0])*16*scale + world_x)
                    #if num_true == 0:
                    #print(prev_player_x, prev_player_y, player_vx, player_vy)
                    if num_true == 1:
                        if was_to_left or was_to_right:
                            player_vx = 0
                            #print(player_x, tile[0])
                            # print(player_x, tile[0], world_x, (tile[0]-1)*16*scale + world_x)
                            #print("a", (tile[0]+1)*16*scale + world_x if was_to_right else (tile[0]-1)*16*scale + world_x)
                            player_x = (tile[0]+1)*16*scale + world_x if was_to_right else (tile[0]-1)*16*scale + world_x

                        elif was_below:
                            player_vy = 0
                            player_y = (tile[1]+1)*16*scale

                        else:
                            player_on_ground = True
                            player_y = (tile[1] - 1)*16*scale
                            player_vy = 0

                    elif num_true == 2:
                        corner_x = tile[0]*16*scale if was_to_left else (tile[0]+1)*16*scale
                        corner_y = tile[1]*16*scale if was_above else (tile[1]+1)*16*scale
                        check_corner = True

                        #if was_to_left or was_to_right:
                        if collidable[tiles[tile[1] - 1][tile[0]]]:
                            player_vx = 0
                            player_x = (tile[0]+1)*16*scale + world_x if was_to_right else (tile[0]-1)*16*scale + world_x
                            check_corner = False

                            if was_below and (collidable[tiles[tile[1]][tile[0] - 1]] and was_to_left) or (collidable[tiles[tile[1]][tile[0] + 1]] and was_to_right):
                                    player_vy = 0
                                    player_y = (tile[1]+1)*16*scale

                            elif was_above and (collidable[tiles[tile[1]][tile[0] - 1]] and was_to_left) or (collidable[tiles[tile[1]][tile[0] + 1]] and was_to_right):
                                    player_on_ground = True
                                    player_y = (tile[1] - 1)*16*scale
                                    player_vy = 0

                        '''if was_below and collidable[tiles[tile[1] - 1][tile[0]]]:
                            #print("a")
                            if (collidable[tiles[tile[1]][tile[0] - 1]] and was_to_left) or (collidable[tiles[tile[1]][tile[0] + 1]] and was_to_right):
                                #print("b")
                                player_vy = 0
                                player_y = (tile[1]+1)*16*scale
                            player_vx = 0
                            #print("b", (tile[0]+1)*16*scale + world_x if was_to_right else (tile[0]-1)*16*scale + world_x)
                            player_x = (tile[0]+1)*16*scale + world_x if was_to_right else (tile[0]-1)*16*scale + world_x
                            check_corner = False
                        
                        # was tile[1] + 1
                        elif was_above and collidable[tiles[tile[1] - 1][tile[0]]]:
                            print("c", player_x, (tile[0]+1)*16*scale + world_x, (tile[0]+1)*16*scale + world_x if was_to_right else (tile[0]-1)*16*scale + world_x)
                            if (collidable[tiles[tile[1]][tile[0] - 1]] and was_to_left) or (collidable[tiles[tile[1]][tile[0] + 1]] and was_to_right):
                                #print("d", tiles[tile[1]][tile[0] - 1], was_to_left, tiles[tile[1]][tile[0] + 1], was_to_right)
                                player_on_ground = True
                                player_y = (tile[1] - 1)*16*scale
                                player_vy = 0
                            player_vx = 0
                            #print("c", (tile[0]+1)*16*scale + world_x if was_to_right else (tile[0]-1)*16*scale + world_x)
                            player_x = (tile[0]+1)*16*scale + world_x if was_to_right else (tile[0]-1)*16*scale + world_x
                            check_corner = False'''

                        if check_corner and not ((player_x - world_x + (player_width if was_to_left else 0) == corner_x and player_vx == 0) or (player_y + (player_height if was_above else 0) == corner_y and player_vy == 0)):
                            slope = player_vy/player_vx if player_vx != 0 else 1e20
                            test = slope*(corner_x - (player_x - world_x + (player_width if was_to_left else 0))) - corner_y + player_y + (player_height if was_above else 0)
                            # print(test, tile, player_x, player_y, player_vx, player_vy, world_x, corner_x, corner_y, player_width if was_to_left else 0, player_height if was_above else 0, was_to_left, was_to_right, was_above, was_below, player_y + (player_height if was_above else 0), player_y + (player_height if was_above else 0) == corner_y, player_vy == 0)
                            # I THINK this is the right way???

                            if was_below:
                                if test > 0:
                                    player_vx = 0
                                    #print("d", (tile[0]+1)*16*scale + world_x if was_to_right else (tile[0]-1)*16*scale + world_x)
                                    player_x = (tile[0]+1)*16*scale + world_x if was_to_right else (tile[0]-1)*16*scale + world_x
                                elif test < 0:
                                    player_vy = 0
                                    player_y = (tile[1]+1)*16*scale
                                elif random.randint(0, 1):
                                    player_vx = 0
                                    #print("e", (tile[0]+1)*16*scale + world_x if was_to_right else (tile[0]-1)*16*scale + world_x)
                                    player_x = (tile[0]+1)*16*scale + world_x if was_to_right else (tile[0]-1)*16*scale + world_x
                                else:
                                    player_vy = 0
                                    player_y = (tile[1]+1)*16*scale

                            else:
                                if test < 0 or (not (test > 0) and random.randint(0, 1)):
                                    player_vx = 0
                                    player_x = (tile[0]+1)*16*scale + world_x if was_to_right else (tile[0]-1)*16*scale + world_x
                                else:
                                    player_on_ground = True
                                    player_y = (tile[1] - 1)*16*scale
                                    player_vy = 0

                            """elif was_to_right and was_below:
                                if test < 0:
                                    player_vx = 0
                                    #print("f", (tile[0]+1)*16*scale + world_x if was_to_right else (tile[0]-1)*16*scale + world_x)
                                    player_x = (tile[0]+1)*16*scale + world_x if was_to_right else (tile[0]-1)*16*scale + world_x
                                elif test > 0:
                                    player_vy = 0
                                    player_y = (tile[1]+1)*16*scale
                                elif random.randint(0, 1):
                                    player_vx = 0
                                    #print("g", (tile[0]+1)*16*scale + world_x if was_to_right else (tile[0]-1)*16*scale + world_x)
                                    player_x = (tile[0]+1)*16*scale + world_x if was_to_right else (tile[0]-1)*16*scale + world_x
                                else:
                                    player_vy = 0
                                    player_y = (tile[1]+1)*16*scale"""

                    else:
                        print("The physics broke again?")
                else:
                    if block_type == 3:
                        tiles[tile[1]][tile[0]] = 0
                        score += 200

            # print(tiles_to_check)

            prev_player_x = player_x
            prev_player_y = player_y
            #print("h", min(player_x + player_vx + scroll_speed, size[0] - player_width))
            player_x = min(player_x + player_vx + scroll_speed, size[0] - player_width)
            #print(player_vy)
            player_y += player_vy
            player_rect = Rect(player_x, player_y, player_width, player_height)

            player_on_ground = player_on_ground or player_y >= ground_height

            """ Spawning """
            if cloud_spawner.spawn(scroll_speed):
                add_non_colliding_position(Cloud, size, entities, scrollables, size[0], x_start=size[0], x_end=size[0]*2)

            if bush_spawner.spawn(scroll_speed):
                add_non_colliding_position(Bush, size, entities, scrollables, size[0], size[1]-(64*scale), x_start=size[0], x_end=size[0]*2)

            if hill_spawner.spawn(scroll_speed):
                add_non_colliding_position(Hill, size, entities, scrollables, size[0], size[1]-(64*scale), x_start=size[0], x_end=size[0]*2)

            if goomba_spawner.spawn(scroll_speed):
                entities.append(Goomba(size[0], size[1]-(48*scale)))

            """ Entity Update """ #and Drawing """
            i = 0
            while i < len(entities):
                entity = entities[i]
                if not entity.tick(scroll_speed, size):
                    entities.pop(i)
                    continue

                if type(entity) == Goomba and player_rect.colliderect(Rect(entity.x, entity.y, 16*scale, 16*scale)):
                        if prev_player_y+player_height-(8*scale) <= entity.y and not entity.squished and player_vy > 0:
                            entity.squished = True
                            score += 100
                        elif not entity.squished:
                            dead = True

                i += 1

            if player_x < 0:
                dead = True

        """ Entity Drawing """
        i = 0
        while i < len(entities):
            entities[i].draw(screen)
            i += 1

        """ World Drawing """
        coin.set_palette(palette_3[palette13][palette_3_anim[time_since_start//150 % (5)]])

        world_x += scroll_speed
        #print(world_x)
        if world_x <= -scale*16:
            world_x += scale*16

            for row in tiles:
                row.pop(0)
                # row.append(0)

            #print(tiles)

            # tiles_since_section += 1
            tiles_until_section -= 1

            if not tiles_until_section:
                # tiles_since_section = 0

                for i in range(len(tiles)):
                    row = tiles[i]

                    if i < len(tiles)-2:
                        for j in range(len(sections[next_section][0])):
                            row.append(sections[next_section][(i)][j])

                    else:
                        for i in range(len(sections[next_section][0])):
                            row.append(0)

                next_section = random.randint(0, len(sections)-1)
                tiles_until_section = len(sections[next_section][0])

        for j in range(len(tiles)):
            for i in range(len(tiles[0])):
                tile = tiles[j][i]
                if tile:
                    screen.blit(tile_images[tile-1], (i*scale*16 + world_x, j*scale*16, 16, 16))


        for i in range(-1, size[0]//(1024*scale) + math.ceil(size[0]/(512*scale))):

            #x = -(-(units) % (512*scale)) + (1024*scale)*i + 2/scale
            #if x < 0:
            #    print(x, "t:",(x * scale * 4) % (scale * 2))
            #    if (x * scale * 4) % (scale * 2):
            #        x += 1/(scale*4)
            #        print(x)


            screen.blit(floor_brick, (math.floor(-(-units % (512*scale)) + (1024*scale)*i + scale/2), size[1]-(16*scale), 1024*scale, 16*scale))
            screen.blit(floor_brick, (math.floor(-(-units % (512*scale)) + (1024*scale)*i + scale/2), size[1]-(32*scale), 1024*scale, 16*scale))

        """for i in range(len(world)):
            item = world[i]
            num_tiles = item[3]*item[4]
            for j in range(num_tiles):
                screen.blit(brick, (scale*16*(item[1] + (j%num_tiles)), scale*16*(item[2] + j//num_tiles), scale*16, scale*16))
            world[i] = (item[0], scroll_speed/(16*scale) + item[1], item[2], item[3], item[4])"""

        """ Player Animation and Drawing"""
        if dead:
            player_image = mario_d_image
        else:
            if player_on_ground:
                if player_running:
                    if (player_facing_right and player_vx < 0) or (not player_facing_right and player_vx > 0):
                        player_image = mario_image_t_right if player_facing_right else mario_image_t_left
                    else:
                        player_image = mario_running_anim_right[player_running_frame] if player_facing_right else mario_running_anim_left[player_running_frame]
                else:
                #elif not player_running and abs(player_vx) > 0:
                #    player_image = mario_image_t_right if player_facing_right else mario_image_t_left
                #else:
                    player_image = mario_image_right if player_facing_right else mario_image_left
            else:
                player_image = mario_image_j_right if player_facing_right else mario_image_j_left


        screen.blit(player_image, (player_x, player_y, player_width, player_height))

        # draw.line(screen, (0, 0, 0), (1024, 0), (1024, size[1]))

        """ UI Drawing """
        score_text_string = "Score:" + str(score)
        score_text = score_font.render(score_text_string, True, (255, 255, 255))
        score_text_rect = score_text.get_rect()
        score_text_rect.center = (size[0] - score_text_rect.width/2 - scale*16, 50)
        screen.blit(score_text, score_text_rect)

        floor_sub = -(-(units) % (512*scale)) + (1024*scale)*i + 2/scale - math.floor(-(-(units) % (512*scale)) + (1024*scale)*i + 2/scale)

        # Show frame and fix framerate
        display.flip()
        time_since_start += timer.tick(fps)
        frame += 1


# Simple end
def quit_g():
    quit()
    sys.exit()

# Run
main()