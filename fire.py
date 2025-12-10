from pico2d import *
import game_world
import game_framework
import math

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 9

PIXEL_PER_METER = (1.0 / 0.03)
GRAVITY = 9.8

class Fire:
    image = None
    sizes = [(0, 71), (92, 76), (185, 74), (276, 74),(367, 74), (456, 74), (548, 71) ]

    def __init__(self, x = 400, y = 300, throwin_speed = 15, throwin_angle = 0):
        if Fire.image == None:
            Fire.image = load_image('./적/남자2(원)/화염.png')

        self.x, self.y = x, y
        self.xv = throwin_speed
        self.yv = 0.0
        self.frame = 0.0
        self.traveled_distance = 0.0

    def draw(self):
        left , width= self.sizes[int(self.frame)]
        bottom = 0
        height = 20
        Fire.image.clip_draw(left, bottom, width, height, self.x, self.y, 40, 40)
        #draw_rectangle(*self.get_bb())

    def update(self):
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(self.sizes)

        distance_this_frame_x = self.xv * game_framework.frame_time * PIXEL_PER_METER
        self.x += distance_this_frame_x
        self.x += game_world.scroll_speed * game_framework.frame_time

        self.traveled_distance += abs(distance_this_frame_x)

        if self.traveled_distance > 350:
            game_world.remove_object(self)

    def get_bb(self):
        return self.x - 20, self.y - 20, self.x + 20, self.y + 20

    def handle_collision(self, group, other):
        if group == 'fire:girl':
            game_world.remove_object(self)
