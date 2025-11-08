from pico2d import *

class Subway:
    def __init__(self):
        self.image1 = load_image('./배경/내부1.png')

    def update(self):
        pass

    def draw(self):
        self.image1.draw(800, 300, 1600, 600)

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass

