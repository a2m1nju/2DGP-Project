from pico2d import *
import game_world
import game_framework
import math

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 9

PIXEL_PER_METER = (1.0 / 0.03)  # 1pixel = 3cm, 1m = 33.33 pixel
GRAVITY = 9.8  # 중력 가속도 (m/s²)

class Book:
    image = None
    sizes = [(20, 12, 25, 20), (82, 15, 21, 26), (155, 13, 22, 17), (215, 7, 28, 23),
             (273, 7, 28, 30), (339, 7, 28, 17), (403, 10, 25, 18) ,(470, 9, 26, 15), (529, 2, 34, 25)]

    def __init__(self, x = 400, y = 300, throwin_speed = 15, throwin_angle = 45):
        if Book.image == None:
            Book.image = load_image('./주인공/Book.png')
        self.x, self.y = x, y
        self.xv = throwin_speed * math.cos(math.radians(throwin_angle))
        self.yv = abs(throwin_speed * math.sin(math.radians(throwin_angle)))
        self.stopped = True if throwin_speed == 0.0 else False
        self.frame = 0.0

    def draw(self):
        left , bottom, height, width= self.sizes[int(self.frame)]
        Book.image.clip_draw(left, bottom, width, height, self.x, self.y, 40, 40)

    def update(self):
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(self.sizes)
        if self.stopped:
            return
        self.x += self.xv * game_framework.frame_time * PIXEL_PER_METER
        self.y += self.yv * game_framework.frame_time * PIXEL_PER_METER

        self.x += game_world.scroll_speed * game_framework.frame_time


    def get_bb(self):
        return self.x - 20, self.y - 20, self.x + 20, self.y + 20

    def handle_collision(self, group, other):
        pass



