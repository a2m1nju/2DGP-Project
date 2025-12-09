import random
from pico2d import *
import game_framework
import game_world
import server

from state_machine import StateMachine
from coin import Coin
from monster import Monster

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
    'Idle': [(0, 0, 57, 111), (116, 0, 57, 111), (237, 0, 57, 111), (353, 0, 57, 111), (474, 0, 57, 111),
             (591, 0, 57, 111), (700, 0, 57, 111)],
    'Walk': [(0, 0, 70, 114), (122, 0, 70, 114), (242, 0, 70, 114), (363, 0, 70, 114), (477, 0, 70, 114),
             (597, 0, 70, 114), (707, 0, 70, 114), (831, 0, 70, 114)],
    'Attack': [(0, 0, 100, 110), (120, 0, 100, 110),(240, 0, 100, 110),(357, 0, 100, 110)],
    'Hurt': [(0, 0, 74, 106), (114, 0, 74, 106), (236, 0, 74, 106)],
    'Dead': [(0, 0, 53, 102), (124, 0, 51, 102), (239, 0, 69, 102), (361, 0, 113, 102), (495, 0, 123, 102)],
    'Action': [(0, 0, 43, 109), (125, 0, 46, 109), (242, 0, 110, 109), (376, 0, 126, 109), (519, 0, 145, 109),
               (679, 0, 141, 109)]
}


class BossIdle:
    def __init__(self, boss):
        self.boss = boss
        self.image = load_image('./적/보스/보스/Idle.png')
        self.frames = BOSS_ANIMATION_DATA['Idle']

    def enter(self, e):
        self.boss.dir = 0
        self.boss.frame = 0.0

    def do(self):
        self.boss.frame = (self.boss.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(
            self.frames)
        dist_to_player = abs(self.boss.x - self.boss.girl.x)

        if get_time() - self.boss.skill_timer > self.boss.skill_cooldown:
            if dist_to_player < 800:
                self.boss.skill_timer = get_time()
                self.boss.skill_cooldown = random.uniform(5.0, 10.0)
                self.boss.state_machine.handle_state_event(('USE_SKILL', None))
                return

        if dist_to_player < 100:
            self.boss.state_machine.handle_state_event(('PLAYER_IN_ATTACK_RANGE', None))
        elif dist_to_player < 800:
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
        self.image = load_image('./적/보스/보스/Walk.png')
        self.frames = BOSS_ANIMATION_DATA['Walk']

    def enter(self, e):
        self.boss.dir = -1
        self.boss.frame = 0.0

    def do(self):
        dist_to_player = abs(self.boss.girl.x - self.boss.x)

        if get_time() - self.boss.skill_timer > self.boss.skill_cooldown:
            if dist_to_player < 800:
                self.boss.skill_timer = get_time()
                self.boss.skill_cooldown = random.uniform(5.0, 10.0)
                self.boss.state_machine.handle_state_event(('USE_SKILL', None))
                return

        self.boss.update_move()
        self.boss.frame = (self.boss.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(
            self.frames)

    def exit(self, e): pass

    def draw(self): self.boss.draw_image(self.image, self.frames)

    def get_bb(self):
        return self.boss.x - 25, self.boss.y - 140, self.boss.x + 65, self.boss.y + 80


class BossAttack:
    def __init__(self, boss):
        self.boss = boss
        self.image = load_image('./적/보스/보스/Attack.png')
        self.frames = BOSS_ANIMATION_DATA['Attack']

    def enter(self, e):
        self.boss.dir = 0
        self.boss.frame = 0.0

    def do(self):
        self.boss.frame = (self.boss.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)
        if self.boss.frame >= len(self.frames):
            self.boss.state_machine.handle_state_event(('TIMEOUT', None))

    def exit(self, e):
        pass

    def draw(self):
        self.boss.draw_image(self.image, self.frames)

    def get_bb(self):
        return self.boss.x - 100, self.boss.y - 140, self.boss.x + 100, self.boss.y + 80


class BossHurt:
    def __init__(self, boss):
        self.boss = boss
        self.image = load_image('./적/보스/보스/Hurt.png')
        self.frames = BOSS_ANIMATION_DATA['Hurt']

    def enter(self, e):
        self.boss.frame = 0.0

    def do(self):
        self.boss.frame = (self.boss.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)
        if self.boss.frame >= len(self.frames):
            self.boss.state_machine.handle_state_event(('TIMEOUT', None))

    def exit(self, e):
        pass

    def draw(self):
        self.boss.draw_image(self.image, self.frames)

    def get_bb(self):
        return self.boss.x - 50, self.boss.y - 140, self.boss.x + 50, self.boss.y + 80


class BossDead:
    def __init__(self, boss):
        self.boss = boss
        self.image = load_image('./적/보스/보스/Dead.png')
        self.frames = BOSS_ANIMATION_DATA['Dead']

    def enter(self, e):
        self.boss.frame = 0.0
        game_world.remove_collision_object(self.boss)

        for _ in range(20):
            coin = Coin(self.boss.x + random.randint(-100, 100), self.boss.y + 50, 100)
            game_world.add_object(coin, 3)
            game_world.add_collision_pair('girl:coin', None, coin)

    def do(self):
        self.boss.frame = (self.boss.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)
        if self.boss.frame >= len(self.frames):
            self.boss.frame = len(self.frames) - 1
            server.enemies_killed_count = 9999

    def exit(self, e):
        pass

    def draw(self):
        self.boss.draw_image(self.image, self.frames)

    def get_bb(self):
        return 0, 0, 0, 0


class BossAction:
    def __init__(self, boss):
        self.boss = boss
        self.image = load_image('./적/보스/보스/Action.png')
        self.frames = BOSS_ANIMATION_DATA['Action']

    def enter(self, e):
        self.boss.dir = 0
        self.boss.frame = 0.0
        self.spawned = False

    def do(self):
        self.boss.frame = (self.boss.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time * 0.3)

        if int(self.boss.frame) == 6 and not self.spawned:
            self.spawn_monster()
            self.spawned = True

        if self.boss.frame >= len(self.frames):
            self.boss.state_machine.handle_state_event(('TIMEOUT', None))

    def spawn_monster(self):
        spawn_x = self.boss.x + (150 * self.boss.face_dir)
        spawn_y = self.boss.y - 50

        minion = Monster(spawn_x, spawn_y, self.boss.girl)

        game_world.add_object(minion, 3)

        game_world.add_collision_pair('girl:enemy', None, minion)
        game_world.add_collision_pair('book:enemy', None, minion)

    def exit(self, e):
        pass

    def draw(self):
        self.boss.draw_image(self.image, self.frames)

    def get_bb(self):
        return self.boss.get_bb_rect()


class FinalBoss:
    font = None
    hp_bar_bg = None
    hp_bar_fill = None

    def __init__(self, girl):
        self.girl = girl
        self.x, self.y = 1600, 200
        self.frame = 0.0
        self.face_dir = -1
        self.dir = 0

        self.max_hp = 10
        self.hp = self.max_hp

        self.scale = 2.0

        self.skill_timer = get_time()
        self.skill_cooldown = random.uniform(5.0, 10.0)

        if FinalBoss.font is None: FinalBoss.font = load_font('ENCR10B.TTF', 16)
        if FinalBoss.hp_bar_bg is None: FinalBoss.hp_bar_bg = load_image('./UI/체력바.png')
        if FinalBoss.hp_bar_fill is None: FinalBoss.hp_bar_fill = load_image('./UI/체력줄.png')

        self.IDLE = BossIdle(self)
        self.WALK = BossWalk(self)
        self.ATTACK = BossAttack(self)
        self.HURT = BossHurt(self)
        self.DEAD = BossDead(self)
        self.ACTION = BossAction(self)

        self.skill_timer = get_time()

        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {player_in_sight_range: self.WALK, player_in_attack_range: self.ATTACK,
                            hit_by_book: self.HURT, hp_is_zero: self.DEAD, use_skill: self.ACTION},
                self.WALK: {player_in_attack_range: self.ATTACK, player_out_of_range: self.IDLE, hit_by_book: self.HURT,
                            hp_is_zero: self.DEAD, use_skill: self.ACTION},
                self.ATTACK: {attack_finished: self.IDLE, hit_by_book: self.HURT, hp_is_zero: self.DEAD},
                self.HURT: {hurt_finished: self.IDLE, hp_is_zero: self.DEAD},
                self.DEAD: {},
                self.ACTION: {attack_finished: self.IDLE, hit_by_book: self.HURT, hp_is_zero: self.DEAD
                }
            }
        )

    def update(self):
        self.x += game_world.scroll_speed * game_framework.frame_time
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
        if dist_abs < 100:
            self.state_machine.handle_state_event(('PLAYER_IN_ATTACK_RANGE', None))
        elif dist_abs > 1200:
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
            l, b, w, h = 0, 0, image.w, image.h
        else:
            l, b, w, h = frames[idx]

        dst_w = w * self.scale
        dst_h = h * self.scale

        if self.face_dir == -1:
            image.clip_composite_draw(l, b, w, h, 0, 'h', self.x, self.y - 30, dst_w, dst_h)
        else:
            image.clip_composite_draw(l, b, w, h, 0, '', self.x, self.y - 30, dst_w, dst_h)

    def draw_hp_bar(self):
        if FinalBoss.hp_bar_bg and FinalBoss.hp_bar_fill:
            bar_x = self.x
            bar_y = self.y + 150

            TARGET_WIDTH = 200
            TARGET_HEIGHT = 30
            HORIZONTAL_PADDING = 18
            VERTICAL_PADDING = 12
            FILL_DRAW_WIDTH = TARGET_WIDTH - HORIZONTAL_PADDING
            FILL_DRAW_HEIGHT = TARGET_HEIGHT - VERTICAL_PADDING

            hp_ratio = self.hp / self.max_hp
            if hp_ratio < 0: hp_ratio = 0
            if hp_ratio > 1: hp_ratio = 1

            FILL_ORIGINAL_WIDTH = FinalBoss.hp_bar_fill.w
            current_clip_width = int(FILL_ORIGINAL_WIDTH * hp_ratio)
            current_draw_width = int(FILL_DRAW_WIDTH * hp_ratio)

            fill_left_edge_x = bar_x - (TARGET_WIDTH / 2) + (HORIZONTAL_PADDING / 2)
            draw_x = fill_left_edge_x + (current_draw_width / 2)

            FinalBoss.hp_bar_bg.draw(bar_x, bar_y, TARGET_WIDTH, TARGET_HEIGHT)
            if current_draw_width > 0:
                FinalBoss.hp_bar_fill.clip_draw(0, 0, current_clip_width, FinalBoss.hp_bar_fill.h, draw_x, bar_y,
                                                current_draw_width, FILL_DRAW_HEIGHT)

    def get_bb(self):
        return self.state_machine.get_bb()

    def get_bb_rect(self):
        return self.x - 60, self.y - 80, self.x + 60, self.y + 80

    def handle_collision(self, group, other):
        if group == 'book:enemy':
            if self.state_machine.cur_state == self.DEAD: return
            self.hp -= other.damage
            if self.hp <= 0:
                self.state_machine.handle_state_event(('HP_IS_ZERO', None))
            else:
                self.state_machine.handle_state_event(('HIT_BY_BOOK', None))