# Nathan Gorman
# 13 June 2025 (edit because I forgot header)
# Mini game contest
# Use left and right arrow keys to move and space bar or up arrow to jump

import sys, pygame, random
from pygame import *

class Entity:
    def draw(self, screen: Surface):
        pass

    def tick(self, scroll_speed, size):
        pass

class Cloud(Entity):
    cloud_images: list[Surface]

    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.img = Cloud.cloud_images[size]

    def draw(self, screen: Surface):
        screen.blit(self.img, (self.x, self.y, self.img.get_width(), self.img.get_height()))

    def tick(self, scroll_speed, size) -> bool:
        self.x += scroll_speed - 0.5
        return self.x > -self.img.get_width()

class Goomba(Entity):
    def __init__(self, x, y, img1, img2, img3):
        self.x = x
        self.y = y
        self.imgs = [img1, img2, img3]
        self.frame = 0
        self.squished = False
        self.squished_time = 0
        self.dead = False

    def tick(self, scroll_speed, size):
        self.frame += 1
        self.x += scroll_speed - 2
        img = self.imgs[((self.frame // 8) % 2)]
        if self.squished:
            self.squished_time += 1
        if self.squished_time >= 2:
            self.dead = True
        return self.x > -img.get_width() and not self.dead

    def draw(self, screen: pygame.Surface):
        img = self.imgs[((self.frame//8)%2)] if not self.squished else self.imgs[2]
        screen.blit(img, (self.x, self.y, img.get_width(), img.get_height()))

def main():

    # Initiate pygame
    init()

    font_name = ""

    for available_font in font.get_fonts():
        if available_font == "freesansbold.ttf":
            font_name = available_font

    if font_name == "":
        font_name = font.get_default_font()

    score_font = pygame.font.Font(font_name, 32)

    # Timing
    timer = time.Clock()
    fps = 60

    # Set up display
    size = display.get_desktop_sizes()[0]
    screen = display.set_mode(size)
    display.set_caption("Game")

    mario_image = image.load("mario.png")
    mario_image_right = transform.scale(mario_image, (mario_image.get_width()*4, mario_image.get_height()*4))
    mario_image_left = transform.flip(mario_image_right, True, False)

    mario_image_r1 = image.load("mario_r1.png")
    mario_image_r1_right = transform.scale(mario_image_r1, (mario_image_r1.get_width() * 4, mario_image_r1.get_height() * 4))
    mario_image_r1_left = transform.flip(mario_image_r1_right, True, False)

    mario_image_r2 = image.load("mario_r2.png")
    mario_image_r2_right = transform.scale(mario_image_r2, (mario_image_r2.get_width() * 4, mario_image_r2.get_height() * 4))
    mario_image_r2_left = transform.flip(mario_image_r2_right, True, False)

    mario_image_r3 = image.load("mario_r3.png")
    mario_image_r3_right = transform.scale(mario_image_r3, (mario_image_r3.get_width() * 4, mario_image_r3.get_height() * 4))
    mario_image_r3_left = transform.flip(mario_image_r3_right, True, False)

    mario_image_j = image.load("mario_j.png")
    mario_image_j_right = transform.scale(mario_image_j, (mario_image_j.get_width() * 4, mario_image_j.get_height() * 4))
    mario_image_j_left = transform.flip(mario_image_j_right, True, False)

    mario_image_t = image.load("mario_t.png")
    mario_image_t_right = transform.scale(mario_image_t, (mario_image_t.get_width() * 4, mario_image_t.get_height() * 4))
    mario_image_t_left = transform.flip(mario_image_t_right, True, False)

    floor_brick = image.load("floor_brick.png")
    floor_brick = transform.scale(floor_brick, (floor_brick.get_width() * 4, floor_brick.get_height() * 4))

    cloud_1 = image.load("cloud_1.png")
    cloud_1 = transform.scale(cloud_1, (cloud_1.get_width() * 4, cloud_1.get_height() * 4))
    cloud_2 = image.load("cloud_2.png")
    cloud_2 = transform.scale(cloud_2, (cloud_2.get_width() * 4, cloud_2.get_height() * 4))
    Cloud.cloud_images = [cloud_1, cloud_2]

    goomba_1 = image.load("goomba_1.png")
    goomba_1 = transform.scale(goomba_1, (goomba_1.get_width() * 4, goomba_1.get_height() * 4))

    goomba_2 = image.load("goomba_2.png")
    goomba_2 = transform.scale(goomba_2, (goomba_2.get_width() * 4, goomba_2.get_height() * 4))

    goomba_3 = image.load("goomba_3.png")
    goomba_3 = transform.scale(goomba_3, (goomba_3.get_width() * 4, goomba_3.get_height() * 4))

    player_width = mario_image_right.get_width()
    player_height = mario_image_right.get_height()
    player_x = 350
    player_y = size[1] - 100 - player_height
    player_vx = 0
    player_vy = 0
    player_jump_strength = -16
    player_on_ground = False
    gravity = 1
    ground_height = size[1]-192
    player_x_speed = 6
    player_x_dir = 0
    left = False
    right = False
    player_facing_right = True
    to_jump = False
    player_running = False
    mario_running_anim_left = [mario_image_r1_left, mario_image_r2_left, mario_image_r3_left, mario_image_r2_left]
    mario_running_anim_right = [mario_image_r1_right, mario_image_r2_right, mario_image_r3_right, mario_image_r2_right]
    player_running_frame = 0
    frame = 0
    player_x_acceleration = 0.5
    scroll_speed = -1
    entities: list[Entity] = [Cloud(random.randint(0, size[0]-cloud_2.get_width()), random.randint(0, size[1]-cloud_2.get_height()-512), random.randint(0, 1), cloud_1, cloud_2), Cloud(size[0] + cloud_2.get_width(), random.randint(0, size[1]-cloud_2.get_height()-512), random.randint(0, 1), cloud_1, cloud_2), Cloud(random.randint(0, size[0]-cloud_2.get_width()), random.randint(0, size[1]-cloud_2.get_height()-512), random.randint(0, 1), cloud_1, cloud_2), Cloud(random.randint(0, size[0]-cloud_2.get_width()), random.randint(0, size[1]-cloud_2.get_height()-512), random.randint(0, 1), cloud_1, cloud_2), Cloud(random.randint(0, size[0]-cloud_2.get_width()), random.randint(0, size[1]-cloud_2.get_height()-512), random.randint(0, 1), cloud_1, cloud_2)]
    squished = 0

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

        player_x = min(player_x + player_vx + scroll_speed, size[0] - player_width)
        player_y += player_vy

        player_rect = Rect(player_x, player_y, player_width, player_height)

        player_running = left or right

        if player_running and not frame % 4:
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
            player_vx -= abs(player_vx)/player_vx

        if random.randint(0, 150) == 0:
            entities.append(Cloud(size[0] + cloud_2.get_width(), random.randint(0, size[1]-cloud_2.get_height()-512), random.randint(0, 1), cloud_1, cloud_2))

        if frame % 240 == 0:
            entities.append(Goomba(size[0], size[1]-192, goomba_1, goomba_2, goomba_3))

        i = 0
        while i < len(entities):
            entity = entities[i]
            if not entity.tick(scroll_speed, size):
                entities.pop(i)
                continue

            if type(entity) == Goomba and player_rect.colliderect(Rect(entity.x, entity.y, 64, 64)):
                    if player_y+player_height-7 <= entity.y and not entity.squished:
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

        for i in range(size[0]//4096 + 1):
            screen.blit(floor_brick, (-(frame % 2048) + 4096*i, size[1]-64, 4096, 64))
            screen.blit(floor_brick, (-(frame % 2048) + 4096 * i, size[1]-128, 4096, 64))

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