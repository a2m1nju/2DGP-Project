from pico2d import *
import random
import game_framework
import game_world
import server

from state_machine import StateMachine
from coin import Coin
from food import Food

PIXEL_PER_METER = (10.0 / 0.3)
RUN_SPEED_KMPH = 15.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 9

time_out = lambda e: e[0] == 'TIMEOUT'
player_in_sight_range = lambda e: e[0] == 'PLAYER_IN_SIGHT_RANGE'
player_in_attack_range = lambda e: e[0] == 'PLAYER_IN_ATTACK_RANGE'
player_out_of_range = lambda e: e[0] == 'PLAYER_OUT_OF_RANGE'
hit_by_book = lambda e: e[0] == 'HIT_BY_BOOK'
hp_is_zero = lambda e: e[0] == 'HP_IS_ZERO'
attack_finished = time_out
hurt_finished = time_out
dead_finished = time_out

ZOMBIE_ANIMATION_DATA = {
    1: {  # 좀비 1
        'Idle': [(0, 0, 34, 68), (92, 0, 34, 68), (187, 0, 34, 68), (284, 0, 34, 68), (382, 0, 34, 68),
                 (480, 0, 34, 68), (577, 0, 34, 68), (672, 0, 34, 68)],
        'Run': [(0, 0, 67, 62), (91, 0, 67, 62), (181, 0, 67, 62), (282, 0, 67, 62), (381, 0, 67, 62),
                (473, 0, 67, 62), (574, 0, 67, 62)],
        'Walk': [(0, 0, 33, 65), (100, 0, 33, 65), (195, 0, 33, 65), (290, 0, 33, 65), (383, 0, 33, 65),
                 (485, 0, 33, 65), (581, 0, 33, 65), (674, 0, 33, 65)],
        'Attack': [(0, 0, 63, 73), (96, 0, 63, 73), (196, 0, 63, 73), (296, 0, 63, 73), (393, 0, 63, 73)],
        'Hurt': [(0, 0, 41, 62), (95, 0, 41, 62), (200, 0, 41, 62)],
        'Dead': [(0, 0, 43, 63), (99, 0, 38, 63), (197, 0, 30, 63), (294, 0, 71, 53), (389, 0, 71, 67)]
    },
    2: {  # 좀비 2
        'Idle': [(0, 0, 23, 66), (94, 0, 23, 66), (189, 0, 23, 66), (286, 0, 23, 66), (383, 0, 23, 66)],
        'Run': [(0, 0, 62, 66), (96, 0, 62, 66), (192, 0, 62, 66), (286, 0, 62, 66), (385, 0, 62, 66),
                (480, 0, 62, 66), (577, 0, 62, 66)],
        'Walk': [(0, 0, 44, 66), (95, 0, 44, 66), (192, 0, 44, 66), (288, 0, 44, 66), (384, 0, 44, 66),
                 (480, 0, 44, 66), (576, 0, 44, 66)],
        'Attack': [(0, 0, 54, 64), (95, 0, 54, 64), (191, 0, 54, 64), (287, 0, 54, 64)],
        'Hurt': [(0, 0, 44, 60), (88, 0, 44, 60), (190, 0, 44, 60)],
        'Dead': [(0, 0, 39, 52), (96, 0, 38, 52), (191, 0, 40, 52), (282, 0, 53, 52), (363, 0, 67, 52)]
    },
    3: {  # 좀비 3
        'Idle': [(0, 0, 40, 70), (128, 0, 40, 70), (255, 0, 40, 70), (381, 0, 40, 70), (509, 0, 40, 70),
                 (638, 0, 40, 70)],
        'Walk': [(0, 0, 55, 70), (130, 0, 55, 70), (255, 0, 55, 70), (379, 0, 55, 70), (507, 0, 55, 70),
                 (638, 0, 55, 70), (765, 0, 55, 70), (899, 0, 55, 70), (1024, 0, 55, 70), (1151, 0, 55, 70)],
        'Run': [],
        'Attack': [(0, 0, 51, 70), (123, 0, 51, 70), (255, 0, 51, 70), (384, 0, 51, 70), (513, 0, 51, 70)],
        'Hurt': [(0, 0, 53, 70), (128, 0, 53, 70), (251, 0, 53, 70), (373, 0, 53, 70)],
        'Dead': [(0, 0, 35, 70), (130, 0, 36, 70), (258, 0, 38, 70), (385, 0, 64, 70), (513, 0, 68, 70)]
    },
    4: {  # 좀비 4
        'Idle': [(2, 0, 40, 72), (127, 0, 40, 72), (256, 0, 40, 72), (384, 0, 40, 72), (512, 0, 40, 72),
                 (639, 0, 40, 72)],
        'Walk': [(0, 0, 65, 71), (125, 0, 65, 71), (250, 0, 65, 71), (375, 0, 65, 71), (508, 0, 65, 71),
                 (640, 0, 65, 71), (768, 0, 65, 71), (888, 0, 65, 71), (1017, 0, 65, 71), (1148, 0, 65, 71)],
        'Run': [],
        'Attack': [(0, 0, 60, 76), (121, 0, 60, 76), (252, 0, 60, 76), (389, 0, 60, 76), (516, 0, 60, 76)],
        'Hurt': [(0, 0, 62, 69), (121, 0, 62, 69), (245, 0, 62, 69), (369, 0, 62, 69)],
        'Dead': [(0, 0, 47, 62), (123, 0, 45, 62), (241, 0, 53, 62), (372, 0, 52, 62), (490, 0, 61, 62)]
    }
}

ZOMBIE_BB_SIZE = {
    1: (35, 90),
    2: (40, 95),
    3: (45, 100),
    4: (50, 105)
}

ZOMBIE_DRAW_CONFIG = {
    1: {'scale': 1.0, 'dy': 0},
    2: {'scale': 1.0, 'dy': 0},
    3: {'scale': 1.0, 'dy': 0},
    4: {'scale': 1.0, 'dy': 0}
}


class ZombieIdle:
    def __init__(self, zombie):
        self.zombie = zombie
        self.image = load_image(f'./적/좀비{zombie.type}(근)/Idle.png')
        self.frames = ZOMBIE_ANIMATION_DATA[zombie.type]['Idle']

    def enter(self, e):
        self.zombie.wait_time = get_time()
        self.zombie.dir = 0
        self.zombie.frame = 0.0

    def do(self):
        self.zombie.frame = (self.zombie.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(
            self.frames)
        dist_to_player = abs(self.zombie.x - self.zombie.girl.x)

        if dist_to_player < 110:
            self.zombie.state_machine.handle_state_event(('PLAYER_IN_ATTACK_RANGE', None))
        elif dist_to_player < 900:
            self.zombie.state_machine.handle_state_event(('PLAYER_IN_SIGHT_RANGE', None))
        elif get_time() - self.zombie.wait_time > 3:
            self.zombie.state_machine.handle_state_event(('TIMEOUT', None))

    def exit(self, e):
        pass

    def draw(self):
        idx = int(self.zombie.frame) % len(self.frames)
        left, bottom, width, height = self.frames[idx]

        cfg = ZOMBIE_DRAW_CONFIG[self.zombie.type]
        dst_w = width * 2.5 * cfg['scale']
        dst_h = height * 2.5 * cfg['scale']
        dst_y = self.zombie.y + cfg['dy']

        if self.zombie.face_dir == -1:
            self.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.zombie.x, dst_y, dst_w, dst_h)
        else:
            self.image.clip_composite_draw(left, bottom, width, height, 0, '', self.zombie.x, dst_y, dst_w, dst_h)

    def get_bb(self):
        bb_w, bb_h = ZOMBIE_BB_SIZE[self.zombie.type]
        return self.zombie.x - bb_w, self.zombie.y - bb_h, self.zombie.x + bb_w, self.zombie.y + bb_h


class ZombieRun:
    def __init__(self, zombie):
        self.zombie = zombie

        run_frames = ZOMBIE_ANIMATION_DATA[zombie.type].get('Run', [])

        if not run_frames:
            self.frames = ZOMBIE_ANIMATION_DATA[zombie.type]['Walk']
            self.image = load_image(f'./적/좀비{zombie.type}(근)/Walk.png')
        else:
            self.frames = run_frames
            self.image = load_image(f'./적/좀비{zombie.type}(근)/Run.png')

    def enter(self, e):
        self.zombie.frame = 0.0

    def do(self):
        dist_to_player = self.zombie.girl.x - self.zombie.x
        if dist_to_player > 0:
            self.zombie.dir = 1
            self.zombie.face_dir = 1
        elif dist_to_player < 0:
            self.zombie.dir = -1
            self.zombie.face_dir = -1
        else:
            self.zombie.dir = 0

        dist_abs = abs(dist_to_player)
        if dist_abs < 110:
            self.zombie.state_machine.handle_state_event(('PLAYER_IN_ATTACK_RANGE', None))
        elif dist_abs > 900:
            self.zombie.state_machine.handle_state_event(('PLAYER_OUT_OF_RANGE', None))

        self.zombie.frame = (self.zombie.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(
            self.frames)

    def exit(self, e):
        pass

    def draw(self):
        idx = int(self.zombie.frame) % len(self.frames)
        left, bottom, width, height = self.frames[idx]

        cfg = ZOMBIE_DRAW_CONFIG[self.zombie.type]
        dst_w = width * 2.5 * cfg['scale']
        dst_h = height * 2.5 * cfg['scale']
        dst_y = self.zombie.y + cfg['dy']

        if self.zombie.face_dir == -1:
            self.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.zombie.x, dst_y, dst_w, dst_h)
        else:
            self.image.clip_composite_draw(left, bottom, width, height, 0, '', self.zombie.x, dst_y, dst_w, dst_h)

    def get_bb(self):
        bb_w, bb_h = ZOMBIE_BB_SIZE[self.zombie.type]
        # Run 상태일 때 BB를 조금 다르게 하고 싶다면 여기서 조정
        return self.zombie.x - (bb_w + 10), self.zombie.y - bb_h, self.zombie.x + (bb_w + 10), self.zombie.y + bb_h


class ZombieWalk:
    def __init__(self, zombie):
        self.zombie = zombie
        self.image = load_image(f'./적/좀비{zombie.type}(근)/Walk.png')
        self.frames = ZOMBIE_ANIMATION_DATA[zombie.type]['Walk']

    def enter(self, e):
        self.zombie.dir = 1
        self.zombie.frame = 0.0

    def do(self):
        dist_to_player = self.zombie.girl.x - self.zombie.x
        if dist_to_player > 0:
            self.zombie.dir = 1
            self.zombie.face_dir = 1
        elif dist_to_player < 0:
            self.zombie.dir = -1
            self.zombie.face_dir = -1
        else:
            self.zombie.dir = 0

        dist_abs = abs(dist_to_player)
        if dist_abs < 110:
            self.zombie.state_machine.handle_state_event(('PLAYER_IN_ATTACK_RANGE', None))
        elif dist_abs > 900:
            self.zombie.state_machine.handle_state_event(('PLAYER_OUT_OF_RANGE', None))

        self.zombie.frame = (self.zombie.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(
            self.frames)

    def exit(self, e):
        pass

    def draw(self):
        idx = int(self.zombie.frame) % len(self.frames)
        left, bottom, width, height = self.frames[idx]

        cfg = ZOMBIE_DRAW_CONFIG[self.zombie.type]
        dst_w = width * 2.5 * cfg['scale']
        dst_h = height * 2.5 * cfg['scale']
        dst_y = self.zombie.y + cfg['dy']

        if self.zombie.face_dir == -1:
            self.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.zombie.x, dst_y, dst_w, dst_h)
        else:
            self.image.clip_composite_draw(left, bottom, width, height, 0, '', self.zombie.x, dst_y, dst_w, dst_h)

    def get_bb(self):
        bb_w, bb_h = ZOMBIE_BB_SIZE[self.zombie.type]
        return self.zombie.x - bb_w, self.zombie.y - bb_h, self.zombie.x + bb_w, self.zombie.y + bb_h


class ZombieAttack:
    attack_sound = None

    def __init__(self, zombie):
        self.zombie = zombie
        filename = 'Attack.png'
        if zombie.type == 1:
            filename = 'Attack_1.png'
        elif zombie.type == 2:
            filename = 'Attack_2.png'

        self.image = load_image(f'./적/좀비{zombie.type}(근)/{filename}')
        self.frames = ZOMBIE_ANIMATION_DATA[zombie.type]['Attack']

        if ZombieAttack.attack_sound is None:
            ZombieAttack.attack_sound = load_wav('./음악/펀치.mp3')
            ZombieAttack.attack_sound.set_volume(20)

    def enter(self, e):
        self.zombie.dir = 0
        self.zombie.frame = 0.0

        if ZombieAttack.attack_sound:
            ZombieAttack.attack_sound.play()

    def do(self):
        animation_speed = 7.0
        self.zombie.frame = (self.zombie.frame + animation_speed * ACTION_PER_TIME * game_framework.frame_time)
        if self.zombie.frame >= len(self.frames):
            self.zombie.frame = len(self.frames) - 1
            self.zombie.state_machine.handle_state_event(('TIMEOUT', None))

    def exit(self, e):
        pass

    def draw(self):
        idx = int(self.zombie.frame)
        if idx >= len(self.frames): idx = len(self.frames) - 1
        left, bottom, width, height = self.frames[idx]

        cfg = ZOMBIE_DRAW_CONFIG[self.zombie.type]
        dst_w = width * 2.5 * cfg['scale']
        dst_h = height * 2.5 * cfg['scale']
        dst_y = self.zombie.y + 10 + cfg['dy']

        if self.zombie.face_dir == -1:
            self.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.zombie.x, dst_y, dst_w, dst_h)
        else:
            self.image.clip_composite_draw(left, bottom, width, height, 0, '', self.zombie.x, dst_y, dst_w, dst_h)

    def get_bb(self):
        bb_w, bb_h = ZOMBIE_BB_SIZE[self.zombie.type]
        expand_w = 35
        if self.zombie.type == 3:
            expand_w = 30
        return self.zombie.x - (bb_w + expand_w), self.zombie.y - bb_h, self.zombie.x + (bb_w + expand_w), self.zombie.y + bb_h


class ZombieHurt:
    def __init__(self, zombie):
        self.zombie = zombie
        self.image = load_image(f'./적/좀비{zombie.type}(근)/Hurt.png')
        self.frames = ZOMBIE_ANIMATION_DATA[zombie.type]['Hurt']

    def enter(self, e):
        self.zombie.dir = 0
        self.zombie.frame = 0.0

    def do(self):
        self.zombie.frame = (self.zombie.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)
        if self.zombie.frame >= len(self.frames):
            self.zombie.frame = len(self.frames) - 1
            self.zombie.state_machine.handle_state_event(('TIMEOUT', None))

    def exit(self, e):
        pass

    def draw(self):
        idx = int(self.zombie.frame)
        if idx >= len(self.frames): idx = len(self.frames) - 1
        left, bottom, width, height = self.frames[idx]

        cfg = ZOMBIE_DRAW_CONFIG[self.zombie.type]
        dst_w = width * 2.5 * cfg['scale']
        dst_h = height * 2.5 * cfg['scale']
        dst_y = self.zombie.y + cfg['dy']

        if self.zombie.face_dir == -1:
            self.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.zombie.x, dst_y, dst_w, dst_h)
        else:
            self.image.clip_composite_draw(left, bottom, width, height, 0, '', self.zombie.x, dst_y, dst_w, dst_h)

    def get_bb(self):
        bb_w, bb_h = ZOMBIE_BB_SIZE[self.zombie.type]
        return self.zombie.x - bb_w, self.zombie.y - bb_h, self.zombie.x + bb_w, self.zombie.y + bb_h


class ZombieDead:
    def __init__(self, zombie):
        self.zombie = zombie
        self.image = load_image(f'./적/좀비{zombie.type}(근)/Dead.png')
        self.frames = ZOMBIE_ANIMATION_DATA[zombie.type]['Dead']

    def enter(self, e):
        self.zombie.dir = 0
        self.zombie.frame = 0.0
        game_world.remove_collision_object(self.zombie)

        server.enemies_killed_count += 1
        self.zombie.girl.gain_exp(20)

        if random.random() < 0.9:
            coin_value = random.choice([10, 20, 30])
            coin = Coin(self.zombie.x, self.zombie.y + 30, coin_value)
            game_world.add_object(coin, 3)
            game_world.add_collision_pair('girl:coin', None, coin)
        else:
            food_item = Food(self.zombie.x, self.zombie.y + 30)
            game_world.add_object(food_item, 3)
            game_world.add_collision_pair('girl:food', None, food_item)

    def exit(self, e):
        pass

    def do(self):
        animation_speed = 4.0
        self.zombie.frame = (self.zombie.frame + animation_speed * ACTION_PER_TIME * game_framework.frame_time)
        if self.zombie.frame >= len(self.frames):
            self.zombie.frame = len(self.frames) - 1

    def draw(self):
        idx = int(self.zombie.frame)
        if idx >= len(self.frames): idx = len(self.frames) - 1
        left, bottom, width, height = self.frames[idx]

        cfg = ZOMBIE_DRAW_CONFIG[self.zombie.type]
        dst_w = width * 2.5 * cfg['scale']
        dst_h = height * 2.5 * cfg['scale']
        dst_y = self.zombie.y + cfg['dy']

        if self.zombie.face_dir == -1:
            self.image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.zombie.x, dst_y, dst_w, dst_h)
        else:
            self.image.clip_composite_draw(left, bottom, width, height, 0, '', self.zombie.x, dst_y, dst_w, dst_h)

    def get_bb(self):
        return 0, 0, 0, 0


class Zombie:
    font = None
    hp_bar_bg = None
    hp_bar_fill = None

    def __init__(self, girl, type=1):
        self.x, self.y = 1000, 150
        self.frame = 0.0
        self.face_dir = 1
        self.dir = 0
        self.girl = girl
        self.type = type

        if self.type == 1:
            self.max_hp = 30
            self.damage = 15
        elif self.type == 2:
            self.max_hp = 30
            self.damage = 15
        else:
            self.max_hp = 50
            self.damage = 20

        self.hp = self.max_hp
        self.wait_time = 0.0


        if Zombie.font is None:
            Zombie.font = load_font('ENCR10B.TTF', 16)

        if Zombie.hp_bar_bg is None:
            Zombie.hp_bar_bg = load_image('./UI/체력바.png')
        if Zombie.hp_bar_fill is None:
            Zombie.hp_bar_fill = load_image('./UI/체력줄.png')

        self.IDLE = ZombieIdle(self)
        self.RUN = ZombieRun(self)
        self.WALK = ZombieWalk(self)
        self.ATTACK = ZombieAttack(self)
        self.HURT = ZombieHurt(self)
        self.DEAD = ZombieDead(self)

        self.chase_state = self.RUN

        if self.type in [1, 2]:
            if random.random() < 0.5:
                self.chase_state = self.WALK
            else:
                self.chase_state = self.RUN

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {player_in_sight_range: self.chase_state, player_in_attack_range: self.ATTACK,
                            hit_by_book: self.HURT, hp_is_zero: self.DEAD},
                self.RUN: {player_in_attack_range: self.ATTACK, player_out_of_range: self.IDLE,
                           hit_by_book: self.HURT, hp_is_zero: self.DEAD},
                self.WALK: {player_in_attack_range: self.ATTACK, player_out_of_range: self.IDLE,
                           hit_by_book: self.HURT, hp_is_zero: self.DEAD},
                self.ATTACK: {attack_finished: self.IDLE, hit_by_book: self.HURT, hp_is_zero: self.DEAD},
                self.HURT: {hurt_finished: self.IDLE, hp_is_zero: self.DEAD},
                self.DEAD: {}
            }
        )

    def update(self):
        self.x += game_world.scroll_speed * game_framework.frame_time

        if server.freeze_timer > get_time():
            return

        self.state_machine.update()

        current_speed = RUN_SPEED_PPS
        if self.type in [1, 2]:
            if self.state_machine.cur_state == self.RUN:
                current_speed = RUN_SPEED_PPS * 1.8

        self.x += self.dir * current_speed * game_framework.frame_time

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

        if self.state_machine.cur_state != self.DEAD:
            if Zombie.hp_bar_bg and Zombie.hp_bar_fill:
                bar_x = self.x
                bar_y = self.y + 110

                TARGET_WIDTH = 100
                TARGET_HEIGHT = 20
                HORIZONTAL_PADDING = 8
                VERTICAL_PADDING = 10
                FILL_DRAW_WIDTH = TARGET_WIDTH - HORIZONTAL_PADDING
                FILL_DRAW_HEIGHT = TARGET_HEIGHT - VERTICAL_PADDING

                hp_ratio = self.hp / self.max_hp
                if hp_ratio < 0: hp_ratio = 0
                if hp_ratio > 1: hp_ratio = 1

                FILL_ORIGINAL_WIDTH = Zombie.hp_bar_fill.w
                current_clip_width = int(FILL_ORIGINAL_WIDTH * hp_ratio)
                current_draw_width = int(FILL_DRAW_WIDTH * hp_ratio)

                fill_left_edge_x = bar_x - (TARGET_WIDTH / 2) + (HORIZONTAL_PADDING / 2)
                draw_x = fill_left_edge_x + (current_draw_width / 2)

                Zombie.hp_bar_bg.draw(bar_x, bar_y, TARGET_WIDTH, TARGET_HEIGHT)

                if current_draw_width > 0:
                    Zombie.hp_bar_fill.clip_draw(
                        0, 0, current_clip_width, Zombie.hp_bar_fill.h,
                        draw_x, bar_y, current_draw_width, FILL_DRAW_HEIGHT
                    )

    def get_bb(self):
        return self.state_machine.get_bb()

    def handle_collision(self, group, other):
        if group == 'book:enemy':
            if self.state_machine.cur_state == self.DEAD:
                return
            self.hp -= other.damage
            if self.hp <= 0:
                self.state_machine.handle_state_event(('HP_IS_ZERO', None))
            else:
                self.state_machine.handle_state_event(('HIT_BY_BOOK', None))

        elif group == 'girl:enemy':
            pass