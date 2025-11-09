from pico2d import load_image, get_time, load_font, draw_rectangle
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDL_KEYUP, SDLK_LEFT, SDLK_a, SDLK_d, SDLK_e

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
    sizes = [2, 127, 256, 384, 513, 640]
    def __init__(self, enemy):
        self.enemy = enemy
        if Idle.image == None:
            Idle.image = load_image('./적/남자1(근)/Idle.png')

    def enter(self, e):
        self.enemy.wait_time = get_time()
        self.enemy.dir = 0
        self.enemy.frame = 0.0

    def exit(self, e):
        pass

    def do(self):
        self.enemy.frame = (self.enemy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 6

        dist_to_player = abs(self.enemy.x - self.enemy.girl.x)

        if dist_to_player < 150:
            self.enemy.state_machine.handle_state_event(('PLAYER_IN_ATTACK_RANGE', None))
        elif dist_to_player < 600:
            self.enemy.state_machine.handle_state_event(('PLAYER_IN_SIGHT_RANGE', None))
        elif get_time() - self.enemy.wait_time > 3:
            self.enemy.state_machine.handle_state_event(('TIMEOUT', None))

    def draw(self):
        left = Idle.sizes[int(self.enemy.frame)]
        bottom = 0
        width = 30
        height = 68
        if self.enemy.face_dir == -1:
            Idle.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.enemy.x, self.enemy.y, 100, 200)
        else:
            Idle.image.clip_composite_draw(left, bottom, width, height, 0, '', self.enemy.x, self.enemy.y, 70, 180)

    def get_bb(self):
        return self.enemy.x - 35, self.enemy.y - 90, self.enemy.x + 35, self.enemy.y + 90


class Run:
    image = None
    sizes = [(0, 43), (128, 43), (245, 57), (375, 52), (504, 40), (645, 40),
             (769, 43), (888, 56), (1017, 55), (1146, 38)]
    def __init__(self, enemy):
        self.enemy = enemy
        if Run.image == None:
            Run.image = load_image('./적/남자1(근)/Run.png')

    def enter(self, e):
        self.enemy.frame = 0.0

    def exit(self, e):
        pass

    def do(self):
        dist_to_player = self.enemy.girl.x - self.enemy.x

        if dist_to_player > 0:
            self.enemy.dir = 1
            self.enemy.face_dir = 1
        elif dist_to_player < 0:
            self.enemy.dir = -1
            self.enemy.face_dir = -1
        else:  # 정확히 같은 위치
            self.enemy.dir = 0

        dist_abs = abs(dist_to_player)

        if dist_abs < 150:
            self.enemy.state_machine.handle_state_event(('PLAYER_IN_ATTACK_RANGE', None))
        elif dist_abs > 600:
            self.enemy.state_machine.handle_state_event(('PLAYER_OUT_OF_RANGE', None))

        self.enemy.frame = (self.enemy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 10

    def handle_event(self, event):
        pass

    def draw(self):
        left , width = Run.sizes[int(self.enemy.frame)]
        bottom = 0
        height = 73
        if self.enemy.face_dir == -1:
            Run.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.enemy.x, self.enemy.y, 120, 200)
        else:
            Run.image.clip_composite_draw(left, bottom, width, height, 0, '', self.enemy.x, self.enemy.y, 120, 200)

    def get_bb(self):
        return self.enemy.x - 45, self.enemy.y - 90, self.enemy.x + 45, self.enemy.y + 90

class Walk:
    image = None
    sizes = [(0, 36), (125, 40), (254, 35), (388, 22), (519, 28),
             (638, 39), (765, 39), (893, 35), (1028, 23), (1154, 33) ]
    def __init__(self, enemy):
        self.enemy = enemy
        if Walk.image == None:
            Walk.image = load_image('./적/남자1(근)/Walk.png')

    def enter(self, e):
        self.enemy.dir = 1
        self.enemy.frame = 0.0

    def exit(self, e):
        pass

    def do(self):
        self.enemy.frame = (self.enemy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 10

    def draw(self):
        left, width = Walk.sizes[int(self.enemy.frame)]
        bottom = 0
        height = 71
        if self.enemy.face_dir == -1:
            Walk.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.enemy.x, self.enemy.y, 100, 180)
        else:
            Walk.image.clip_composite_draw(left, bottom, width, height, 0, '', self.enemy.x, self.enemy.y, 100, 180)

    def get_bb(self):
        return self.enemy.x - 35, self.enemy.y - 90, self.enemy.x + 35, self.enemy.y + 90

class Attack:
    image = None
    sizes = [(0, 65), (123, 70), (257, 64), (404, 69), (533, 40) ]
    def __init__(self, enemy):
        self.enemy = enemy
        if Attack.image == None:
            Attack.image = load_image('./적/남자1(근)/Attack.png')

    def enter(self, e):
        self.enemy.dir = 0
        self.enemy.frame = 0.0

    def exit(self, e):
        pass

    def do(self):
        self.enemy.frame = (self.enemy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)
        total_frames = len(Attack.sizes)

        if self.enemy.frame >= total_frames:
            self.enemy.frame = total_frames - 1
            self.enemy.state_machine.handle_state_event(('TIMEOUT', None))

    def draw(self):
        left, width = Attack.sizes[int(self.enemy.frame)]
        bottom = 0
        height = 72
        if self.enemy.face_dir == -1:
            Attack.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.enemy.x, self.enemy.y, 160, 220)
        else:
            Attack.image.clip_composite_draw(left, bottom, width, height, 0, '', self.enemy.x, self.enemy.y, 160, 220)

    def get_bb(self):
        return self.enemy.x - 80, self.enemy.y - 110, self.enemy.x + 80, self.enemy.y + 110

class Hurt:
    image = None
    sizes =  [(0, 37), (123, 41), (249, 42)]
    def __init__(self, enemy):
        self.enemy = enemy
        if Hurt.image == None:
            Hurt.image = load_image('./적/남자1(근)/Hurt.png')

    def enter(self, e):
        self.enemy.dir = 0
        self.enemy.frame = 0.0

    def exit(self, e):
        pass

    def do(self):
        self.enemy.frame = (self.enemy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)
        total_frames = len(Hurt.sizes)

        if self.enemy.frame >= total_frames:
            self.enemy.frame = total_frames - 1
            self.enemy.state_machine.handle_state_event(('TIMEOUT', None))

    def draw(self):
        left, width = Hurt.sizes[int(self.enemy.frame)]
        bottom = 0
        height = 67
        if self.enemy.face_dir == -1:
            Hurt.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.enemy.x, self.enemy.y, 120, 180)
        else:
            Hurt.image.clip_composite_draw(left, bottom, width, height, 0, '', self.enemy.x, self.enemy.y, 120, 180)

    def get_bb(self):
        return self.enemy.x - 35, self.enemy.y - 90, self.enemy.x + 35, self.enemy.y + 90


class Dead:
    image = None
    sizes =  [(0, 37), (120, 44), (215, 71), (340, 71)]
    def __init__(self, enemy):
        self.enemy = enemy
        if Dead.image == None:
            Dead.image = load_image('./적/남자1(근)/Dead.png')

    def enter(self, e):
        self.enemy.dir = 0
        self.enemy.frame = 0.0
        game_world.remove_collision_object(self.enemy)

    def exit(self, e):
        pass

    def do(self):
        animation_speed = 4.0
        self.enemy.frame = (self.enemy.frame + animation_speed * ACTION_PER_TIME * game_framework.frame_time)
        total_frames = len(Dead.sizes)

        if self.enemy.frame >= total_frames:
            self.enemy.frame = total_frames - 1

    def draw(self):
        left, width = Dead.sizes[int(self.enemy.frame)]
        bottom = 0
        height = 67
        if self.enemy.face_dir == -1:
            Dead.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.enemy.x, self.enemy.y, 120, 180)
        else:
            Dead.image.clip_composite_draw(left, bottom, width, height, 0, '', self.enemy.x, self.enemy.y, 120, 180)

    def get_bb(self):
        return self.enemy.x - 35, self.enemy.y - 90, self.enemy.x + 35, self.enemy.y + 90

class Enemy:
    def __init__(self, girl):
        self.x, self.y = 1000, 150
        self.frame = 0.0
        self.face_dir = 1
        self.dir = 0
        self.girl = girl
        self.hp = 10

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.WALK = Walk(self)
        self.ATTACK = Attack(self)
        self.HURT = Hurt(self)
        self.DEAD = Dead(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE : {player_in_sight_range: self.RUN, player_in_attack_range: self.ATTACK,
                             hit_by_book: self.HURT, hp_is_zero: self.DEAD},
                self.RUN : {player_in_attack_range: self.ATTACK, player_out_of_range: self.IDLE,
                            hit_by_book: self.HURT, hp_is_zero: self.DEAD},
                self.WALK : {time_out: self.IDLE},
                self.ATTACK : {attack_finished: self.IDLE, hit_by_book: self.HURT, hp_is_zero: self.DEAD},
                self.HURT : {hurt_finished: self.IDLE, hp_is_zero: self.DEAD},
                self.DEAD : {}
            }
        )

    def update(self):
        self.state_machine.update()

        self.x += game_world.scroll_speed * game_framework.frame_time
        self.x += self.dir * RUN_SPEED_PPS * game_framework.frame_time

        canvas_width = 1600
        buffer = canvas_width / 2

        if self.x < (0 - buffer):
            game_world.remove_object(self)
        elif self.x > (canvas_width + buffer):
            game_world.remove_object(self)

    def handle_event(self, event):
        pass


    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.state_machine.get_bb()

    def handle_collision(self, group, other):
        if group == 'book:enemy':
            if self.state_machine.cur_state == self.DEAD:
                return

            game_world.remove_object(other)

            self.hp -= 1
            if self.hp <= 0:
                self.state_machine.handle_state_event(('HP_IS_ZERO', None))
            else:
                self.state_machine.handle_state_event(('HIT_BY_BOOK', None))