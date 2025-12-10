from pico2d import *
import game_world
import game_framework


class MagicBall:
    image = None
    sizes = [(0, 35), (125, 40), (252, 42), (380, 41), (506, 35), (636, 37), (765, 42), (886, 57),
             (1002, 80), (1112, 111), (1252, 90), (1384, 86), (1514, 81), (1645, 76), (1775, 70), (1912, 52)]

    def __init__(self, x, y, face_dir):
        if MagicBall.image == None:
            MagicBall.image = load_image('./이펙트/마법.png')
        self.x, self.y = x, y
        self.start_x = x
        self.face_dir = face_dir
        self.velocity = 600 * face_dir
        self.frame = 0

    def update(self):
        self.x += self.velocity * game_framework.frame_time

        if abs(self.x - self.start_x) > 600:
            game_world.remove_object(self)

        if self.x < 0 or self.x > 1600:
            game_world.remove_object(self)

        self.frame = (self.frame + 20 * game_framework.frame_time) % 16

    def draw(self):
        left, width = self.sizes[int(self.frame)]
        bottom = 0
        height = 73

        if self.face_dir == -1:
            self.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.x, self.y, width * 1.5, height* 1.5)
        else:
            self.image.clip_composite_draw(left, bottom, width, height, 0, '', self.x, self.y, width* 1.5, height* 1.5)

        #draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.x - 25, self.y - 25, self.x + 25, self.y + 25

    def handle_collision(self, group, other):
        if group == 'fire:girl':
            game_world.remove_object(self)