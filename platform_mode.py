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
    'speed': []
}

shop_items = []
item_slots = []

def get_item_description(filename, m_type):
    name = os.path.splitext(filename)[0]

    if m_type == 'hp':
        if '감튀' in name:
            desc = "저는 맘스터치 감튀를 좋아합니다"
        elif '샌드위치2' in name:
            desc = "서브웨이 에그마요에 에그마요 추가"
        elif '당고' in name:
            desc = "맛있는지 잘 모르겠다"
        elif '비빔밥' in name:
            desc = "열무비빔밥 vs 육회비빔밥"
        elif '사과' in name:
            desc = "사과드립니다."
        elif '주먹밥' in name:
            desc = "CU에 파는 반숙계란 버터간장밥을 아십니까?"
        elif '체리' in name:
            desc = "정신 체리세요[국산]."
        elif '치즈버거' in name:
            desc = ("띠드버거 머꼬 시퍼여 띠드버거어~ 띠드버거 사쥬세요 띠드버거~"
                    "나 띠드 대따 조아하는거 알디?? 내껀 띠드 두자앙?!")
        elif '토마토' in name:
            desc = "저는 실제로 2달동안 토마토만 먹은적이 있습니다"
        elif '피자' in name:
            desc = "핫소스 5개 추가"
        else:
            desc = "체력을 회복시켜주는 음식입니다."

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

    elif m_type == 'speed':
        if '포션1' in name:
            desc = "치유의 포션"
        if '포션2' in name:
            desc = "번개의 포션"
        if '포션3' in name:
            desc = "서리의 포션"
        if '포션4' in name:
            desc = "치유의 포션 LV.2"
        if '포션5' in name:
            desc = "신속의 포션"
        if '포션6' in name:
            desc = "번개의 포션 LV.2"
        if '포션7' in name:
            desc = "신속의 포션 LV.2"
        if '포션9' in name:
            desc = "태양의 포션"
        if '포션8' in name:
            desc = "스톤 스킨의 포션"
        if '포션10' in name:
            desc = "달의 포션"
        if '포션11' in name:
            desc = "서리의 포션 LV.2"
        else:
            desc = "이동 속도를 올려주는 아이템입니다."

    return f"<{name}> : {desc}"

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
        item_info_font = load_font('ChangwonDangamRound.ttf', 20)

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
        'speed': './아이템/상인3'
    }

    for m_type, folder_path in folder_map.items():
        item_database[m_type] = []
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith('.png'):
                    full_path = os.path.join(folder_path, filename)
                    image = load_image(full_path)

                    price = random.randint(10, 30)
                    description = get_item_description(filename, m_type)

                    item_data = {'image': image, 'price': price, 'path': full_path, 'description': description}
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

    m3 = Merchant(1300, 160, 'speed')
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
        desc_x, desc_y = 480, 200
        desc_width, desc_height = 250, 100

        description_ui.draw(desc_x, desc_y, desc_width, desc_height)

        desc_text = hovered_item_info['description']

        item_info_font.draw(desc_x - 110, desc_y + 10, desc_text, (0, 0, 0))

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

def handle_events():
    global shop_active, inventory_active

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()

        elif event.type == SDL_MOUSEMOTION:
            mx, my = event.x, 600 - 1 - event.y
            if shop_active:
                check_shop_hover(mx, my)

        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                if shop_active:
                    shop_active = False
                elif inventory_active:
                    inventory_active = False
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
                        shop_active = not shop_active
                        if shop_active:
                            update_shop_items(target_merchant)
                            server.girl.dir = 0

                            server.girl.key_a_down = False
                            server.girl.key_d_down = False
                            server.girl.state_machine.cur_state.exit(None)
                            server.girl.state_machine.cur_state = server.girl.IDLE
                            server.girl.state_machine.cur_state.enter(None)
                    elif shop_active:
                        shop_active = False

            elif event.key == SDLK_t:
                if not shop_active:
                    inventory_active = not inventory_active
                    if inventory_active:
                        server.girl.dir = 0
                        server.girl.key_a_down = False
                        server.girl.key_d_down = False

            else:
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

        shop_items.pop(index)

    else:
        print("돈이 부족합니다!")


def pause(): pass
def resume(): pass