from pico2d import load_image, get_time, load_font, draw_rectangle, clamp
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDL_KEYUP, SDLK_a, SDLK_d, SDLK_e, SDLK_q, SDLK_w, SDLK_LSHIFT

import game_world
import game_framework
import random
import server

from book import Book
from lightning import Lightning
from shield import Shield
from state_machine import StateMachine

def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

time_out = lambda e: e[0] == 'TIMEOUT'
hit_by_enemy = lambda e: e[0] == 'HIT_BY_ENEMY'
time_out_to_idle = lambda e: e[0] == 'TIMEOUT_IDLE'
time_out_to_walk = lambda e: e[0] == 'TIMEOUT_WALK'
hp_is_zero = lambda e: e[0] == 'HP_IS_ZERO'
land_to_idle = lambda e: e[0] == 'LAND_TO_IDLE'
land_to_walk = lambda e: e[0] == 'LAND_TO_WALK'
land_to_run = lambda e: e[0] == 'LAND_TO_RUN'
all_keys_up = lambda e: e[0] == 'ALL_KEYS_UP'


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

def q_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_q

def q_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_q

def w_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_w

def w_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_w

def shift_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LSHIFT

def shift_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LSHIFT

PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 30.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

GRAVITY = 9.8
JUMP_SPEED_MPS = 10.0
JUMP_SPEED_PPS = (JUMP_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 9

DASH_SPEED_KMPH = 50.0
DASH_SPEED_MPM = (DASH_SPEED_KMPH * 1000.0 / 60.0)
DASH_SPEED_MPS = (DASH_SPEED_MPM / 60.0)
DASH_SPEED_PPS = (DASH_SPEED_MPS * PIXEL_PER_METER)



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
        game_world.scroll_speed = 0.0


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
        self.shield_object = None

    def enter(self, e):
        self.girl.dir = 0
        game_world.scroll_speed = 0.0
        self.girl.frame = 0

        self.girl.buff_end_time = get_time() + 5.0 + self.girl.e_duration_bonus

        if self.girl.shield_object is None:
            self.girl.shield_object = Shield(self.girl.x, self.girl.y)
            game_world.add_object(self.girl.shield_object, 5)

    def exit(self, e):
        pass

    def do(self):
        self.girl.frame = (self.girl.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 4

        if self.shield_object:
            self.shield_object.x = self.girl.x - 15
            self.shield_object.y = self.girl.y

        if self.girl.frame >= len(Protection.sizes):
            self.girl.frame = len(Protection.sizes) - 1
            self.girl.state_machine.handle_state_event(('TIMEOUT', None))

    def handle_event(self, event):
        pass

    def draw(self):
        left = Protection.sizes[int(self.girl.frame)]
        bottom = 0
        width = 36
        height = 70
        if self.girl.face_dir == -1:
            Protection.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.girl.x, self.girl.y, 80, 160)
        else:
            Protection.image.clip_composite_draw(left, bottom, width, height, 0, '', self.girl.x, self.girl.y, 80, 160)

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
        self.girl.frame = 0

    def exit(self, e):
        pass

    def do(self):
        speed_mult = 1.0
        if get_time() < self.girl.buffs['speed']['timer']:
            speed_mult = self.girl.buffs['speed']['value']

        if self.girl.key_d_down:
            self.girl.dir = 1
            self.girl.face_dir = 1
        elif self.girl.key_a_down:
            self.girl.dir = -1
            self.girl.face_dir = -1
        else:
            self.girl.dir = 0

        if self.girl.bg_scrolling:
            game_world.scroll_speed = -self.girl.dir * RUN_SPEED_PPS * speed_mult
        else:
            game_world.scroll_speed = 0
            self.girl.x += self.girl.dir * RUN_SPEED_PPS * speed_mult * game_framework.frame_time
            self.girl.x = clamp(25, self.girl.x, 1600 - 25)

        self.girl.frame = (self.girl.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 12


    def draw(self):
        left = Walk.sizes[int(self.girl.frame)]
        bottom = 0
        width = 40
        height = 75
        if self.girl.face_dir == -1:
            Walk.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.girl.x, self.girl.y, 70, 180)
        else:
            Walk.image.clip_composite_draw(left, bottom, width, height, 0, '', self.girl.x, self.girl.y, 70, 180)

    def get_bb(self):
        return self.girl.x - 40, self.girl.y - 90, self.girl.x + 40, self.girl.y + 90

class Run:
    image = None
    sizes = [(0, 47), (93, 50), (188, 59), (291, 51), (389, 38), (487, 38)]
    def __init__(self, girl):
        self.girl = girl
        if Run.image == None:
            Run.image = load_image('./주인공/Run.png')

    def enter(self, e):
        self.girl.frame = 0

    def exit(self, e):
        pass

    def do(self):
        animation_speed = 7.0
        speed_mult = 1.0
        if get_time() < self.girl.buffs['speed']['timer']:
            speed_mult = self.girl.buffs['speed']['value']

        if self.girl.key_d_down:
            self.girl.dir = 1
            self.girl.face_dir = 1
        elif self.girl.key_a_down:
            self.girl.dir = -1
            self.girl.face_dir = -1
        else:
            self.girl.dir = 0

        if self.girl.bg_scrolling:
            game_world.scroll_speed = -self.girl.dir * DASH_SPEED_PPS * speed_mult
        else:
            game_world.scroll_speed = 0
            self.girl.x += self.girl.dir * DASH_SPEED_PPS * speed_mult * game_framework.frame_time
            self.girl.x = clamp(25, self.girl.x, 1600 - 25)

        self.girl.frame = (self.girl.frame + animation_speed * ACTION_PER_TIME * game_framework.frame_time) % 6

    def draw(self):
        left, width = Run.sizes[int(self.girl.frame)]
        bottom = 0
        height = 81
        if self.girl.face_dir == -1:
            Run.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.girl.x, self.girl.y, 90, 180)
        else:
            Run.image.clip_composite_draw(left, bottom, width, height, 0, '', self.girl.x, self.girl.y, 90, 180)

    def get_bb(self):
        return self.girl.x - 45, self.girl.y - 90, self.girl.x + 45, self.girl.y + 90

class Attack:
    image = None
    sizes = [(7, 40), (131, 43), (253, 51), (378, 59), (503, 61), (645, 62), (776, 73), (905, 37)]
    def __init__(self, girl):
        self.girl = girl
        if Attack.image == None:
            Attack.image = load_image('./주인공/Attack.png')

    def enter(self, e):
        self.girl.throw_book()
        self.girl.frame = 0.0
        self.girl.dir = 0
        game_world.scroll_speed = 0.0
        self.girl.last_attack_time = get_time()

    def exit(self, e):
        pass

    def do(self):
        self.girl.frame = (self.girl.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)

        if self.girl.frame >= len(Attack.sizes):
            self.girl.frame = len(Attack.sizes) - 1
            self.girl.state_machine.handle_state_event(('TIMEOUT', None))

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

class Hurt:
    image = None
    sizes = [(0, 51), (123, 61), (254, 65)]
    def __init__(self, girl):
        self.girl = girl
        if Hurt.image == None:
            Hurt.image = load_image('./주인공/Hurt.png')

    def enter(self, e):
        self.girl.frame = 0.0

    def exit(self, e):
        pass

    def do(self):
        animation_speed = 5.0
        self.girl.frame = (self.girl.frame + animation_speed * ACTION_PER_TIME * game_framework.frame_time)

        if self.girl.key_d_down:
            self.girl.dir = 1
            self.girl.face_dir = 1
        elif self.girl.key_a_down:
            self.girl.dir = -1
            self.girl.face_dir = -1
        else:
            self.girl.dir = 0

        if self.girl.bg_scrolling:
            game_world.scroll_speed = -self.girl.dir * RUN_SPEED_PPS
        else:
            game_world.scroll_speed = 0
            self.girl.x += self.girl.dir * RUN_SPEED_PPS * game_framework.frame_time
            self.girl.x = clamp(25, self.girl.x, 1600 - 25)

        if self.girl.frame >= len(Hurt.sizes):
            self.girl.frame = len(Hurt.sizes) - 1

            if self.girl.dir == 0:
                self.girl.state_machine.handle_state_event(('TIMEOUT_IDLE', None))
            else:
                self.girl.state_machine.handle_state_event(('TIMEOUT_WALK', None))

    def draw(self):
        left, width = Hurt.sizes[int(self.girl.frame)]
        bottom = 0
        height = 90
        if self.girl.face_dir == -1:
            Hurt.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.girl.x, self.girl.y, 65, 180)
        else:
            Hurt.image.clip_composite_draw(left, bottom, width, height, 0, '', self.girl.x, self.girl.y, 65, 180)

    def get_bb(self):
        return self.girl.x - 55, self.girl.y - 90, self.girl.x + 55, self.girl.y + 90

class Dead:
    image = None
    sizes = [(0, 30), (127, 31), (258, 57), (387, 70), (515, 70)]

    def __init__(self, girl):
        self.girl = girl
        if Dead.image == None:
            Dead.image = load_image('./주인공/Dead.png')

        self.gameover_timer = 0.0

    def enter(self, e):
        self.girl.frame = 0.0
        self.girl.dir = 0
        game_world.scroll_speed = 0.0
        game_world.remove_collision_object(self.girl)
        self.gameover_timer = 0.0

    def exit(self, e):
        pass

    def do(self):
        animation_speed = 4.0
        self.girl.frame = (self.girl.frame + animation_speed * ACTION_PER_TIME * game_framework.frame_time)
        total_frames = len(Dead.sizes)

        if self.girl.frame >= total_frames:
            self.girl.frame = total_frames - 1 

            if self.gameover_timer == 0.0:
                self.gameover_timer = get_time()


            if get_time() - self.gameover_timer > 0.5:
                import gameover_mode
                game_framework.change_mode(gameover_mode)

    def draw(self):
        left, width = Dead.sizes[int(self.girl.frame)]
        bottom = 0
        height = 80
        if self.girl.face_dir == -1:
            Dead.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.girl.x, self.girl.y, 100, 180)
        else:
            Dead.image.clip_composite_draw(left, bottom, width, height, 0, '', self.girl.x, self.girl.y, 100, 180)

    def get_bb(self):
        return 0, 0, 0, 0

class Skill:
    image = None
    sizes = [0, 91, 181, 269]

    def __init__(self, girl):
        self.girl = girl
        if Skill.image == None:
            Skill.image = load_image('./주인공/Skill.png')

    def enter(self, e):
        self.girl.last_skill_time = get_time()
        self.girl.frame = 0.0
        game_world.scroll_speed = 0.0
        base_y = 230
        min_distance = 20

        base_tick_damage = 2
        dmg_bonus = self.girl.q_damage_bonus

        if hasattr(self.girl, 'buffs') and 'q_buff' in self.girl.buffs:
            if get_time() < self.girl.buffs['q_buff']['timer']:
                dmg_bonus += self.girl.buffs['q_buff']['value']

        final_tick_damage = base_tick_damage + dmg_bonus

        offsets = []
        for _ in range(4):
            offsets.append(random.randint(100, 400))
        offsets.sort()

        final_x_positions = []
        last_x = None

        for offset in offsets:
            current_x = self.girl.x + (offset * self.girl.face_dir)

            if last_x is not None:
                if abs(current_x - last_x) < min_distance:
                    current_x = last_x + (min_distance * self.girl.face_dir)

            final_x_positions.append(current_x)
            last_x = current_x

        for x_pos in final_x_positions:
            lightning = Lightning(x_pos, base_y, final_tick_damage)
            game_world.add_object(lightning, 4)
            game_world.add_collision_pair('lightning:enemy', lightning, None)


    def exit(self, e):
        pass

    def do(self):
        animation_speed = 5.0
        self.girl.frame = (self.girl.frame + animation_speed * ACTION_PER_TIME * game_framework.frame_time)

        if self.girl.frame >= len(Skill.sizes):
            self.girl.frame = len(Skill.sizes) - 1
            self.girl.state_machine.handle_state_event(('TIMEOUT', None))

    def draw(self):
        left = Skill.sizes[int(self.girl.frame)]
        bottom = 0
        width = 61
        height = 68
        if self.girl.face_dir == -1:
            Skill.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.girl.x, self.girl.y, 130, 170)
        else:
            Skill.image.clip_composite_draw(left, bottom, width, height, 0, '', self.girl.x, self.girl.y, 130, 170)

    def get_bb(self):
        return self.girl.x - 65, self.girl.y - 85, self.girl.x + 65, self.girl.y + 85


class Jump:
    image = None
    sizes = [0, 88, 180, 275, 362, 457, 557, 650 ]

    def __init__(self, girl):
        self.girl = girl
        if Jump.image == None:
            Jump.image = load_image('./주인공/Jump.png')

    def enter(self, e):
        self.girl.frame = 0.0
        self.girl.y_velocity = JUMP_SPEED_PPS

    def exit(self, e):
        self.girl.y_velocity = 0

    def do(self):
        animation_speed = 3.0
        self.girl.y_velocity -= GRAVITY * PIXEL_PER_METER * game_framework.frame_time
        self.girl.y += self.girl.y_velocity * game_framework.frame_time

        if self.girl.key_d_down:
            self.girl.dir = 1
            self.girl.face_dir = 1
        elif self.girl.key_a_down:
            self.girl.dir = -1
            self.girl.face_dir = -1
        else:
            self.girl.dir = 0

        if self.girl.bg_scrolling:
            game_world.scroll_speed = -self.girl.dir * RUN_SPEED_PPS
        else:
            game_world.scroll_speed = 0
            self.girl.x += self.girl.dir * RUN_SPEED_PPS * game_framework.frame_time
            self.girl.x = clamp(25, self.girl.x, 1600 - 25)

        self.girl.frame = (self.girl.frame + animation_speed * ACTION_PER_TIME * game_framework.frame_time) % 8

        if self.girl.y <= 150:
            self.girl.y = 150
            self.girl.y_velocity = 0

            if self.girl.key_shift_down and self.girl.dir != 0:
                self.girl.state_machine.handle_state_event(('LAND_TO_RUN', None))
            elif self.girl.dir == 0:
                self.girl.state_machine.handle_state_event(('LAND_TO_IDLE', None))
            else:
                self.girl.state_machine.handle_state_event(('LAND_TO_WALK', None))

    def draw(self):
        left = Jump.sizes[int(self.girl.frame)]
        width = 50
        bottom = 0
        height = 102

        if self.girl.face_dir == -1:
            Jump.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.girl.x, self.girl.y, 100, 200)
        else:
            Jump.image.clip_composite_draw(left, bottom, width, height, 0, '', self.girl.x, self.girl.y, 100, 200)

    def get_bb(self):
        return self.girl.x - 50, self.girl.y - 80, self.girl.x + 50, self.girl.y + 80

class Girl:
    def __init__(self):
        self.x, self.y = 100, 150
        self.ground_y = 150
        self.frame = 0.0
        self.face_dir = 1
        self.dir = 0
        self.y_velocity = 0.0

        self.level = 1
        self.exp = 0
        self.max_exp = 100
        self.max_hp = 100
        self.hp = self.max_hp
        self.damage = 1
        self.attack_range = 450.0

        self.last_attack_time = 0.0
        self.attack_cooldown = 0.5
        self.last_hit_time = 0.0
        self.hit_cooldown = 0.5

        self.key_a_down = False
        self.key_d_down = False

        self.key_shift_down = False

        self.skill_cooldown = 5.0
        self.last_skill_time = -self.skill_cooldown

        self.skill_e_cooldown = 10.0
        self.last_skill_e_time = -self.skill_e_cooldown
        self.buff_end_time = 0.0
        self.shield_object = None

        self.q_damage_bonus = 0
        self.e_duration_bonus = 0.0

        self.buffs = {
            'regen': {'timer': 0, 'value': 0},
            'speed': {'timer': 0, 'value': 1.0},
            'q_buff': {'timer': 0, 'value': 0},
            'defense': {'timer': 0, 'value': 1.0}
        }
        self.regen_tick = 0.0

        self.bg_scrolling = True

        self.inventory = []
        self.level_up_image = load_image('./UI/레벨업.png')
        self.level_up_end_time = 0.0

        self.IDLE = Idle(self)
        self.PROTECTION = Protection(self)
        self.WALK = Walk(self)
        self.ATTACK = Attack(self)
        self.HURT = Hurt(self)
        self.DEAD = Dead(self)
        self.SKILL = Skill(self)
        self.JUMP = Jump(self)
        self.RUN = Run(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.PROTECTION : {e_up: self.IDLE, hit_by_enemy: self.HURT, hp_is_zero: self.DEAD,w_down: self.JUMP,
                                   left_down: self.WALK, right_down: self.WALK, space_down: self.ATTACK, q_down : self.SKILL,
                                   shift_down: self.RUN},
                self.IDLE : {space_down: self.ATTACK, right_down: self.WALK, left_down: self.WALK, w_down: self.JUMP
                             , left_up: self.WALK, right_up : self.WALK , e_down: self.PROTECTION, hit_by_enemy: self.HURT,
                             hp_is_zero: self.DEAD, q_down : self.SKILL, shift_down: self.IDLE},
                self.WALK : {space_down: self.ATTACK, w_down: self.JUMP, e_down: self.PROTECTION, hit_by_enemy: self.HURT,
                             hp_is_zero: self.DEAD, q_down : self.SKILL, shift_down: self.RUN, all_keys_up: self.IDLE,
                             right_up: self.WALK,left_up: self.WALK,right_down: self.WALK, left_down: self.WALK},
                self.ATTACK : {time_out: self.IDLE, e_down: self.PROTECTION, space_down: self.ATTACK, w_down: self.JUMP,
                               right_down: self.WALK, left_down: self.WALK, hit_by_enemy: self.HURT,
                               hp_is_zero: self.DEAD, q_down : self.SKILL, shift_down: self.RUN},
                self.HURT: { time_out_to_idle: self.IDLE, time_out_to_walk: self.WALK, space_down: self.ATTACK, w_down: self.JUMP,
                             e_down: self.PROTECTION, hp_is_zero: self.DEAD, right_down: self.WALK, left_down: self.WALK,
                             q_down : self.SKILL, shift_down: self.RUN},
                self.DEAD : {},
                self.SKILL : {hit_by_enemy: self.HURT, hp_is_zero: self.DEAD, left_down: self.WALK, right_down: self.WALK,
                                space_down: self.ATTACK, time_out: self.IDLE,  e_down: self.PROTECTION, w_down: self.JUMP,
                              shift_down: self.RUN},
                self.JUMP : {land_to_idle: self.IDLE, land_to_walk: self.WALK, hit_by_enemy: self.HURT,
                              hp_is_zero: self.DEAD, space_down: self.ATTACK, q_down: self.SKILL, e_down: self.PROTECTION,
                             land_to_run: self.RUN},
                self.RUN : { shift_up: self.WALK, space_down: self.ATTACK,w_down: self.JUMP, e_down: self.PROTECTION,
                             hit_by_enemy: self.HURT, hp_is_zero: self.DEAD, q_down : self.SKILL, right_up: self.RUN,
                             left_up: self.RUN, all_keys_up: self.IDLE}
            }
        )

    def activate_buff(self, name, value, duration):
        self.buffs[name]['timer'] = get_time() + duration
        self.buffs[name]['value'] = value
        print(f"버프 활성화: {name} (수치:{value}, 시간:{duration}초)")

    def gain_exp(self, amount):
        self.exp += amount
        print(f"Exp: {self.exp}/{self.max_exp}")

        while self.exp >= self.max_exp:
            self.exp -= self.max_exp
            self.level += 1
            self.max_exp = int(self.max_exp * 1.5)

            self.max_hp += 20
            self.hp = self.max_hp
            self.damage += 5
            print(f"Level Up! Lv.{self.level} HP:{self.max_hp} Dmg:{self.damage}")

            self.level_up_end_time = get_time() + 2.0

    def update(self):
        self.state_machine.update()
        current_time = get_time()
        if current_time < self.buffs['regen']['timer']:
            if current_time - self.regen_tick > 1.0:  # 1초마다
                self.hp += self.buffs['regen']['value']
                if self.hp > self.max_hp: self.hp = self.max_hp
                self.regen_tick = current_time
                print("체력 자동 회복중...")

        if self.y > self.ground_y:
            self.y_velocity -= GRAVITY * PIXEL_PER_METER * game_framework.frame_time
            self.y += self.y_velocity * game_framework.frame_time
        if self.state_machine.cur_state != self.JUMP and self.y <= 150:
            self.y = self.ground_y
            self.y_velocity = 0

        current_time = get_time()

        if self.shield_object:
            if current_time > self.buff_end_time:
                self.shield_object.deactivate()
                self.shield_object = None

                self.last_skill_e_time = current_time
            else:
                if self.state_machine.cur_state != self.PROTECTION:
                    self.shield_object.x = self.x
                    self.shield_object.y = self.y

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_a:
                self.key_a_down = True
            elif event.key == SDLK_d:
                self.key_d_down = True
            elif event.key == SDLK_LSHIFT:
                self.key_shift_down = True

            elif event.key == SDLK_SPACE:
                current_time = get_time()
                if current_time - self.last_attack_time < self.attack_cooldown:
                    return

            elif event.key == SDLK_q:
                current_time = get_time()
                if current_time - self.last_skill_time < self.skill_cooldown:
                    return

            elif event.key == SDLK_e:
                current_time = get_time()
                if current_time - self.last_skill_e_time < self.skill_e_cooldown:
                    return

            elif event.key == SDLK_w:
                pass

            self.state_machine.handle_state_event(('INPUT', event))
            pass

        elif event.type == SDL_KEYUP:
            if event.key == SDLK_a:
                self.key_a_down = False
            elif event.key == SDLK_d:
                self.key_d_down = False
            elif event.key == SDLK_LSHIFT:
                self.key_shift_down = False

            if (event.key == SDLK_a or event.key == SDLK_d):
                if not self.key_a_down and not self.key_d_down:
                    self.state_machine.handle_state_event(('ALL_KEYS_UP', None))
                else:
                    self.state_machine.handle_state_event(('INPUT', event))
            else:
                self.state_machine.handle_state_event(('INPUT', event))

            pass

    def throw_book(self):
        book = Book(self.x + self.face_dir*40, self.y+20, self.face_dir * 15, 0, self.damage, self.attack_range)
        game_world.add_object(book, 4)
        game_world.add_collision_pair('book:enemy', book, None)

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

        if get_time() < self.level_up_end_time:
            self.level_up_image.draw(self.x, self.y + 140, 96, 17)

    def get_bb(self):
        return self.state_machine.get_bb()

    def handle_collision(self, group, other):
        current_time = get_time()

        if group == 'girl:coin':
            import play_mode
            server.coin_count += other.value
            return

        elif group == 'girl:food':
            self.hp += other.value
            if self.hp > 100:
                self.hp = self.max_hp
            return

        if current_time < self.buff_end_time:
            return

        if current_time - self.last_hit_time < self.hit_cooldown:
            return

        if group == 'girl:enemy' or group == 'fire:girl':
            if self.state_machine.cur_state == self.DEAD:
                return

            dmg_multiplier = 1.0
            if get_time() < self.buffs['defense']['timer']:
                dmg_multiplier = self.buffs['defense']['value']

            damage = 10 * dmg_multiplier
            self.hp -= damage

            self.last_hit_time = current_time

            if self.hp <= 0:
                self.hp = 0
                self.state_machine.handle_state_event(('HP_IS_ZERO', None))
            else:
                self.state_machine.handle_state_event(('HIT_BY_ENEMY', None))