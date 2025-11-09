import random
from pico2d import *

import game_framework
import game_world

from girl import Girl
from subway import Subway
from book import Book
from enemy import Enemy

girl = None
font = None

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
    global girl, font

    girl = Girl()
    girl.x = 800
    game_world.add_object(girl, 4)
    game_world.add_collision_pair('girl:enemy', girl, None)

    font = load_font('ENCR10B.TTF', 16)


    Subway('./배경/내부2.png', 800, 300, 1600, 600, 0, is_looping=True)

    enemy = Enemy(girl)
    game_world.add_object(enemy, 4)
    game_world.add_collision_pair('book:enemy', None, enemy)
    game_world.add_collision_pair('girl:enemy', None, enemy)

def update():
    game_world.update()
    game_world.handle_collisions()


def draw():
    clear_canvas()
    game_world.render()
    font.draw(girl.x - 30, girl.y + 110, f'HP: {girl.hp}', (255, 0, 0))
    update_canvas()


def finish():
    game_world.clear()

def pause(): pass
def resume(): pass

