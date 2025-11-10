from pico2d import load_image, get_time, load_font, draw_rectangle

import game_world
import game_framework

from state_machine import StateMachine
from fire import Fire

time_out = lambda e: e[0] == 'TIMEOUT'
player_in_sight_range = lambda e: e[0] == 'PLAYER_IN_SIGHT_RANGE'
player_in_attack_range = lambda e: e[0] == 'PLAYER_IN_ATTACK_RANGE'
player_out_of_range = lambda e: e[0] == 'PLAYER_OUT_OF_RANGE'
hit_by_book = lambda e: e[0] == 'HIT_BY_BOOK'
hp_is_zero = lambda e: e[0] == 'HP_IS_ZERO'
attack_finished = time_out
hurt_finished = time_out
dead_finished = time_out

ATTACK_RANGE_PIXELS = 400
SIGHT_RANGE_PIXELS = 600
#MAX_RANGE_PIXELS = 400

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
    sizes = [0, 255, 511, 767, 1024, 1277, 1536]
    def __init__(self, enemy):
        self.enemy = enemy
        if Idle.image == None:
            Idle.image = load_image('./적/남자2(원)/Idle.png')

    def enter(self, e):
        self.enemy.wait_time = get_time()
        self.enemy.dir = 0
        self.enemy.frame = 0.0

    def exit(self, e):
        pass

    def do(self):
        self.enemy.frame = (self.enemy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(
            self.sizes)
        dist_to_player = abs(self.enemy.x - self.enemy.girl.x)
        current_time = get_time()

        if dist_to_player < ATTACK_RANGE_PIXELS and \
                current_time - self.enemy.last_attack_time > self.enemy.attack_cooldown:
            self.enemy.state_machine.handle_state_event(('PLAYER_IN_ATTACK_RANGE', None))
        elif dist_to_player < SIGHT_RANGE_PIXELS:
            self.enemy.state_machine.handle_state_event(('PLAYER_IN_SIGHT_RANGE', None))

    def draw(self):
        left = self.sizes[int(self.enemy.frame)]
        bottom = 0
        width = 50
        height = 105
        if self.enemy.face_dir == -1:
            Idle.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.enemy.x, self.enemy.y, 70 ,180)
        else:
            Idle.image.clip_composite_draw(left, bottom, width, height, 0, '', self.enemy.x, self.enemy.y, 70, 180)

    def get_bb(self):
        return self.enemy.x - 35, self.enemy.y - 90, self.enemy.x + 35, self.enemy.y + 90

class Walk:
    image = None
    sizes = [0, 257, 512, 769, 1018, 1280, 1537, 1794, 2049, 2304]
    def __init__(self, enemy):
        self.enemy = enemy
        if Walk.image == None:
            Walk.image = load_image('./적/남자2(원)/Walk.png')

    def enter(self, e):
        self.enemy.frame = 0.0

    def exit(self, e):
        self.enemy.dir = 0
        game_world.scroll_speed = 0.0

    def do(self):
        dist_to_player = self.enemy.girl.x - self.enemy.x
        current_time = get_time()

        if dist_to_player > 0:
            self.enemy.dir = 1
            self.enemy.face_dir = 1
        elif dist_to_player < 0:
            self.enemy.dir = -1
            self.enemy.face_dir = -1
        else:
            self.enemy.dir = 0

        dist_abs = abs(dist_to_player)

        if dist_abs < ATTACK_RANGE_PIXELS and \
                current_time - self.enemy.last_attack_time > self.enemy.attack_cooldown:
            self.enemy.state_machine.handle_state_event(('PLAYER_IN_ATTACK_RANGE', None))
        elif dist_abs > SIGHT_RANGE_PIXELS:
            self.enemy.state_machine.handle_state_event(('PLAYER_OUT_OF_RANGE', None))

        self.enemy.frame = (self.enemy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(self.sizes)

    def handle_event(self, event):
        pass

    def draw(self):
        left = self.sizes[int(self.enemy.frame)]
        width = 55
        bottom = 0
        height = 106

        if self.enemy.face_dir == -1:
            Walk.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.enemy.x, self.enemy.y,90,180)
        else:
            Walk.image.clip_composite_draw(left, bottom, width, height, 0, '', self.enemy.x, self.enemy.y, 90,180)
    def get_bb(self):
        return self.enemy.x - 35, self.enemy.y - 90, self.enemy.x + 35, self.enemy.y + 90

class Attack:
    image = None
    #sizes = [(0, 50),(257, 47),(518, 48),(773, 90),(1029, 116),
             #(1286, 122),(1541, 129),(1797, 137),(2053,140),(2309,140)]
    sizes = [0, 257, 518, 773, 1029, 1286, 1541, 1797, 2053, 2309]
    def __init__(self, enemy):
        self.enemy = enemy
        if Attack.image == None:
            Attack.image = load_image('./적/남자2(원)/Special_Blow_1.png')

    def enter(self, e):
        self.enemy.dir = 0
        self.enemy.frame = 0.0
        self.enemy.throw_fire()
        self.enemy.last_attack_time = get_time()

    def exit(self, e):
        pass

    def do(self):
        animation_speed = 10.0
        self.enemy.frame = (self.enemy.frame + animation_speed * ACTION_PER_TIME * game_framework.frame_time)

        if self.enemy.frame >= len(self.sizes):
            self.enemy.frame = len(self.sizes) - 1
            self.enemy.state_machine.handle_state_event(('TIMEOUT', None))

    def draw(self):
        left = self.sizes[int(self.enemy.frame)]
        bottom = 0
        width = 140
        height = 100

        if self.enemy.face_dir == -1:
            Attack.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.enemy.x, self.enemy.y, 180, 180)
        else:
            Attack.image.clip_composite_draw(left, bottom, width, height, 0, '', self.enemy.x, self.enemy.y, 180, 180)

    def get_bb(self):
        return self.enemy.x, self.enemy.y - 90, self.enemy.x + 90, self.enemy.y + 90

class Hurt:
    image = None
    sizes =  [(0, 51), (256, 48), (508, 41), (764, 41)]
    def __init__(self, enemy):
        self.enemy = enemy
        if Hurt.image == None:
            Hurt.image = load_image('./적/남자2(원)/Hurt_2.png')

    def enter(self, e):
        self.enemy.dir = 0
        self.enemy.frame = 0.0

    def exit(self, e):
        pass

    def do(self):
        self.enemy.frame = (self.enemy.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)
        total_frames = len(self.sizes)

        if self.enemy.frame >= total_frames:
            self.enemy.frame = total_frames - 1
            self.enemy.state_machine.handle_state_event(('TIMEOUT', None))

    def draw(self):
        left, width = self.sizes[int(self.enemy.frame)]
        bottom = 0
        height = 95

        if self.enemy.face_dir == -1:
            Hurt.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.enemy.x, self.enemy.y, 70, 180)
        else:
            Hurt.image.clip_composite_draw(left, bottom, width, height, 0, '', self.enemy.x, self.enemy.y, 70, 180)

    def get_bb(self):
        return self.enemy.x - 35, self.enemy.y - 90, self.enemy.x + 35, self.enemy.y + 90


class Dead:
    image = None
    sizes =  [(0, 60),(237, 65),(463,89),(751,59),(1005, 67),
              (1239,72),(1454, 100),(1711,91),(1966, 115)]
    def __init__(self, enemy):
        self.enemy = enemy
        if Dead.image == None:
            Dead.image = load_image('./적/남자2(원)/Dead.png')

    def enter(self, e):
        self.enemy.dir = 0
        self.enemy.frame = 0.0
        game_world.remove_collision_object(self.enemy)

        import play_mode
        play_mode.enemies_killed_count += 1

    def exit(self, e):
        pass

    def do(self):
        animation_speed = 4.0
        self.enemy.frame = (self.enemy.frame + animation_speed * ACTION_PER_TIME * game_framework.frame_time)
        total_frames = len(self.sizes)

        if self.enemy.frame >= total_frames:
            self.enemy.frame = total_frames - 1

    def draw(self):
        left, width = self.sizes[int(self.enemy.frame)]
        bottom = 0
        height = 112

        if self.enemy.face_dir == -1:
            Dead.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.enemy.x, self.enemy.y, 100, 180)
        else:
            Dead.image.clip_composite_draw(left, bottom, width, height, 0, '', self.enemy.x, self.enemy.y, 100 , 180)

    def get_bb(self):
        return 0,0,0,0

class Enemy_R:
    font = None
    def __init__(self, girl):
        self.x, self.y = 1300, 150
        self.frame = 0.0
        self.face_dir = 1
        self.dir = 0
        self.girl = girl
        self.hp = 5
        self.last_attack_time = 0.0
        self.attack_cooldown = 2.0

        if Enemy_R.font is None:
            Enemy_R.font = load_font('ENCR10B.TTF', 16)

        self.IDLE = Idle(self)
        self.WALK = Walk(self)
        self.ATTACK = Attack(self)
        self.HURT = Hurt(self)
        self.DEAD = Dead(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {player_in_sight_range: self.WALK, player_in_attack_range: self.ATTACK,
                            hit_by_book: self.HURT, hp_is_zero: self.DEAD},
                self.WALK: {player_in_attack_range: self.ATTACK, player_out_of_range: self.IDLE,
                            hit_by_book: self.HURT, hp_is_zero: self.DEAD},
                self.ATTACK: {attack_finished: self.IDLE, hit_by_book: self.HURT, hp_is_zero: self.DEAD},
                self.HURT: {hurt_finished: self.IDLE, hp_is_zero: self.DEAD},
                self.DEAD: {}
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

    def throw_fire(self):
        fire = Fire(self.x + self.face_dir * 40, self.y + 45, self.face_dir * 10)
        game_world.add_object(fire, 4)
        game_world.add_collision_pair('fire:girl', fire, None)

    def handle_event(self, event):
        pass

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

        if self.state_machine.cur_state != self.DEAD:
            Enemy_R.font.draw(self.x - 30, self.y + 110, f'HP: {self.hp}', (255, 0, 0))

    def get_bb(self):
        return self.state_machine.get_bb()

    def handle_collision(self, group, other):
        if group == 'book:enemy':
            if self.state_machine.cur_state == self.DEAD:
                return

            game_world.remove_object(other)  # Book 제거

            self.hp -= 1
            if self.hp <= 0:
                self.state_machine.handle_state_event(('HP_IS_ZERO', None))
            else:
                self.state_machine.handle_state_event(('HIT_BY_BOOK', None))

        elif group == 'girl:enemy':
            pass