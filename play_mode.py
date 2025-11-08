import random
from pico2d import *

import game_framework
import game_world

from girl import Girl
from subway import Subway
from book import Book

girl = None

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            girl.handle_event(event)

def init():
    global girl

    girl = Girl()
    game_world.add_object(girl, 4)

    Subway('./배경/내부1.png', 800, 300, 1600, 600, 0)
    Subway('./배경/기둥2.png', 805, 270, 780, 340, 3)
    Subway('./배경/문1.png', 300, 268, 180, 320, 2)
    Subway('./배경/문2.png', 1300, 268, 180, 320, 2)

    seat_y = 158
    seat_w, seat_h = 87, 100
    for i in range(4):
        seat_x = 498 + (i * 87)
        Subway('./배경/좌석.png', seat_x, seat_y, seat_w, seat_h, 2)

    # 오른쪽 4개 좌석 (문2 왼쪽)
    for i in range(4):
        seat_x = 846 + (i * 87)
        Subway('./배경/좌석.png', seat_x, seat_y, seat_w, seat_h, 2)


def update():
    game_world.update()
    game_world.handle_collisions()


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def finish():
    game_world.clear()

def pause(): pass
def resume(): pass

