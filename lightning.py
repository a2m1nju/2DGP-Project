from pico2d import *
import game_world
import game_framework

TIME_PER_ACTION = 0.5
TOTAL_FRAMES = 6


class Lightning:
    image = None
    def __init__(self, x, y):
        if Lightning.image is None:
            Lightning.image = load_image('./이펙트/번개.png')

    def update(self):
        pass

    def draw(self):
        pass

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass