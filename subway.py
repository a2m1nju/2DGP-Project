from pico2d import *
import game_world
import game_framework


class Subway:
    def __init__(self, image_path, x, y, w, h, depth, is_looping=False):
        self.image = load_image(image_path)
        self.x, self.y, self.w, self.h = x, y, w, h
        game_world.add_object(self, depth)
        self.is_looping = is_looping

        if self.is_looping:
            self.x1 = x
            self.x2 = x + w

    def update(self):
        scroll_amount = game_world.scroll_speed * game_framework.frame_time
        canvas_width = 1600  # main.py 캔버스 크기

        if self.is_looping:
            self.x1 += scroll_amount
            self.x2 += scroll_amount

            if game_world.scroll_speed < 0:
                if self.x1 <= -self.w / 2:
                    self.x1 = self.x2 + self.w
                if self.x2 <= -self.w / 2:
                    self.x2 = self.x1 + self.w

            elif game_world.scroll_speed > 0:
                if self.x1 >= canvas_width + self.w / 2:
                    self.x1 = self.x2 - self.w
                if self.x2 >= canvas_width + self.w / 2:
                    self.x2 = self.x1 - self.w

        else:
            self.x += scroll_amount
            if game_world.scroll_speed < 0 and self.x + self.w / 2 < 0:
                game_world.remove_object(self)
            elif game_world.scroll_speed > 0 and self.x - self.w / 2 > canvas_width:
                game_world.remove_object(self)

    def draw(self):
        if self.is_looping:
            self.image.draw(self.x1, self.y, self.w, self.h)
            self.image.draw(self.x2, self.y, self.w, self.h)
        else:
            self.image.draw(self.x, self.y, self.w, self.h)

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass