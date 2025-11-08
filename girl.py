from pico2d import load_image, get_time, load_font, draw_rectangle
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT

import game_world
import game_framework

from state_machine import StateMachine


def space_down(e): # e is space down ?
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

time_out = lambda e: e[0] == 'TIMEOUT'

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT


def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT


def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT


def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT

PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 20.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 9


class Idle:
    image = None
    def __init__(self, girl):
        self.girl = girl
        if Idle.image == None:
            Idle.image = load_image('./주인공/Idle.png')

    def enter(self, e):
        self.girl.wait_time = get_time()
        self.girl.dir = 0


    def exit(self, e):
        pass

    def do(self):
        self.girl.frame = (self.girl.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8
        if get_time() - self.girl.wait_time > 3:
            self.girl.state_machine.handle_state_event(('TIMEOUT', None))

    def draw(self):
        Idle.image.clip_draw(int(self.girl.frame) * 130, 0, 130, 130, self.girl.x, self.girl.y, 200, 200)

class Protection:

    def __init__(self, girl):
        pass

    def enter(self, e):
        pass

    def exit(self, e):
        pass

    def do(self):
        pass

    def handle_event(self, event):
        pass

    def draw(self):
        pass


class Walk:
    def __init__(self, girl):
        pass
    def enter(self, e):
        pass
    def exit(self, e):
        pass

    def do(self):
        pass

    def draw(self):
        pass

class Attack:
    def __init__(self, girl):
        pass

    def enter(self, e):
        pass

    def exit(self, e):
        pass

    def do(self):
        pass

    def draw(self):
        pass

class Girl:
    def __init__(self):

        self.ball_count = 10

        self.x, self.y = 100, 150
        self.frame = 0
        self.face_dir = 1
        self.dir = 0

        self.IDLE = Idle(self)
        self.PROTECTION = Protection(self)
        self.WALK = Walk(self)
        self.ATTACK = Attack(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.PROTECTION : {},
                self.IDLE : {},
                self.WALK : {},
                self.ATTACK : {}
            }
        )


    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
        pass

    def draw(self):
        self.state_machine.draw()

    def get_bb(self):
        pass

    def handle_collision(self, group, other):
        pass
