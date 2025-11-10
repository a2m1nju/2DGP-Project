import random
from pico2d import *

import game_framework
import game_world

from girl import Girl
from subway import Subway
from book import Book
from enemy import Enemy
from enemy_R import Enemy_R

girl = None
font = None
spawn_timer = 0.0
spawn_cooldown = 8.0
spawn_count = 0
max_spawn_count = 2

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
    global girl, font, spawn_timer, spawn_count
    global enemies_killed_count

    girl = Girl()
    girl.x = 800
    game_world.add_object(girl, 4)
    game_world.add_collision_pair('girl:enemy', girl, None)

    game_world.add_collision_pair('fire:girl', None, girl)

    font = load_font('ENCR10B.TTF', 16)

    Subway('./배경/내부2.png', 800, 300, 1600, 600, 0, is_looping=True)

    enemy = Enemy(girl)
    game_world.add_object(enemy, 4)
    game_world.add_collision_pair('book:enemy', None, enemy)
    game_world.add_collision_pair('girl:enemy', None, enemy)

    enemy_r = Enemy_R(girl)
    enemy_r.x = 1300
    game_world.add_object(enemy_r, 4)
    game_world.add_collision_pair('book:enemy', None, enemy_r)
    game_world.add_collision_pair('girl:enemy', None, enemy_r)

    spawn_count = 2
    spawn_timer = get_time()
    enemies_killed_count = 0

def update():
    global spawn_timer, spawn_cooldown, spawn_count, max_spawn_count
    global enemies_killed_count

    game_world.update()
    game_world.handle_collisions()

    if enemies_killed_count >= max_spawn_count:
        import gameclear_mode
        game_framework.change_mode(gameclear_mode)
        return

    if spawn_count >= max_spawn_count:
        return

    current_time = get_time()
    if current_time - spawn_timer > spawn_cooldown:
        spawn_timer = current_time
        enemy = Enemy(girl)
        enemy.x = 1600 + 100
        game_world.add_object(enemy, 4)
        game_world.add_collision_pair('book:enemy', None, enemy)
        game_world.add_collision_pair('girl:enemy', None, enemy)
        spawn_count += 1


def draw():
    clear_canvas()
    game_world.render()
    font.draw(girl.x - 30, girl.y + 110, f'HP: {girl.hp}', (255, 0, 0))
    update_canvas()


def finish():
    game_world.clear()

def pause(): pass
def resume(): pass

