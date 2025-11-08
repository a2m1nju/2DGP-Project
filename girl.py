from pico2d import load_image, get_time, load_font, draw_rectangle
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDL_KEYUP, SDLK_LEFT, SDLK_a, SDLK_d, SDLK_e

import game_world
import game_framework

from book import Book
from state_machine import StateMachine


def space_down(e): # e is space down ?
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

time_out = lambda e: e[0] == 'TIMEOUT'

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_d

def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_d

def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a

def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_a

def e_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_e

def e_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_e

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
    sizes = [2, 130, 258 ,386, 514, 642, 770, 898, 1026]
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
        self.girl.frame = (self.girl.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 9
        if get_time() - self.girl.wait_time > 3:
            self.girl.state_machine.handle_state_event(('TIMEOUT', None))

    def draw(self):
        left = Idle.sizes[int(self.girl.frame)]
        bottom = 0
        width = 30
        height = 77
        if self.girl.face_dir == -1:
            Idle.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.girl.x, self.girl.y, 70, 180)
        else:
            Idle.image.clip_composite_draw(left, bottom, width, height, 0, '', self.girl.x, self.girl.y, 70, 180)

    def get_bb(self):
        return self.girl.x - 43, self.girl.y - 90, self.girl.x + 43, self.girl.y + 90


class Protection:
    image = None
    sizes = [2, 128, 253, 381]
    def __init__(self, girl):
        self.girl = girl
        if Protection.image == None:
            Protection.image = load_image('./주인공/Protection.png')

    def enter(self, e):
        self.girl.dir = 0

    def exit(self, e):
        pass

    def do(self):
        self.girl.frame = (self.girl.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 4

    def handle_event(self, event):
        pass

    def draw(self):
        left = Protection.sizes[int(self.girl.frame)]
        bottom = 0
        width = 36
        height = 70
        if self.girl.face_dir == -1:
            Protection.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.girl.x, self.girl.y, 70, 180)
        else:
            Protection.image.clip_composite_draw(left, bottom, width, height, 0, '', self.girl.x, self.girl.y, 70, 180)

    def get_bb(self):
        return self.girl.x - 43, self.girl.y - 90, self.girl.x + 43, self.girl.y + 90

class Walk:
    image = None
    sizes = [4, 132, 259, 385 , 513, 642, 772, 902, 1031, 1160, 1287, 1414]
    def __init__(self, girl):
        self.girl = girl
        if Walk.image == None:
            Walk.image = load_image('./주인공/Walk.png')

    def enter(self, e):
        if right_down(e) or left_up(e):
            self.girl.dir = self.girl.face_dir = 1
        elif left_down(e) or right_up(e):
            self.girl.dir = self.girl.face_dir = -1

    def exit(self, e):
        self.girl.face_dir = self.girl.dir

    def do(self):
        self.girl.frame = (self.girl.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 12
        self.girl.x += self.girl.dir * RUN_SPEED_PPS * game_framework.frame_time

    def draw(self):
        left = Walk.sizes[int(self.girl.frame)]
        bottom = 0
        width = 40
        height = 75
        if self.girl.dir == -1:
            Walk.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.girl.x, self.girl.y, 70, 180)
        else:
            Walk.image.clip_composite_draw(left, bottom, width, height, 0, '', self.girl.x, self.girl.y, 70, 180)

    def get_bb(self):
        return self.girl.x - 40, self.girl.y - 90, self.girl.x + 40, self.girl.y + 90

class Attack:
    image = None
    sizes = [(7, 40), (131, 43), (253, 51), (378, 59), (503, 61), (645, 62), (776, 73), (905, 37)]
    def __init__(self, girl):
        self.girl = girl
        if Attack.image == None:
            Attack.image = load_image('./주인공/Attack.png')

    def enter(self, e):
        pass

    def exit(self, e):
        pass

    def do(self):
        self.girl.frame = (self.girl.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8

    def draw(self):
        left, width = Attack.sizes[int(self.girl.frame)]
        bottom = 0
        height = 79
        if self.girl.face_dir == -1:
            Attack.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.girl.x, self.girl.y, 110, 190)
        else:
            Attack.image.clip_composite_draw(left, bottom, width, height, 0, '', self.girl.x, self.girl.y, 110, 190)

    def get_bb(self):
        return self.girl.x - 55, self.girl.y - 90, self.girl.x + 55, self.girl.y + 90

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
                self.PROTECTION : {e_up: self.IDLE},
                self.IDLE : {space_down: self.ATTACK, right_down: self.WALK, left_down: self.WALK
                             , left_up: self.WALK, right_up : self.WALK , e_down: self.PROTECTION},
                self.WALK : {space_down: self.ATTACK, right_up: self.IDLE, left_up: self.IDLE,
                             right_down: self.IDLE, left_down: self.IDLE, e_down: self.PROTECTION},
                self.ATTACK : {space_down: self.IDLE, e_down: self.PROTECTION}
            }
        )


    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
        pass

    def throw_book(self):
        if self.ball_count > 0:
            self.ball_count -= 1
            book = Book(self.x+self.face_dir*40, self.y+100, self.face_dir * 15)
            game_world.add_object(book, 1)

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.state_machine.get_bb()

    def handle_collision(self, group, other):
        pass
