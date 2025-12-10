from pico2d import *
import game_world
import game_framework

FALL_SPEED_PPS = 300
GROUND_Y = 130

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 9
PIXEL_PER_METER = (1.0 / 0.03)
GRAVITY = 9.8

class Coin:
    image_10 = None
    image_20 = None
    image_30 = None
    coin_collect_sound = None

    def __init__(self, x, y, value = 10):
        if Coin.image_10 is None:
            Coin.image_10 = load_image('./아이템/코인/코인1.png')

        if Coin.image_20 is None:
            Coin.image_20 = load_image('./아이템/코인/코인2.png')

        if Coin.image_30 is None:
            Coin.image_30 = load_image('./아이템/코인/코인3.png')

        if Coin.coin_collect_sound is None:
            try:
                Coin.coin_collect_sound = load_wav('./음악/코인.mp3')
                Coin.coin_collect_sound.set_volume(5)
            except Exception as e:
                print(f"코인 효과음 로드 실패: ./음악/coin_collect.wav, {e}")
                Coin.coin_collect_sound = None

        self.x, self.y = x, y
        self.yv = FALL_SPEED_PPS
        self.value = value

    def update(self):
        self.x += game_world.scroll_speed * game_framework.frame_time

        if self.y > GROUND_Y:
            self.yv -= GRAVITY * PIXEL_PER_METER * game_framework.frame_time
            self.y += self.yv * game_framework.frame_time

        if self.y < GROUND_Y:
            self.y = GROUND_Y
            self.yv = 0

    def draw(self):
        if self.value == 30:
            self.image_30.draw(self.x, self.y, 24, 24)
        elif self.value == 20:
            self.image_20.draw(self.x, self.y, 24, 24)
        else:
            self.image_10.draw(self.x, self.y, 24, 24)
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.x - 12, self.y - 12, self.x + 12, self.y + 12

    def handle_collision(self, group, other):
        if group == 'girl:coin':
            if Coin.coin_collect_sound:
                Coin.coin_collect_sound.play()
            game_world.remove_object(self)
