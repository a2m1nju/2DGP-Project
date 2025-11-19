import random
from pico2d import *

import game_framework
import game_world
import server
import platform_mode

from girl import Girl
from subway import Subway
from enemy import Enemy
from enemy_R import Enemy_R

girl = None
font = None
hp_bar_bg = None
hp_bar_fill = None

skill_q_icon = None
skill_q_icon_bw = None
skill_e_icon = None
skill_e_icon_bw = None

inventory_ui = None
inventory_active = False

spawn_timer = 0.0
spawn_cooldown = 5.0
max_spawn_count = 1
max_enemies_on_screen = 3
coin_count = 0

inventory_font = None

def init():
    global girl, font, spawn_timer, coin_count
    global enemies_killed_count, skill_e_icon, skill_e_icon_bw, skill_q_icon, skill_q_icon_bw
    global inventory_ui, inventory_active, inventory_font
    global hp_bar_bg, hp_bar_fill

    if server.girl is None:
        server.girl = Girl()

    server.girl.bg_scrolling = True

    girl = server.girl
    girl.x = 800
    girl.ground_y = 150
    girl.y = girl.ground_y
    game_world.add_object(server.girl, 4)
    game_world.add_collision_pair('girl:enemy', girl, None)
    game_world.add_collision_pair('fire:girl', None, girl)
    game_world.add_collision_pair('girl:coin', girl, None)
    game_world.add_collision_pair('girl:food', girl, None)

    font = load_font('ENCR10B.TTF', 16)
    inventory_font = load_font('ENCR10B.TTF', 25)

    skill_q_icon = load_image('./이펙트/스킬/Q.png')
    skill_q_icon_bw = load_image('./이펙트/스킬/Q_b.png')

    skill_e_icon = load_image('./이펙트/스킬/E.png')
    skill_e_icon_bw = load_image('./이펙트/스킬/E_b.png')

    if hp_bar_bg is None:
        hp_bar_bg = load_image('./UI/체력바.png')
    if hp_bar_fill is None:
        hp_bar_fill = load_image('./UI/체력줄.png')

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
    coin_count = server.coin_count

    inventory_ui = load_image('./UI/인벤토리1.png')
    inventory_active = False

def handle_events():
    global inventory_active

    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()

        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            if inventory_active:
                inventory_active = False
            else:
                game_framework.quit()

        elif event.type == SDL_KEYDOWN and event.key == SDLK_t:
            inventory_active = not inventory_active
            if inventory_active:
                girl.dir = 0
                girl.key_a_down = False
                girl.key_d_down = False

        elif event.type == SDL_MOUSEBUTTONDOWN:
            if inventory_active:
                mx, my = event.x, 600 - 1 - event.y
                handle_inventory_click(mx, my)

        else:
            if not inventory_active:
                girl.handle_event(event)

def handle_inventory_click(mx, my):
    global inventory_active

    close_btn_x_min = 950
    close_btn_x_max = 985
    close_btn_y_min = 460
    close_btn_y_max = 490

    if (close_btn_x_min <= mx <= close_btn_x_max) and (close_btn_y_min <= my <= close_btn_y_max):
        inventory_active = False

def update():
    global spawn_timer, spawn_cooldown, spawn_count, max_spawn_count
    global enemies_killed_count
    global max_enemies_on_screen

    if inventory_active:
        return

    game_world.update()
    game_world.handle_collisions()

    if enemies_killed_count >= max_spawn_count:
        import gameclear_mode
        server.coin_count = coin_count
        game_framework.change_mode(gameclear_mode)
        return

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

    #font.draw(girl.x - 30, girl.y + 110, f'HP: {girl.hp}', (255, 0, 0))
    if hp_bar_bg and hp_bar_fill:
        bar_x = girl.x
        bar_y = girl.y + 110

        TARGET_WIDTH = 100
        TARGET_HEIGHT = 20

        HORIZONTAL_PADDING = 8
        VERTICAL_PADDING = 10

        FILL_DRAW_WIDTH = TARGET_WIDTH - HORIZONTAL_PADDING
        FILL_DRAW_HEIGHT = TARGET_HEIGHT - VERTICAL_PADDING

        hp_ratio = girl.hp / girl.max_hp
        if hp_ratio < 0: hp_ratio = 0
        if hp_ratio > 1: hp_ratio = 1

        FILL_ORIGINAL_WIDTH = hp_bar_fill.w
        current_clip_width = int(FILL_ORIGINAL_WIDTH * hp_ratio)
        current_draw_width = int(FILL_DRAW_WIDTH * hp_ratio)

        fill_left_edge_x = bar_x - (TARGET_WIDTH / 2) + (HORIZONTAL_PADDING / 2)
        draw_x = fill_left_edge_x + (current_draw_width / 2)

        hp_bar_bg.draw(bar_x, bar_y, TARGET_WIDTH, TARGET_HEIGHT)

        if current_draw_width > 0:
            hp_bar_fill.clip_draw(0, 0, current_clip_width, hp_bar_fill.h, draw_x, bar_y,
                                  current_draw_width,FILL_DRAW_HEIGHT)

    font.draw(50, 550, f'KILLS: {enemies_killed_count}', (255, 255, 255))
    font.draw(50, 520, f'COINS: {coin_count}', (255, 255, 255))

    font.draw(50, 490, f'Lv: {girl.level}', (255, 255, 255))
    font.draw(50, 460, f'EXP: {int(girl.exp)} / {int(girl.max_exp)}', (255, 255, 255))

    if skill_q_icon and skill_q_icon_bw:
        icon_x, icon_y = 250, 475
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
        icon_x, icon_y = 315, 475
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

    if inventory_active:
        inventory_ui.draw(800, 300, 392, 404)

        inv_start_x = 665
        inv_start_y = 410
        inv_gap_x = 67
        inv_gap_y = 67

        for i, item in enumerate(server.girl.inventory):
            row = i // 5
            col = i % 5
            ix = inv_start_x + (col * inv_gap_x)
            iy = inv_start_y - (row * inv_gap_y)

            if 'image' in item:
                item['image'].draw(ix, iy, 40, 40)

        if inventory_font:
            inventory_font.draw(705, 150, f'{coin_count}', (0, 0, 0))

    update_canvas()

def finish():
    global skill_q_icon, skill_q_icon_bw, skill_e_icon, skill_e_icon_bw, inventory_font
    global hp_bar_bg, hp_bar_fill
    game_world.clear()
    skill_q_icon = None
    skill_q_icon_bw = None
    skill_e_icon = None
    skill_e_icon_bw = None
    inventory_font = None
    hp_bar_bg = None
    hp_bar_fill = None

def pause(): pass
def resume(): pass

