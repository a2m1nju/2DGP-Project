from pico2d import *
import random
import game_framework
import game_world
import server

from state_machine import StateMachine
from coin import Coin
from food import Food
from poison import Poison

PIXEL_PER_METER = (10.0 / 0.3)
RUN_SPEED_KMPH = 10.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8


time_out = lambda e: e[0] == 'TIMEOUT'
player_in_sight_range = lambda e: e[0] == 'PLAYER_IN_SIGHT_RANGE'
player_in_attack_range = lambda e: e[0] == 'PLAYER_IN_ATTACK_RANGE'
player_out_of_range = lambda e: e[0] == 'PLAYER_OUT_OF_RANGE'
hit_by_book = lambda e: e[0] == 'HIT_BY_BOOK'
hp_is_zero = lambda e: e[0] == 'HP_IS_ZERO'
use_skill = lambda e: e[0] == 'USE_SKILL'

attack_finished = time_out
hurt_finished = time_out
dead_finished = time_out
skill_finished = time_out

BOSS_ANIMATION_DATA = {
    'Idle': [(0, 0, 70, 78), (136, 0, 70, 78), (274, 0, 70, 78), (410, 0, 70, 78), (545, 0, 70, 78),
             (683, 0, 70, 78)],
    'Walk': [(0, 0, 80, 85), (146, 0, 80, 85), (278, 0, 80, 85), (408, 0, 80, 85), (545, 0, 80, 85),
             (686, 0, 80, 85), (824, 0, 80, 85), (964, 0, 80, 85)],
    'Run': [(0, 0, 89, 84), (139, 0, 83, 84), (268, 0, 94, 84), (408, 0, 89, 84), (547, 0, 84, 84),
            (680, 0, 88, 84), (810, 0, 97, 84)],
    'Attack': [(0, 0, 80, 96),(134, 0, 80, 96), (254, 0, 80, 96), (409, 0, 80, 96), (545, 0, 80, 96), ],
    'Hurt': [(0, 0, 65, 79), (136, 0, 65, 79), (274, 0, 65, 79), (408, 0, 65, 79), (544, 0, 65, 79)],
    'Dead': [(0, 0, 50, 78), (134, 0, 52, 78), (280, 0, 45, 78), (405, 0, 56, 78), (547, 0, 71, 78)],
    'Poison': [(0, 0, 100, 53), (133, 0, 68, 117),(264, 0, 86, 117),(387, 0, 103, 117),(519, 0, 112, 117),
               (649, 0, 123, 117)]
}


class BossIdle:
    def __init__(self, boss):
        self.boss = boss
        self.image = load_image('./적/좀비중간보스/Idle.png')
        self.frames = BOSS_ANIMATION_DATA['Idle']

    def enter(self, e):
        self.boss.wait_time = get_time()
        self.boss.dir = 0
        self.boss.frame = 0.0

    def do(self):
        self.boss.frame = (self.boss.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(
            self.frames)

        dist_to_player = abs(self.boss.x - self.boss.girl.x)

        if dist_to_player < 150:
            self.boss.state_machine.handle_state_event(('PLAYER_IN_ATTACK_RANGE', None))
        elif dist_to_player < 800:
            current_time = get_time()
            if current_time - self.boss.last_skill_time > self.boss.skill_cooldown:
                if dist_to_player > 300 and random.random() < 0.01:
                    self.boss.state_machine.handle_state_event(('USE_SKILL', None))
                    return

            self.boss.state_machine.handle_state_event(('PLAYER_IN_SIGHT_RANGE', None))

    def exit(self, e):
        pass

    def draw(self):
        self.boss.draw_image(self.image, self.frames)

    def get_bb(self):
        return self.boss.get_bb_rect()


class BossWalk:
    def __init__(self, boss):
        self.boss = boss
        self.image = load_image('./적/좀비중간보스/Walk.png')
        self.frames = BOSS_ANIMATION_DATA['Walk']

    def enter(self, e):
        self.boss.dir = 1
        self.boss.frame = 0.0

    def do(self):
        self.boss.update_move()
        self.boss.frame = (self.boss.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(
            self.frames)

        current_time = get_time()
        if current_time - self.boss.last_skill_time > self.boss.skill_cooldown:
            if random.random() < 0.01:
                self.boss.state_machine.handle_state_event(('USE_SKILL', None))

    def exit(self, e): pass

    def draw(self): self.boss.draw_image(self.image, self.frames)

    def get_bb(self): return self.boss.get_bb_rect()


class BossRun:
    def __init__(self, boss):
        self.boss = boss
        self.image = load_image('./적/좀비중간보스/Run.png')
        self.frames = BOSS_ANIMATION_DATA['Run']

    def enter(self, e): self.boss.frame = 0.0

    def do(self):
        self.boss.update_move()
        self.boss.frame = (self.boss.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(
            self.frames)

        current_time = get_time()
        if current_time - self.boss.last_skill_time > self.boss.skill_cooldown:
            if random.random() < 0.01:
                self.boss.state_machine.handle_state_event(('USE_SKILL', None))

    def exit(self, e): pass

    def draw(self): self.boss.draw_image(self.image, self.frames)

    def get_bb(self): return self.boss.get_bb_rect()


class BossAttack:
    def __init__(self, boss):
        self.boss = boss
        self.image = load_image('./적/좀비중간보스/Attack.png')
        self.frames = BOSS_ANIMATION_DATA['Attack']

    def enter(self, e):
        self.boss.dir = 0
        self.boss.frame = 0.0

    def do(self):
        self.boss.frame = (self.boss.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)
        if self.boss.frame >= len(self.frames):
            self.boss.frame = len(self.frames) - 1
            self.boss.state_machine.handle_state_event(('TIMEOUT', None))

    def exit(self, e):
        pass

    def draw(self):
        self.boss.draw_image(self.image, self.frames)

    def get_bb(self):
        l, b, r, t = self.boss.get_bb_rect()
        if self.boss.face_dir == 1:
            return l + 20, b, r + 20, t
        else:
            return l - 20, b, r - 20, t

class BossSkill:
    def __init__(self, boss):
        self.boss = boss
        self.image = load_image('./적/좀비중간보스/Poison.png')
        self.frames = BOSS_ANIMATION_DATA['Poison']
        self.has_spawned = False

    def enter(self, e):
        self.boss.dir = 0
        self.boss.frame = 0.0
        self.boss.last_skill_time = get_time()
        self.has_spawned = False

    def do(self):
        self.boss.frame = (self.boss.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)

        if int(self.boss.frame) == 3 and not self.has_spawned:
            self.spawn_poison()
            self.has_spawned = True

        if self.boss.frame >= len(self.frames):
            self.boss.frame = len(self.frames) - 1
            self.boss.state_machine.handle_state_event(('TIMEOUT', None))

    def exit(self, e):
        pass

    def draw(self):
        self.boss.draw_image(self.image, self.frames)

    def get_bb(self):
        return self.boss.get_bb_rect()

    def spawn_poison(self):
        import random
        target_x = self.boss.girl.x

        spawned_positions = []
        count = 0
        max_attempts = 20

        while count < 2 and max_attempts > 0:
            max_attempts -= 1

            offset = random.randint(-200, 200)
            spawn_x = target_x + offset

            spawn_x = clamp(50, spawn_x, 1550)

            is_too_close = False
            for prev_x in spawned_positions:
                if abs(spawn_x - prev_x) < 80:
                    is_too_close = True
                    break

            if is_too_close:
                continue

            spawned_positions.append(spawn_x)

            spawn_y = 120
            poison = Poison(spawn_x, spawn_y)
            game_world.add_object(poison, 4)
            game_world.add_collision_pair('girl:poison', None, poison)

            count += 1


class BossHurt:
    def __init__(self, boss):
        self.boss = boss
        self.image = load_image('./적/좀비중간보스/Hurt.png')
        self.frames = BOSS_ANIMATION_DATA['Hurt']

    def enter(self, e):
        self.boss.dir = 0
        self.boss.frame = 0.0

    def do(self):
        self.boss.frame = (self.boss.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)
        if self.boss.frame >= len(self.frames):
            self.boss.frame = len(self.frames) - 1
            self.boss.state_machine.handle_state_event(('TIMEOUT', None))

    def exit(self, e): pass

    def draw(self): self.boss.draw_image(self.image, self.frames)

    def get_bb(self): return self.boss.get_bb_rect()


class BossDead:
    def __init__(self, boss):
        self.boss = boss
        self.image = load_image('./적/좀비중간보스/Dead.png')
        self.frames = BOSS_ANIMATION_DATA['Dead']

    def enter(self, e):
        self.boss.dir = 0
        self.boss.frame = 0.0
        game_world.remove_collision_object(self.boss)
        server.enemies_killed_count += 1
        self.boss.girl.gain_exp(100)

        for _ in range(5):
            coin = Coin(self.boss.x + random.randint(-50, 50), self.boss.y + 30, 100)
            game_world.add_object(coin, 3)
            game_world.add_collision_pair('girl:coin', None, coin)

    def do(self):
        self.boss.frame = (self.boss.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)
        if self.boss.frame >= len(self.frames):
            self.boss.frame = len(self.frames) - 1

    def exit(self, e):
        pass

    def draw(self):
        self.boss.draw_image(self.image, self.frames)

    def get_bb(self):
        return 0, 0, 0, 0


class ZombieBoss:
    font = None
    hp_bar_bg = None
    hp_bar_fill = None

    def __init__(self, girl):
        self.girl = girl
        self.x, self.y = 1700, 150
        self.frame = 0.0
        self.face_dir = -1
        self.dir = 0

        self.max_hp = 100
        self.hp = self.max_hp

        self.skill_cooldown = 8.0
        self.last_skill_time = get_time() - 5.0

        self.scale = 2.5
        self.bb_width = 60
        self.bb_height = 120

        if ZombieBoss.font is None: ZombieBoss.font = load_font('ENCR10B.TTF', 16)
        if ZombieBoss.hp_bar_bg is None: ZombieBoss.hp_bar_bg = load_image('./UI/체력바.png')
        if ZombieBoss.hp_bar_fill is None: ZombieBoss.hp_bar_fill = load_image('./UI/체력줄.png')

        self.IDLE = BossIdle(self)
        self.RUN = BossRun(self)
        self.WALK = BossWalk(self)
        self.ATTACK = BossAttack(self)
        self.SKILL = BossSkill(self)
        self.HURT = BossHurt(self)
        self.DEAD = BossDead(self)

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {player_in_sight_range: self.RUN, player_in_attack_range: self.ATTACK,
                            hit_by_book: self.HURT, hp_is_zero: self.DEAD, use_skill: self.SKILL},
                self.RUN: {player_in_attack_range: self.ATTACK, player_out_of_range: self.IDLE,
                           hit_by_book: self.HURT, hp_is_zero: self.DEAD, use_skill: self.SKILL},
                self.WALK: {player_in_attack_range: self.ATTACK, player_out_of_range: self.IDLE,
                            hit_by_book: self.HURT, hp_is_zero: self.DEAD, use_skill: self.SKILL},
                self.ATTACK: {attack_finished: self.IDLE, hit_by_book: self.HURT, hp_is_zero: self.DEAD},
                self.SKILL: {skill_finished: self.IDLE, hit_by_book: self.HURT, hp_is_zero: self.DEAD},
                self.HURT: {hurt_finished: self.IDLE, hp_is_zero: self.DEAD},
                self.DEAD: {}
            }
        )

    def update(self):
        self.x += game_world.scroll_speed * game_framework.frame_time
        if server.freeze_timer > get_time(): return
        self.state_machine.update()

    def update_move(self):
        dist = self.girl.x - self.x
        if dist > 0:
            self.dir, self.face_dir = 1, 1
        elif dist < 0:
            self.dir, self.face_dir = -1, -1
        else:
            self.dir = 0

        dist_abs = abs(dist)
        if dist_abs < 150:
            self.state_machine.handle_state_event(('PLAYER_IN_ATTACK_RANGE', None))
        elif dist_abs > 800:
            self.state_machine.handle_state_event(('PLAYER_OUT_OF_RANGE', None))

        self.x += self.dir * RUN_SPEED_PPS * game_framework.frame_time

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())
        if self.state_machine.cur_state != self.DEAD:
            self.draw_hp_bar()

    def draw_image(self, image, frames):
        idx = int(self.frame)
        if idx >= len(frames): idx = len(frames) - 1

        if not frames:
            left, bottom, width, height = 0, 0, image.w, image.h
        else:
            left, bottom, width, height = frames[idx]

        dst_w = width * self.scale
        dst_h = height * self.scale

        base_height = 78
        y_offset = (height - base_height) * self.scale / 2
        dst_y = self.y + y_offset + 10

        if self.face_dir == -1:
            image.clip_composite_draw(left, bottom, width, height, 0, 'h', self.x, dst_y, dst_w, dst_h)
        else:
            image.clip_composite_draw(left, bottom, width, height, 0, '', self.x, dst_y, dst_w, dst_h)

    def draw_hp_bar(self):
        if ZombieBoss.hp_bar_bg and ZombieBoss.hp_bar_fill:
            bar_x = self.x
            bar_y = self.y + 200

            TARGET_WIDTH = 200
            TARGET_HEIGHT = 30
            HORIZONTAL_PADDING = 18
            VERTICAL_PADDING = 12
            FILL_DRAW_WIDTH = TARGET_WIDTH - HORIZONTAL_PADDING
            FILL_DRAW_HEIGHT = TARGET_HEIGHT - VERTICAL_PADDING

            hp_ratio = self.hp / self.max_hp
            if hp_ratio < 0: hp_ratio = 0
            if hp_ratio > 1: hp_ratio = 1

            FILL_ORIGINAL_WIDTH = ZombieBoss.hp_bar_fill.w
            current_clip_width = int(FILL_ORIGINAL_WIDTH * hp_ratio)
            current_draw_width = int(FILL_DRAW_WIDTH * hp_ratio)

            fill_left_edge_x = bar_x - (TARGET_WIDTH / 2) + (HORIZONTAL_PADDING / 2)
            draw_x = fill_left_edge_x + (current_draw_width / 2)

            ZombieBoss.hp_bar_bg.draw(bar_x, bar_y, TARGET_WIDTH, TARGET_HEIGHT)
            if current_draw_width > 0:
                ZombieBoss.hp_bar_fill.clip_draw(
                    0, 0, current_clip_width, ZombieBoss.hp_bar_fill.h,
                    draw_x, bar_y, current_draw_width, FILL_DRAW_HEIGHT
                )

    def get_bb(self):
        return self.state_machine.get_bb()

    def get_bb_rect(self):
        return self.x - 90, self.y - 100, self.x + 90, self.y + 140


    def handle_collision(self, group, other):
        if group == 'book:enemy':
            if self.state_machine.cur_state == self.DEAD: return
            self.hp -= other.damage
            if self.hp <= 0:
                self.state_machine.handle_state_event(('HP_IS_ZERO', None))
            else:
                self.state_machine.handle_state_event(('HIT_BY_BOOK', None))
        elif group == 'girl:enemy':
            pass