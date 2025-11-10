from pico2d import *
import game_world
import game_framework

FALL_SPEED_PPS = 300
GROUND_Y = 130

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 9
PIXEL_PER_METER = (1.0 / 0.03)
GRAVITY = 9.8

class Coin:
    image = None

    def __init__(self, x, y):
        if Coin.image is None:
            Coin.image = load_image('./코인/코인_드랍1.png')
        self.x, self.y = x, y
        self.yv = FALL_SPEED_PPS

    def update(self):
        self.x += game_world.scroll_speed * game_framework.frame_time

        if self.y > GROUND_Y:
            self.yv -= GRAVITY * PIXEL_PER_METER * game_framework.frame_time
            self.y += self.yv * game_framework.frame_time

        if self.y < GROUND_Y:
            self.y = GROUND_Y
            self.yv = 0

    def draw(self):
        self.image.draw(self.x, self.y, 24, 24)
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.x - 12, self.y - 12, self.x + 12, self.y + 12

    def handle_collision(self, group, other):
        if group == 'girl:coin':
            game_world.remove_object(self)
