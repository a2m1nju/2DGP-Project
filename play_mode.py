import random
from pico2d import *

import game_framework
import game_world

from girl import Girl
from subway import Subway
from enemy import Enemy
from enemy_R import Enemy_R

girl = None
font = None

skill_q_icon = None
skill_q_icon_bw = None
skill_e_icon = None
skill_e_icon_bw = None

spawn_timer = 0.0
spawn_cooldown = 8.0
max_spawn_count = 3
max_enemies_on_screen = 3
coin_count = 0

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
    global girl, font, spawn_timer, coin_count, skill_q_icon, skill_q_icon_bw
    global enemies_killed_count, skill_e_icon, skill_e_icon_bw


    girl = Girl()
    girl.x = 800
    game_world.add_object(girl, 4)
    game_world.add_collision_pair('girl:enemy', girl, None)
    game_world.add_collision_pair('fire:girl', None, girl)
    game_world.add_collision_pair('girl:coin', girl, None)
    game_world.add_collision_pair('girl:food', girl, None)

    font = load_font('ENCR10B.TTF', 16)

    skill_q_icon = load_image('./이펙트/스킬/Q.png')
    skill_q_icon_bw = load_image('./이펙트/스킬/Q_b.png')

    skill_e_icon = load_image('./이펙트/스킬/E.png')
    skill_e_icon_bw = load_image('./이펙트/스킬/E_b.png')

    Subway('./배경/내부2.png', 800, 300, 1600, 600, 0, is_looping=True)

    for i in range(0,1):
        if random.choice([True, False]):
            e = Enemy(girl)
        else:
            e = Enemy_R(girl)

        e.x = random.randint(1000, 1500)
        game_world.add_object(e, 4)
        game_world.add_collision_pair('book:enemy', None, e)
        game_world.add_collision_pair('girl:enemy', None, e)

    spawn_timer = get_time()
    enemies_killed_count = 0
    coin_count = 0

def update():
    global spawn_timer, spawn_cooldown, spawn_count, max_spawn_count
    global enemies_killed_count
    global max_enemies_on_screen

    game_world.update()
    game_world.handle_collisions()

    if enemies_killed_count >= max_spawn_count:
        import gameclear_mode
        game_framework.change_mode(gameclear_mode)
        return

    current_enemy_count = 0
    if 'girl:enemy' in game_world.collision_pairs:
        current_enemy_count = len(game_world.collision_pairs['girl:enemy'][1])

    if current_enemy_count >= max_enemies_on_screen:
        return

    current_time = get_time()
    if current_time - spawn_timer > spawn_cooldown:
        spawn_timer = current_time

        if random.choice([True, False]):
            e = Enemy(girl)
        else:
            e = Enemy_R(girl)
        e.x = 1700 + random.randint(-50, 50)
        game_world.add_object(e, 4)
        game_world.add_collision_pair('book:enemy', None, e)
        game_world.add_collision_pair('girl:enemy', None, e)


def draw():
    clear_canvas()
    game_world.render()

    font.draw(girl.x - 30, girl.y + 110, f'HP: {girl.hp}', (255, 0, 0))
    font.draw(50, 550, f'KILLS: {enemies_killed_count}', (255, 255, 255))
    font.draw(50, 520, f'COINS: {coin_count}', (255, 255, 255))

    if skill_q_icon and skill_q_icon_bw:
        icon_x, icon_y = 75, 475
        icon_w, icon_h = 50, 50

        current_time = get_time()
        elapsed_time = current_time - girl.last_skill_time
        cooldown = girl.skill_cooldown

        clip_l, clip_b, clip_w, clip_h = 0, 0, 32, 32

        if elapsed_time < cooldown:
            skill_q_icon_bw.clip_draw(clip_l, clip_b, clip_w, clip_h, icon_x, icon_y, icon_w, icon_h)

            remaining_time = cooldown - elapsed_time
            font.draw(icon_x - 5, icon_y - 40, f'{remaining_time:.1f}', (255, 255, 255))
        else:
            skill_q_icon.clip_draw(clip_l, clip_b, clip_w, clip_h, icon_x, icon_y, icon_w, icon_h)

    if skill_e_icon and skill_e_icon_bw:
        icon_x, icon_y = 140, 475
        icon_w, icon_h = 50, 50

        current_time = get_time()

        elapsed_time = current_time - girl.last_skill_e_time
        cooldown = girl.skill_e_cooldown

        clip_l, clip_b, clip_w, clip_h = 0, 0, 32, 32

        if current_time < girl.buff_end_time:
            skill_e_icon.clip_draw(clip_l, clip_b, clip_w, clip_h, icon_x, icon_y, icon_w, icon_h)
            remaining_buff_time = girl.buff_end_time - current_time
            font.draw(icon_x - 5, icon_y - 40, f'{remaining_buff_time:.1f}', (255, 255, 255))

        elif elapsed_time < cooldown:
            skill_e_icon_bw.clip_draw(clip_l, clip_b, clip_w, clip_h, icon_x, icon_y, icon_w, icon_h)
            remaining_time = cooldown - elapsed_time
            font.draw(icon_x - 5, icon_y - 40, f'{remaining_time:.1f}', (255, 255, 255))

        else:
            skill_e_icon.clip_draw(clip_l, clip_b, clip_w, clip_h, icon_x, icon_y, icon_w, icon_h)

    update_canvas()

def finish():
    global skill_q_icon, skill_q_icon_bw, skill_e_icon, skill_e_icon_bw
    game_world.clear()
    skill_q_icon = None
    skill_q_icon_bw = None
    skill_e_icon = None
    skill_e_icon_bw = None

def pause(): pass
def resume(): pass

