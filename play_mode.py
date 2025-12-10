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

description_ui = None
hovered_item_info = None
item_info_font = None

spawn_timer = 0.0
spawn_cooldown = 4.0
max_spawn_count = 12
max_enemies_on_screen = 3
coin_count = 0

last_click_time = 0.0
last_clicked_index = -1

inventory_font = None
background = None
current_bg_index = 1

is_clearing = False
clearing_timer = 0.0
announcement_sound = None
announcement_font = None
announcement_x = 0
announcement_text = "이번역은 고통역입니다. 내리실 문은 오른쪽입니다."
announcement_bg_image = None
glitch_sound = None
bgm = None

def init():
    global girl, font, spawn_timer, coin_count
    global skill_e_icon, skill_e_icon_bw, skill_q_icon, skill_q_icon_bw
    global inventory_ui, inventory_active, inventory_font
    global hp_bar_bg, hp_bar_fill
    global description_ui, hovered_item_info, item_info_font
    global background, current_bg_index
    global is_clearing, clearing_timer, announcement_sound, announcement_font, announcement_x, announcement_bg_image
    global bgm, glitch_sound

    server.stage_level = 1

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
    game_world.add_collision_pair('girl:poison', girl, None)

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

    background = Subway('./배경/스테이지1/1.png', 800, 300, 1600, 600, 0, is_looping=True)
    current_bg_index = 1

    is_clearing = False
    clearing_timer = 0.0
    announcement_x = 1600
    announcement_font = load_font('ChangwonDangamRound.ttf', 40)

    if announcement_bg_image is None:
        try:
            announcement_bg_image = load_image('./배경/스테이지1/안내배경.png')
        except:
            print("이미지를 찾을 수 없습니다.")
            announcement_bg_image = None

    try:
        announcement_sound = load_wav('./음악/고통역.wav')
        announcement_sound.set_volume(70)
    except:
        print("안내 방송 파일을 찾을 수 없습니다.")
        announcement_sound = None

    try:
        glitch_sound = load_wav('./음악/글리치.wav')
        glitch_sound.set_volume(50)
    except:
        print("글리치 사운드 파일을 찾을 수 없습니다.")
        glitch_sound = None

    bgm = load_music('./음악/스테이지1.wav')
    bgm.set_volume(50)
    bgm.repeat_play()

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
    server.enemies_killed_count = 0
    coin_count = server.coin_count

    inventory_ui = load_image('./UI/인벤토리1.png')
    inventory_active = False

    if description_ui is None:
        description_ui = load_image('./UI/설명창.png')

    if item_info_font is None:
        item_info_font = load_font('ChangwonDangamRound.ttf', 15)


    hovered_item_info = None

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

        elif event.type == SDL_MOUSEMOTION:
            if inventory_active:
                mx, my = event.x, 600 - 1 - event.y
                check_inventory_hover(mx, my)

        else:
            if not inventory_active:
                girl.handle_event(event)

def handle_inventory_click(mx, my):
    global inventory_active
    global last_click_time, last_clicked_index

    close_btn_x_min = 950
    close_btn_x_max = 985
    close_btn_y_min = 460
    close_btn_y_max = 490

    if (close_btn_x_min <= mx <= close_btn_x_max) and (close_btn_y_min <= my <= close_btn_y_max):
        inventory_active = False

    inv_start_x = 665
    inv_start_y = 410
    inv_gap_x = 67
    inv_gap_y = 67

    clicked_index = -1

    for i in range(len(server.girl.inventory)):
        row = i // 5
        col = i % 5
        ix = inv_start_x + (col * inv_gap_x)
        iy = inv_start_y - (row * inv_gap_y)

        if (ix - 20 <= mx <= ix + 20) and (iy - 20 <= my <= iy + 20):
            clicked_index = i
            break

    if clicked_index != -1:
        current_time = get_time()

        if clicked_index == last_clicked_index and (current_time - last_click_time) < 0.5:
            use_inventory_item(clicked_index)
            last_clicked_index = -1
            last_click_time = 0.0

        else:
            last_clicked_index = clicked_index
            last_click_time = current_time
    else:
        last_clicked_index = -1


def use_inventory_item(index):
    global hovered_item_info
    if index < 0 or index >= len(server.girl.inventory):
        return

    item = server.girl.inventory[index]

    is_food = False

    if '상인1' in item['path']:
        is_food = True
    elif item.get('value', 0) > 0 and item.get('stat_type') is None:
        is_food = True

    if is_food:
        recovery = item.get('value', 0)
        server.girl.hp += recovery

        if server.girl.hp > server.girl.max_hp:
            server.girl.hp = server.girl.max_hp

        print(f"아이템 사용: HP {recovery} 회복! 현재 HP: {server.girl.hp}")

        server.girl.inventory.pop(index)
        hovered_item_info = None

    elif '상인3' in item['path'] or 'potion' in item['path']:
        p_type = item.get('stat_type')
        val = item.get('value', 0)
        dur = item.get('duration', 0)

        if p_type == 'perm_q':
            server.girl.q_damage_bonus += val
            print(f"Q 스킬 공격력 영구 증가! (+{val})")
        elif p_type == 'perm_e':
            server.girl.e_duration_bonus += val
            print(f"E 스킬 지속시간 영구 증가! (+{val})")

        elif p_type == 'regen':
            server.girl.activate_buff('regen', val, dur)
        elif p_type == 'speed':
            server.girl.activate_buff('speed', val, dur)
        elif p_type == 'q_buff':
            server.girl.activate_buff('q_buff', val, dur)
        elif p_type == 'defense':
            server.girl.activate_buff('defense', val, dur)
        elif p_type == 'freeze':

            server.freeze_timer = get_time() + dur
            print(f"모든 적이 {dur}초간 멈춥니다!")

        server.girl.inventory.pop(index)
        hovered_item_info = None
    else:
        print("사용할 수 없는 아이템입니다(장비 등).")

def check_inventory_hover(mx, my):
    global inventory_active, hovered_item_info

    if not inventory_active:
        return

    inv_start_x = 665
    inv_start_y = 410
    inv_gap_x = 67
    inv_gap_y = 67

    if server.girl is None or not hasattr(server.girl, 'inventory'):
        return

    hovered_item_info = None

    for i, item in enumerate(server.girl.inventory):
        row = i // 5
        col = i % 5

        ix = inv_start_x + (col * inv_gap_x)
        iy = inv_start_y - (row * inv_gap_y)

        item_bb_x_min = ix - 20
        item_bb_x_max = ix + 20
        item_bb_y_min = iy - 20
        item_bb_y_max = iy + 20

        if (item_bb_x_min <= mx <= item_bb_x_max) and (item_bb_y_min <= my <= item_bb_y_max):
            hovered_item_info = item
            return

def update():
    global spawn_timer, spawn_cooldown, spawn_count, max_spawn_count
    global max_enemies_on_screen
    global current_bg_index
    global is_clearing, clearing_timer, announcement_x, announcement_sound
    global bgm

    if inventory_active:
        return

    game_world.update()
    game_world.handle_collisions()

    new_bg_index = (server.enemies_killed_count // 2) + 1
    if new_bg_index > 6:
        new_bg_index = 6

    if new_bg_index > current_bg_index:
        current_bg_index = new_bg_index
        background.image = load_image(f'./배경/스테이지1/{current_bg_index}.png')

        if glitch_sound:
            glitch_sound.play()

    if server.enemies_killed_count >= max_spawn_count:
        if not is_clearing:
            is_clearing = True
            clearing_timer = get_time()
            if announcement_sound:
                announcement_sound.play()

    if is_clearing:
        announcement_x -= 400 * game_framework.frame_time

        if announcement_x + 800 < 0:
            import platform_mode
            game_framework.change_mode(platform_mode)
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
    if not is_clearing:
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
                                      current_draw_width, FILL_DRAW_HEIGHT)

        font.draw(50, 550, f'KILLS: {server.enemies_killed_count}', (255, 255, 255))
        font.draw(50, 520, f'COINS: {server.coin_count}', (255, 255, 255))
        font.draw(50, 490, f'Lv: {girl.level}', (255, 255, 255))
        font.draw(50, 460, f'EXP: {int(girl.exp)} / {int(girl.max_exp)}', (255, 255, 255))
        font.draw(50, 430, f'MAX HP: {girl.max_hp}', (255, 255, 255))
        font.draw(50, 400, f'ATK: {girl.damage}', (255, 255, 255))

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

    if is_clearing and announcement_bg_image:
        announcement_bg_image.draw(800, 500, 1600, 80)

    if is_clearing and announcement_font:
        announcement_font.draw(announcement_x, 500, announcement_text, (255, 0, 0))

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
            inventory_font.draw(705, 150, f'{server.coin_count}', (0, 0, 0))

    if inventory_active and hovered_item_info and description_ui:
        desc_width, desc_height = 250, 200
        desc_x, desc_y = 460, 200

        description_ui.draw(desc_x, desc_y, desc_width, desc_height)
        desc_text = hovered_item_info['description']

        max_chars_per_line = 20
        line_spacing = 25
        lines = []
        manual_lines = desc_text.split('\n')

        for manual_line in manual_lines:
            current_index = 0
            while current_index < len(manual_line):
                line_segment = manual_line[current_index:current_index + max_chars_per_line].strip()
                if line_segment:
                    lines.append(line_segment)
                current_index += max_chars_per_line

        start_y = desc_y + desc_height / 2 - 20

        for i, line in enumerate(lines):
            y_pos = start_y - (i * line_spacing)
            if y_pos < desc_y - desc_height / 2 + 10:
                break

            x_pos = desc_x - 110

            if item_info_font:
                item_info_font.draw(x_pos, y_pos, line, (0, 0, 0))

    update_canvas()

def finish():
    global skill_q_icon, skill_q_icon_bw, skill_e_icon, skill_e_icon_bw, inventory_font
    global hp_bar_bg, hp_bar_fill
    global bgm, announcement_bg_image, glitch_sound
    game_world.clear()
    skill_q_icon = None
    skill_q_icon_bw = None
    skill_e_icon = None
    skill_e_icon_bw = None
    inventory_font = None
    hp_bar_bg = None
    hp_bar_fill = None
    bgm = None
    announcement_bg_image = None
    glitch_sound = None

def pause(): pass
def resume(): pass

