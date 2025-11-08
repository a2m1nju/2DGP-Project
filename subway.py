from pico2d import *
import game_world

class Subway:
    def __init__(self, image_path, x, y, w, h, depth):
        self.image = load_image(image_path)
        self.x, self.y, self.w, self.h = x, y, w, h
        game_world.add_object(self, depth)


    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x, self.y, self.w, self.h)

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass

