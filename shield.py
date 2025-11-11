from pico2d import *
import game_world
import game_framework

TIME_PER_ACTION = 0.2
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 1


class Shield:
    image = None
    sizes = [0, 186, 380]

    def __init__(self, x, y):
        if Shield.image is None:
            Shield.image = load_image('./이펙트/쉴드.png')

        self.x, self.y = x, y
        self.frame = 0.0
        self.total_frames = len(self.sizes)
        self.is_active = True

    def update(self):
        if not self.is_active:
            game_world.remove_object(self)
            return

        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)

        if self.frame >= self.total_frames:
            self.frame = 0.0

    def draw(self):
        left = self.sizes[int(self.frame)]
        bottom = 0
        width = 170
        height = 163

        Shield.image.clip_draw(left, bottom, width, height, self.x, self.y, 200, 200)

    def get_bb(self):
        return 0,0,0,0

    def handle_collision(self, group, other):
        pass

    def deactivate(self):
        self.is_active = False