from pico2d import *
import game_framework
import game_world
import server
from subway import Subway
from merchant import Merchant
import random
import os
import server

font = None
shop_ui = None
shop_active = False
inventory_ui = None
inventory_active = False
inventory_font = None
description_ui = None
hovered_item_info = None
item_info_font = None

item_database = {
    'hp': [],
    'power': [],
    'potion': []
}

HP_ITEM_VALUES = {
    '감튀': 15,
    '샌드위치2': 25,
    '당고': 20,
    '비빔밥': 60,
    '사과': 10,
    '주먹밥': 30,
    '체리': 5,
    '치즈버거': 35,
    '토마토': 5,
    '피자': 50,
    '김밥': 40
}

POWER_ITEM_INFO = {
    '망토': {'type': 'range', 'value': 150},
    '모자1': {'type': 'max_hp', 'value': 5},
    '모자2': {'type': 'damage', 'value': 1},
    '모자3': {'type': 'max_hp', 'value': 45},
    '반지1': {'type': 'range', 'value': 100},
    '반지2': {'type': 'damage', 'value': 5},
    '반지3': {'type': 'damage', 'value': 10},
    '방패1': {'type': 'max_hp', 'value': 40},
    '방패2': {'type': 'damage', 'value': 15},
    '방패3': {'type': 'max_hp', 'value': 30},
    '왕관': {'type': 'damage', 'value': 20},
    '의상1': {'type': 'range', 'value': 50},
    '의상2': {'type': 'damage', 'value': 8},
}

POTION_ITEM_INFO = {
    '포션1': {'type': 'regen', 'value': 2, 'duration': 10.0},      # 치유: 10초간 초당 2 회복 (총 20)
    '포션2': {'type': 'q_buff', 'value': 5, 'duration': 15.0},     # 번개: 15초간 Q 데미지 +5
    '포션3': {'type': 'freeze', 'value': 0, 'duration': 5.0},      # 서리: 5초간 적 정지
    '포션4': {'type': 'regen', 'value': 5, 'duration': 10.0},      # 치유LV2: 10초간 초당 5 회복 (총 50)
    '포션5': {'type': 'speed', 'value': 1.5, 'duration': 10.0},    # 신속: 10초간 이속 1.5배
    '포션6': {'type': 'q_buff', 'value': 10, 'duration': 15.0},    # 번개LV2
    '포션7': {'type': 'speed', 'value': 2.0, 'duration': 10.0},    # 신속LV2
    '포션8': {'type': 'defense', 'value': 0.5, 'duration': 15.0},  # 스톤스킨: 15초간 받는 피해 50% 감소
    '포션9': {'type': 'perm_q', 'value': 2.0, 'duration': 0},      # 태양: 영구 Q 데미지 +2
    '포션10': {'type': 'perm_e', 'value': 2.0, 'duration': 0},     # 달: 영구 E 지속시간 +2초
    '포션11': {'type': 'freeze', 'value': 0, 'duration': 10.0},    # 서리LV2
}

shop_items = []
item_slots = []

def get_item_description(filename, m_type):
    name = os.path.splitext(filename)[0]

    if m_type == 'hp':
        if '감튀' in name:
            desc = ("[감자튀김]\n"
                    "저는 맘스터치 감튀를 좋아합니다")
        elif '샌드위치2' in name:
            desc = ("[샌드위치]\n"
                    "서브웨이 에그마요에 에그마요 추가")
        elif '당고' in name:
            desc = ("[당고]\n"
                    "맛있는지 잘 모르겠다")
        elif '비빔밥' in name:
            desc = ("[비빔밥]\n"
                    "열무비빔밥 vs 육회비빔밥")
        elif '사과' in name:
            desc = ("[사과]\n"
                    "사과드립니다.")
        elif '주먹밥' in name:
            desc = ("[삼각김밥]\n"
                    "CU에 파는 반숙계란 버터간장밥을 아십니까?")
        elif '체리' in name:
            desc = ("[체리]\n"
                    "정신 체리세요[국산].")
        elif '치즈버거' in name:
            desc = ("[치즈버거]\n"
                    "띠드버거 머꼬 시퍼여 띠드버거어~ 띠드버거 사쥬세요 띠드버거~"
                    "나 띠드 대따 조아하는거 알디?? 내껀 띠드 두자앙?!")
        elif '토마토' in name:
            desc = ("[토마토]\n"
                    "토맛토마토 VS 토마토맛토")
        elif '피자' in name:
            desc = ("[피자]"
                    "핫소스 5개 추가")
        elif '김밥' in name:
            desc = ("[김밥]\n"
                    "김천국밥")
        else:
            desc = "체력을 회복시켜주는 음식입니다."

        recovery = 0
        for key, val in HP_ITEM_VALUES.items():
            if key in name:
                recovery = val
                break
        if recovery > 0:
            desc += f"\n[HP +{recovery}]"

    elif m_type == 'power':
        if '망토' in name:
            desc = "마법사가 될 것 같은 느낌"
        elif '모자1' in name:
            desc = "고양이가 되어보세요."
        elif '모자2' in name:
            desc = ("너 테레비도 안 보냐? 테레비도 안 봐?"
                    "너 뉴스도 안 보지?"
                    "지금 대침체 모르냐? 금융 위기 모르냐?"
                    "왜 나만 계속 갈구냐 왜 갈구냐고")
        elif '모자3' in name:
            desc = "리나메"
        elif '반지1' in name:
            desc = "오른손 중지의 의미는 성공"
        elif '반지2' in name:
            desc = "왼손 검지의 의미는 신념 "
        elif '반지3' in name:
            desc = "오른손 약지의 의미는 정신력"
        elif '방패1' in name:
            desc = "엄청난 태풍을 부르는 금창의 용사"
        elif '방패2' in name:
            desc = "망치 나가신다!"
        elif '방패3' in name:
            desc = "놀랍게도 더이상 쓸 말이 없습니다"
        elif '왕관' in name:
            desc = "KING 너희들 나 못 이겨 "
        elif '의상1' in name:
            desc = "저는 흰색 옷을 입으면 구마 당합니다"
        elif '의상2' in name:
            desc = "왠지 도둑질을 잘 할 것 같은 복장"
        else:
            desc = "공격력 또는 방어력을 올려주는 장비입니다."

        found_info = None
        for key, info in POWER_ITEM_INFO.items():
            if key in name:
                found_info = info
                break

        if found_info:
            val = found_info['value']
            if found_info['type'] == 'damage':
                desc += f"\n[공격력 +{val}]"
            elif found_info['type'] == 'max_hp':
                desc += f"\n[최대체력 +{val}]"
            elif found_info['type'] == 'range':
                desc += f"\n[사거리 +{val}]"

    elif m_type == 'potion':
        if '포션1' == name:
            desc = "치유의 포션" # 일정시간동안 체력회복
        elif '포션2' == name:
            desc = "번개의 포션" # 일정시간동안 q 스킬 공격력 증가
        elif '포션3' == name:
            desc = "서리의 포션" # 일정시간동안 적 멈춤
        elif '포션4' == name:
            desc = "치유의 포션 LV.2"
        elif '포션5' == name:
            desc = "신속의 포션" # 일정시간동안 이동속도 증가
        elif '포션6' == name:
            desc = "번개의 포션 LV.2"
        elif '포션7' == name:
            desc = "신속의 포션 LV.2"
        elif '포션9' == name:
            desc = "태양의 포션" #영구적으로 q 스킬 공격력 증가
        elif '포션8' == name:
            desc = "스톤 스킨의 포션" # 일정시간동안 방어력 증가
        elif '포션10' == name:
            desc = "달의 포션" # 영구적으로 e 스킬 지속시간 증가
        elif '포션11' == name:
            desc = "서리의 포션 LV.2"
        else:
            desc = "알 수 없는 포션입니다."

    return f"{desc}"

def init():
    global font, shop_ui, shop_active, item_database, item_slots
    global inventory_ui, inventory_active, inventory_font
    global description_ui, hovered_item_info , item_info_font

    hovered_item_info = None

    if shop_ui is None:
        shop_ui = load_image('./UI/상점1.png')

    if inventory_ui is None:
        inventory_ui = load_image('./UI/인벤토리1.png')

    if description_ui is None:
        description_ui = load_image('./UI/설명창.png')

    if item_info_font is None:
        item_info_font = load_font('ChangwonDangamRound.ttf', 15)

    if inventory_font is None:
        inventory_font = load_font('ENCR10B.TTF', 25)

    if font is None:
        font = load_font('ENCR10B.TTF', 20)

    if server.girl:
        server.girl.state_machine.cur_state = server.girl.IDLE
        server.girl.IDLE.enter(None)
        server.girl.bg_scrolling = False

    shop_active = False
    inventory_active = False

    folder_map = {
        'hp': './아이템/상인1',
        'power': './아이템/상인2',
        'potion': './아이템/상인3'
    }

    for m_type, folder_path in folder_map.items():
        item_database[m_type] = []
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith('.png'):
                    full_path = os.path.join(folder_path, filename)
                    image = load_image(full_path)

                    description = get_item_description(filename, m_type)
                    name = os.path.splitext(filename)[0]

                    item_value = 0
                    item_stat_type = None

                    if m_type == 'hp':
                        for key, val in HP_ITEM_VALUES.items():
                            if key in name:
                                item_value = val
                                break
                        if item_value == 0: item_value = 10

                    if m_type == 'hp':
                        price = item_value//2 + random.randint(5, 15)
                    else:
                        price = random.randint(10, 30)

                    if m_type == 'power':
                        item_value = 5
                        item_stat_type = 'max_hp'

                        for key, info in POWER_ITEM_INFO.items():
                            if key in name:
                                item_value = info['value']
                                item_stat_type = info['type']
                                break

                        if item_stat_type == 'damage':
                            price = item_value * 10 + random.randint(10, 30)
                        elif item_stat_type == 'range':
                            price = int(item_value * 0.5) + random.randint(20, 40)
                        else:
                            price = item_value + random.randint(20, 40)

                    if m_type == 'potion':
                        item_value = 0
                        item_stat_type = 'none'
                        item_duration = 0

                        if name in POTION_ITEM_INFO:
                            info = POTION_ITEM_INFO[name]
                            item_stat_type = info['type']
                            item_value = info['value']
                            item_duration = info['duration']

                        if 'perm' in item_stat_type:
                            price = 150 + random.randint(0, 50)
                        else:
                            price = 30 + random.randint(0, 20)



                    item_data = {'image': image,
                                 'price': price,
                                 'path': full_path,
                                 'description': description,
                                 'value': item_value,
                                 'stat_type': item_stat_type,
                                 'duration': item_duration if m_type == 'potion' else 0}
                    item_database[m_type].append(item_data)
        else:
            print(f"Warning: Folder not found - {folder_path}")

    start_x = 700
    start_y = 448
    gap_x = 97
    gap_y = 175

    item_slots = [
        (start_x, start_y), (start_x + gap_x, start_y), (start_x + gap_x * 2, start_y),
        (start_x, start_y - gap_y), (start_x + gap_x, start_y - gap_y), (start_x + gap_x * 2, start_y - gap_y)
    ]

    server.subway = Subway('./배경/플랫폼.png', 800, 300, 1600, 600, 0, is_looping=False)

    if server.girl:
        game_world.add_object(server.girl, 4)
        server.girl.x = 100
        server.girl.ground_y = 180
        server.girl.y = 180
        server.girl.state_machine.cur_state = server.girl.IDLE

    server.girl.bg_scrolling = False

    m1 = Merchant(500, 160, 'hp')
    game_world.add_object(m1, 3)

    m2 = Merchant(900, 160, 'power')
    game_world.add_object(m2, 3)

    m3 = Merchant(1300, 160, 'potion')
    game_world.add_object(m3, 3)

    game_world.add_collision_pair('girl:merchant', server.girl, m1)
    game_world.add_collision_pair('girl:merchant', server.girl, m2)
    game_world.add_collision_pair('girl:merchant', server.girl, m3)

def finish():
    game_world.clear()

    global shop_items
    shop_items = []

def update():
    game_world.update()
    game_world.handle_collisions()

    if shop_active or inventory_active:
        return

    if server.girl.x > 1550:
        if server.stage_level == 1:
            import stage2_mode
            game_framework.change_mode(stage2_mode)

        elif server.stage_level == 2:
            import play_mode
            server.stage_level = 1
            game_framework.change_mode(play_mode)

        else:
            # 기본값
            import play_mode
            game_framework.change_mode(play_mode)

def draw():
    global font, inventory_font, hovered_item_info, item_info_font

    clear_canvas()
    game_world.render()

    if font is None:
        from pico2d import load_font
        font = load_font('ENCR10B.TTF', 20)

    if shop_active:
        shop_ui.draw(800, 300, 357, 453)

        for i, item in enumerate(shop_items):
            if i < len(item_slots):
                x, y = item_slots[i]
                item['image'].draw(x, y, 50, 50)
                font.draw(x - 15, y - 47, f'{item["price"]}G', (0, 0, 0))

        font.draw(705, 117, f'{server.coin_count}', (0, 0, 0))

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

            item['image'].draw(ix, iy, 40, 40)

        if inventory_font:
            inventory_font.draw(705, 150, f'{server.coin_count}', (0, 0, 0))

    if hovered_item_info and description_ui:
        desc_width, desc_height = 250, 200

        if shop_active:
            desc_x, desc_y = 480, 200
        elif inventory_active:
            desc_x, desc_y = 460, 200
        else:
            desc_x, desc_y = 480, 200

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
            else:
                font.draw(x_pos, y_pos, line, (0, 0, 0))

    update_canvas()


def update_shop_items(merchant):
    global shop_items

    if not hasattr(merchant, 'inventory'):
        merchant.inventory = []

        pool = item_database.get(merchant.item_type, [])

        if pool:
            count = min(len(pool), 6)
            merchant.inventory = random.sample(pool, count)

            while len(merchant.inventory) < 6:
                merchant.inventory.append(random.choice(pool))

    shop_items = merchant.inventory

def check_shop_hover(mx, my):
    global shop_active, shop_items, item_slots, hovered_item_info

    hovered_item_info = None

    if not shop_active:
        return

    for i, slot_pos in enumerate(item_slots):
        if i < len(shop_items):
            sx, sy = slot_pos

            item_bb_x_min = sx - 25
            item_bb_x_max = sx + 25
            item_bb_y_min = sy - 25
            item_bb_y_max = sy + 25

            if (item_bb_x_min <= mx <= item_bb_x_max) and (item_bb_y_min <= my <= item_bb_y_max):
                hovered_item_info = shop_items[i]
                return

    for i, slot_pos in enumerate(item_slots):
        if i < len(shop_items):
            sx, sy = slot_pos
            price_bb_x_min = sx - 30
            price_bb_x_max = sx + 30
            price_bb_y_min = sy - 105
            price_bb_y_max = sy - 80

            if (price_bb_x_min <= mx <= price_bb_x_max) and (price_bb_y_min <= my <= price_bb_y_max):
                hovered_item_info = shop_items[i]
                return

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

def handle_events():
    global shop_active, inventory_active, hovered_item_info

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()

        elif event.type == SDL_MOUSEMOTION:
            mx, my = event.x, 600 - 1 - event.y
            hovered_item_info = None
            if shop_active:
                check_shop_hover(mx, my)
            elif inventory_active:
                check_inventory_hover(mx, my)

        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                if shop_active:
                    shop_active = False
                    hovered_item_info = None
                elif inventory_active:
                    inventory_active = False
                    hovered_item_info = None
                else:
                    game_framework.quit()

            elif event.key == SDLK_v:
                if not inventory_active:
                    target_merchant = None
                    for obj in game_world.all_objects():
                        if isinstance(obj, Merchant):
                            if game_world.collide(server.girl, obj):
                                target_merchant = obj
                                break

                    if target_merchant:
                        if shop_active:
                            shop_active = False
                            hovered_item_info = None
                        else:
                            shop_active = True
                            update_shop_items(target_merchant)
                            server.girl.dir = 0
                            server.girl.key_a_down = False
                            server.girl.key_d_down = False
                            server.girl.state_machine.cur_state.exit(None)
                            server.girl.state_machine.cur_state = server.girl.IDLE
                            server.girl.state_machine.cur_state.enter(None)
                    elif shop_active:
                        shop_active = False
                        hovered_item_info = None


            elif event.key == SDLK_t:
                if not shop_active:
                    inventory_active = not inventory_active
                    if inventory_active:
                        server.girl.dir = 0
                        server.girl.key_a_down = False
                        server.girl.key_d_down = False

            else:
                hovered_item_info = None
                if not shop_active and not inventory_active:
                    server.girl.handle_event(event)


        elif event.type == SDL_MOUSEBUTTONDOWN:
            mx, my = event.x, 600 - 1 - event.y

            if shop_active:
                handle_shop_click(mx, my)
            elif inventory_active:
                handle_inventory_click(mx, my)

        else:
            if not shop_active and not inventory_active:
                server.girl.handle_event(event)


def handle_shop_click(mx, my):
    global shop_active

    close_btn_x_min = 940
    close_btn_x_max = 960
    close_btn_y_min = 490
    close_btn_y_max = 525

    if (close_btn_x_min <= mx <= close_btn_x_max) and (close_btn_y_min <= my <= close_btn_y_max):
        shop_active = False
        return

    for i, slot_pos in enumerate(item_slots):
        if i < len(shop_items):
            sx, sy = slot_pos
            if (sx - 30 <= mx <= sx + 30) and (sy - 105 <= my <= sy - 80):
                buy_item(i)
                break


def handle_inventory_click(mx, my):
    global inventory_active

    close_btn_x_min = 950
    close_btn_x_max = 985
    close_btn_y_min = 460
    close_btn_y_max = 490

    if (close_btn_x_min <= mx <= close_btn_x_max) and (close_btn_y_min <= my <= close_btn_y_max):
        inventory_active = False

def buy_item(index):
    global shop_items

    if index < 0 or index >= len(shop_items):
        return

    item = shop_items[index]

    if server.coin_count >= item['price']:
        server.coin_count -= item['price']
        server.girl.inventory.append(item)

        if 'stat_type' in item and 'value' in item:
            if item['stat_type'] == 'max_hp':
                server.girl.max_hp += item['value']
                server.girl.hp += item['value']
                print(f"최대 체력 증가! {server.girl.max_hp}")

            elif item['stat_type'] == 'damage':
                server.girl.damage += item['value']
                print(f"공격력 증가! {server.girl.damage}")

            elif item['stat_type'] == 'range':
                server.girl.attack_range += item['value']
                print(f"사거리 증가! {server.girl.attack_range}")

        shop_items.pop(index)

    else:
        print("돈이 부족합니다!")


def pause(): pass
def resume(): pass