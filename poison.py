from pico2d import *
import game_world
import game_framework


class Poison:
    image = None
    sizes = [(0,65), (163,74), (330,86), (484,120),(671,136),
             (866,154),(1058,169),(1275,171),(1488,180),(1706,193)]

    def __init__(self, x, y, duration=3.0, damage=10):
        self.x, self.y = x, y
        self.duration = duration
        self.damage = damage
        self.frame = 0.0

        if Poison.image is None:
            Poison.image = load_image('./이펙트/독/Posion.png')

    def update(self):
        self.x += game_world.scroll_speed * game_framework.frame_time

        self.frame = (self.frame + 5.0 * game_framework.frame_time) % len(self.sizes)

        self.duration -= game_framework.frame_time
        if self.duration <= 0:
            game_world.remove_object(self)

    def draw(self):
        idx = int(self.frame)
        if idx >= len(self.sizes): idx = 0

        left, width = self.sizes[idx]
        bottom = 0
        height = 158

        Poison.image.clip_draw(left, bottom, width, height, self.x, self.y)

        #draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.x - 100, self.y - 60, self.x + 100, self.y + 60

    def handle_collision(self, group, other):
        pass