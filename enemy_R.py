from pico2d import load_image, get_time, load_font, draw_rectangle

import game_world
import game_framework

from state_machine import StateMachine

time_out = lambda e: e[0] == 'TIMEOUT'
player_in_sight_range = lambda e: e[0] == 'PLAYER_IN_SIGHT_RANGE'
player_in_attack_range = lambda e: e[0] == 'PLAYER_IN_ATTACK_RANGE'
player_out_of_range = lambda e: e[0] == 'PLAYER_OUT_OF_RANGE'
hit_by_book = lambda e: e[0] == 'HIT_BY_BOOK'
hp_is_zero = lambda e: e[0] == 'HP_IS_ZERO'
attack_finished = time_out
hurt_finished = time_out
dead_finished = time_out

PIXEL_PER_METER = (10.0 / 0.3)
RUN_SPEED_KMPH = 15.0
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
            Idle.image = load_image('./적/남자2(원)/Idle.png')

    def enter(self, e):
        pass

    def exit(self, e):
        pass

    def do(self):
        pass

    def draw(self):
        pass

    def get_bb(self):
        return 0,0,0,0

class Walk:
    image = None
    sizes = []
    def __init__(self, enemy):
        self.enemy = enemy
        if Walk.image == None:
            Walk.image = load_image('./적/남자2(원)/Walk.png')

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
        return 0,0,0,0

class Attack:
    image = None
    sizes = []
    def __init__(self, enemy):
        self.enemy = enemy
        if Attack.image == None:
            Attack.image = load_image('./적/남자2(원)/Special_Blow.png')

    def enter(self, e):
        pass

    def exit(self, e):
        pass

    def do(self):
        pass

    def draw(self):
        pass

    def get_bb(self):
        return 0,0,0,0

class Hurt:
    image = None
    sizes =  []
    def __init__(self, enemy):
        self.enemy = enemy
        if Hurt.image == None:
            Hurt.image = load_image('./적/남자2(원)/Hurt.png')

    def enter(self, e):
        pass

    def exit(self, e):
        pass

    def do(self):
        pass

    def draw(self):
        pass

    def get_bb(self):
        return 0,0,0,0


class Dead:
    image = None
    sizes =  []
    def __init__(self, enemy):
        self.enemy = enemy
        if Dead.image == None:
            Dead.image = load_image('./적/남자2원(원)/Dead.png')

    def enter(self, e):
        pass

    def exit(self, e):
        pass

    def do(self):
        pass

    def draw(self):
        pass

    def get_bb(self):
        return 0,0,0,0

class Enemy:
    font = None
    def __init__(self, girl):
        self.x, self.y = 1300, 150
        self.frame = 0.0
        self.face_dir = 1
        self.dir = 0
        self.girl = girl
        self.hp = 10

        self.IDLE = Idle(self)
        self.WALK = Walk(self)
        self.ATTACK = Attack(self)
        self.HURT = Hurt(self)
        self.DEAD = Dead(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE : {},
                self.WALK : {},
                self.ATTACK : {},
                self.HURT : {},
                self.DEAD : {}
            }
        )

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        pass


    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.state_machine.get_bb()

    def handle_collision(self, group, other):
        pass