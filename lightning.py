from pico2d import *
import game_world
import game_framework

THUNDER_DURATION = 0.5
DAMAGE_TICK_INTERVAL = 0.1

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 5

class Lightning:
    image = None
    sizes = [0, 170, 340, 510, 680]

    def __init__(self, x, y):
        if Lightning.image is None:
            Lightning.image = load_image('./이펙트/번개.png')

        self.x, self.y = x, y
        self.frame = 0.0
        self.duration_timer = THUNDER_DURATION
        self.damage_timer = 0.0
        self.hit_enemies = set()

    def update(self):
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(self.sizes)

        self.duration_timer -= game_framework.frame_time
        if self.duration_timer <= 0:
            game_world.remove_object(self)
            return

        self.damage_timer += game_framework.frame_time
        if self.damage_timer >= DAMAGE_TICK_INTERVAL:
            self.damage_timer = 0.0
            self.hit_enemies.clear()
            self.apply_damage_to_enemies_in_range()

    def draw(self):
        bottom = self.sizes[int(self.frame)]
        left = 0
        width = 36
        height = 170

        Lightning.image.clip_draw(left, bottom, width, height, self.x, self.y, 60, 360)
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.x - 15, self.y - 180, self.x + 15, self.y + 180

    def apply_damage_to_enemies_in_range(self):
        for o in game_world.all_objects():
            if 'Enemy' in o.__class__.__name__ and o not in self.hit_enemies:
                if game_world.collide(self, o):
                    o.state_machine.handle_state_event(('HIT_BY_BOOK', None))
                    self.hit_enemies.add(o)

    def handle_collision(self, group, other):
        pass
