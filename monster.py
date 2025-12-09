# monster.py
from pico2d import *
import game_framework
import game_world
import server
from state_machine import StateMachine

PIXEL_PER_METER = (10.0 / 0.3)
RUN_SPEED_KMPH = 18.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8

time_out = lambda e: e[0] == 'TIMEOUT'
player_in_attack_range = lambda e: e[0] == 'PLAYER_IN_ATTACK_RANGE'
player_out_of_range = lambda e: e[0] == 'PLAYER_OUT_OF_RANGE'
hit_by_book = lambda e: e[0] == 'HIT_BY_BOOK'
hp_is_zero = lambda e: e[0] == 'HP_IS_ZERO'
attack_finished = time_out
hurt_finished = time_out


MONSTER_ANIMATION_DATA = {
    'Idle': [(0, 0, 62, 72), (118, 0, 62, 72), (236, 0, 62, 72), (354, 0, 62, 72), (472, 0, 62, 72),
             (590, 0, 62, 72)],
    'Walk': [(0, 0, 36, 69), (118, 0, 36, 69), (236, 0, 36, 69), (348, 0, 36, 69)],
    'Attack': [(0, 0, 58, 70), (109, 0, 86, 70), (214, 0, 104, 70), (358, 0, 63, 70), (488, 0, 66, 70),
               (606, 0, 66, 70)],
    'Hurt': [(0, 0, 60, 68), (110, 0, 87, 68), (224, 0, 87, 68), ],
    'Dead': [(0, 0, 60, 79), (118, 0, 57, 79), (235, 0, 60, 79), (354, 0, 66, 79), (468, 0, 70, 79)]
}


class MonsterIdle:
    def __init__(self, monster):
        self.monster = monster
        self.image = load_image('./적/보스/몬스터/Idle.png')
        self.frames = MONSTER_ANIMATION_DATA['Idle']

    def enter(self, e):
        self.monster.frame = 0
        self.monster.dir = 0

    def do(self):
        self.monster.frame = (self.monster.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(self.frames)
        dist = abs(self.monster.x - self.monster.target.x)
        if dist < 100:
            self.monster.state_machine.handle_state_event(('PLAYER_IN_ATTACK_RANGE', None))
        elif dist < 800:
            self.monster.state_machine.handle_state_event(('PLAYER_IN_SIGHT_RANGE', None))

    def exit(self, e):
        pass

    def draw(self):
        self.monster.draw_image(self.image, self.frames)

    def get_bb(self):
        return self.monster.x - 30, self.monster.y - 40, self.monster.x + 30, self.monster.y + 40


class MonsterWalk:
    def __init__(self, monster):
        self.monster = monster
        self.image = load_image('./적/보스/몬스터/Walk.png')
        self.frames = MONSTER_ANIMATION_DATA['Walk']

    def enter(self, e):
        self.monster.frame = 0

    def do(self):
        diff = self.monster.target.x - self.monster.x
        self.monster.dir = 1 if diff > 0 else -1
        self.monster.face_dir = self.monster.dir
        self.monster.x += self.monster.dir * RUN_SPEED_PPS * game_framework.frame_time

        self.monster.frame = ( self.monster.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(self.frames)

        dist = abs(diff)
        if dist < 100:
            self.monster.state_machine.handle_state_event(('PLAYER_IN_ATTACK_RANGE', None))
        elif dist > 1000:
            self.monster.state_machine.handle_state_event(('PLAYER_OUT_OF_RANGE', None))

    def exit(self, e):
        pass

    def draw(self):
        self.monster.draw_image(self.image, self.frames)

    def get_bb(self):
        return self.monster.x - 40, self.monster.y - 70, self.monster.x + 40, self.monster.y + 70


class MonsterAttack:
    def __init__(self, monster):
        self.monster = monster
        self.image = load_image('./적/보스/몬스터/Attack.png')
        self.frames = MONSTER_ANIMATION_DATA['Attack']

    def enter(self, e):
        self.monster.frame = 0

    def do(self):
        self.monster.frame = (self.monster.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)
        if self.monster.frame >= len(self.frames):
            self.monster.state_machine.handle_state_event(('TIMEOUT', None))

    def exit(self, e): pass

    def draw(self): self.monster.draw_image(self.image, self.frames)

    def get_bb(self):
        if self.monster.face_dir == -1:
            return self.monster.x - 70, self.monster.y - 70, self.monster.x + 70, self.monster.y + 70
        else:
            return self.monster.x - 70, self.monster.y - 70, self.monster.x + 70, self.monster.y + 70


class MonsterHurt:
    def __init__(self, monster):
        self.monster = monster
        self.image = load_image('./적/보스/몬스터/Hurt.png')
        self.frames = MONSTER_ANIMATION_DATA['Hurt']

    def enter(self, e): self.monster.frame = 0

    def do(self):
        self.monster.frame += FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time
        if self.monster.frame >= len(self.frames): self.monster.state_machine.handle_state_event(('TIMEOUT', None))

    def exit(self, e): pass

    def draw(self): self.monster.draw_image(self.image, self.frames)

    def get_bb(self):
        return self.monster.x - 70, self.monster.y - 50, self.monster.x + 70, self.monster.y + 50

class MonsterDead:
    def __init__(self, monster):
        self.monster = monster
        self.image = load_image('./적/보스/몬스터/Dead.png')
        self.frames = MONSTER_ANIMATION_DATA['Dead']

    def enter(self, e):
        self.monster.frame = 0
        game_world.remove_collision_object(self.monster)
        server.enemies_killed_count += 1

    def do(self):
        self.monster.frame += FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time
        if self.monster.frame >= len(self.frames): self.monster.frame = len(self.frames) - 1

    def exit(self, e): pass

    def draw(self): self.monster.draw_image(self.image, self.frames)

    def get_bb(self): return 0, 0, 0, 0


class Monster:
    def __init__(self, x, y, target):
        self.x, self.y = x, y
        self.target = target
        self.frame = 0
        self.dir = 0
        self.face_dir = -1
        self.hp = 3

        self.IDLE = MonsterIdle(self)
        self.WALK = MonsterWalk(self)
        self.ATTACK = MonsterAttack(self)
        self.HURT = MonsterHurt(self)
        self.DEAD = MonsterDead(self)

        self.state_machine = StateMachine(self.IDLE, {
            self.IDLE: {lambda e: e[0] == 'PLAYER_IN_SIGHT_RANGE': self.WALK,
                        lambda e: e[0] == 'PLAYER_IN_ATTACK_RANGE': self.ATTACK, hit_by_book: self.HURT,
                        hp_is_zero: self.DEAD},
            self.WALK: {player_out_of_range: self.IDLE, lambda e: e[0] == 'PLAYER_IN_ATTACK_RANGE': self.ATTACK,
                        hit_by_book: self.HURT, hp_is_zero: self.DEAD},
            self.ATTACK: {attack_finished: self.IDLE, hit_by_book: self.HURT, hp_is_zero: self.DEAD},
            self.HURT: {hurt_finished: self.IDLE, hp_is_zero: self.DEAD},
            self.DEAD: {}
        })

    def update(self):
        self.x += game_world.scroll_speed * game_framework.frame_time
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def draw_image(self, image, frames):
        idx = int(self.frame)
        if idx >= len(frames): idx = len(frames) - 1
        l, b, w, h = frames[idx]
        if self.face_dir == -1:
            image.clip_composite_draw(l, b, w, h, 0, 'h', self.x, self.y, w * 2, h * 2)
        else:
            image.clip_composite_draw(l, b, w, h, 0, '', self.x, self.y, w * 2, h * 2)

    def get_bb(self):
        return self.state_machine.get_bb()

    def get_bb_rect(self):
        return self.x - 20, self.y - 35, self.x + 20, self.y + 35

    def handle_collision(self, group, other):
        if group == 'book:enemy':
            if self.state_machine.cur_state == self.DEAD: return
            self.hp -= other.damage
            if self.hp <= 0:
                self.state_machine.handle_state_event(('HP_IS_ZERO', None))
            else:
                self.state_machine.handle_state_event(('HIT_BY_BOOK', None))