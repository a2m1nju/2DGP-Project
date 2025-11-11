from pico2d import *
import game_world
import game_framework
import random

FALL_SPEED_PPS = 300
GROUND_Y = 130
PIXEL_PER_METER = (1.0 / 0.03)
GRAVITY = 9.8

FOOD_IMAGE_PATHS = [
    './아이템/음식/김밥.png',
    './아이템/음식/샌드위치.png',
    './아이템/음식/토마토.png'
]
class Food:
    image_cache = {}

    def __init__(self, x, y):
        self.value = random.randint(5, 15)
        image_path = random.choice(FOOD_IMAGE_PATHS)

        if image_path not in Food.image_cache:
            Food.image_cache[image_path] = load_image(image_path)

        self.image = Food.image_cache[image_path]

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
        self.image.draw(self.x, self.y, 30, 30)
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.x - 15, self.y - 15, self.x + 15, self.y + 15

    def handle_collision(self, group, other):
        if group == 'girl:food':
            game_world.remove_object(self)