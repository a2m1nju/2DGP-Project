from pico2d import load_image, get_time, load_font, draw_rectangle
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDL_KEYUP, SDLK_LEFT, SDLK_a, SDLK_d, SDLK_e

import game_world
import game_framework

from state_machine import StateMachine

def space_down(e): 
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

PIXEL_PER_METER = (10.0 / 0.3) 
RUN_SPEED_KMPH = 20.0 
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 9


class Idle:
    image = None
    sizes = []
    def __init__(self, enemy):
        self.enemy = enemy
        if Idle.image == None:
            Idle.image = load_image('./적/남자1(근)/Idle.png')

    def enter(self, e):
        pass


    def exit(self, e):
        pass

    def do(self):
        pass

    def draw(self):
        pass

    def get_bb(self):
        pass


class Run:
    image = None
    sizes = []
    def __init__(self, enemy):
        self.enemy = enemy
        if Run.image == None:
            Run.image = load_image('./적/남자1(근)/Run.png')

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

    def get_bb(self):
        pass

class Walk:
    image = None
    sizes = []
    def __init__(self, enemy):
        self.enemy = enemy
        if Walk.image == None:
            Walk.image = load_image('./적/남자1(근)/Walk.png')

    def enter(self, e):
        pass

    def exit(self, e):
        pass

    def do(self):
        pass


    def draw(self):
        pass

    def get_bb(self):
        pass

class Attack:
    image = None
    sizes = []
    def __init__(self, enemy):
        self.enemy = enemy
        if Attack.image == None:
            Attack.image = load_image('./적/남자1(근)/Attack.png')

    def enter(self, e):
        pass

    def exit(self, e):
        pass

    def do(self):
        pass

    def draw(self):
        pass

    def get_bb(self):
        pass

class Hurt:
    image = None
    sizes = []
    def __init__(self, enemy):
        self.enemy = enemy
        if Hurt.image == None:
            Hurt.image = load_image('./적/남자1(근)/Hurt.png')

    def enter(self, e):
        pass

    def exit(self, e):
        pass

    def do(self):
        pass

    def draw(self):
        pass

    def get_bb(self):
        pass

class Dead:
    image = None
    sizes = []
    def __init__(self, enemy):
        self.enemy = enemy
        if Dead.image == None:
            Dead.image = load_image('./적/남자1(근)/Dead.png')

    def enter(self, e):
        pass

    def exit(self, e):
        pass

    def do(self):
        pass

    def draw(self):
        pass

    def get_bb(self):
        pass

class Enenmy:
    def __init__(self):

        self.ball_count = 10

        self.x, self.y = 100, 150
        self.frame = 0.0
        self.face_dir = 1
        self.dir = 0

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.WALK = Walk(self)
        self.ATTACK = Attack(self)
        self.HURT = Hurt(self)
        self.DEAD = Dead(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.PROTECTION : {e_up: self.IDLE},
                self.IDLE : {space_down: self.ATTACK, right_down: self.WALK, left_down: self.WALK
                             , left_up: self.WALK, right_up : self.WALK , e_down: self.PROTECTION},
                self.RUN : {},
                self.WALK : {space_down: self.ATTACK, right_up: self.IDLE, left_up: self.IDLE,
                             right_down: self.IDLE, left_down: self.IDLE, e_down: self.PROTECTION},
                self.ATTACK : {time_out: self.IDLE, e_down: self.PROTECTION, space_down: self.ATTACK,
                               right_down: self.WALK, left_down: self.WALK},
                self.HURT : {},
                self.DEAD : {}
            }
        )

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_a:
                self.key_a_down = True
            elif event.key == SDLK_d:
                self.key_d_down = True
        elif event.type == SDL_KEYUP:
            if event.key == SDLK_a:
                self.key_a_down = False
            elif event.key == SDLK_d:
                self.key_d_down = False

        self.state_machine.handle_state_event(('INPUT', event))
        pass


    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.state_machine.get_bb()

    def handle_collision(self, group, other):
        pass
