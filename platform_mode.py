from pico2d import *
import game_framework
import game_world
import server
from subway import Subway
from merchant import Merchant
import random
import os

font = None
shop_ui = None
shop_active = False

item_database = {
    'hp': [],
    'power': [],
    'speed': []
}

shop_items = []
item_slots = []

def init():
    global font, shop_ui, shop_active, item_database, item_slots

    if shop_ui is None:
        shop_ui = load_image('./UI/상점1.png')

    shop_active = False

    folder_map = {
        'hp': './아이템/상인1',
        'power': './아이템/상인2',
        'speed': './아이템/상인3'
    }

    for m_type, folder_path in folder_map.items():
        item_database[m_type] = [] # 리스트 초기화
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith('.png'):
                    full_path = os.path.join(folder_path, filename)
                    image = load_image(full_path)
                    item_database[m_type].append(image)
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

    if shop_active: return

    if server.girl.x > 1550:
        import play_mode
        game_framework.change_mode(play_mode)

def draw():
    global font

    clear_canvas()
    game_world.render()

    if font is None:
        from pico2d import load_font
        font = load_font('ENCR10B.TTF', 16)

    if shop_active:
        shop_ui.draw(800, 300, 357, 453)

        for i, item_image in enumerate(shop_items):
            if i < len(item_slots):
                x, y = item_slots[i]
                item_image.draw(x, y, 50, 50)

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

    # 전역 shop_items 변수가 현재 상인의 인벤토리를 가리키게 함
    shop_items = merchant.inventory

def handle_events():
    global shop_active
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()

        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                if shop_active:
                    shop_active = False
                else:
                    game_framework.quit()


            elif event.key == SDLK_v:
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
                        server.girl.key_a_down = False
                        server.girl.key_d_down = False
                        server.girl.key_shift_down = False
                        server.girl.dir = 0
                        server.girl.state_machine.cur_state.exit(None)
                        server.girl.state_machine.cur_state = server.girl.IDLE
                        server.girl.state_machine.cur_state.enter(None)

                elif shop_active:
                    shop_active = False

            else:
                if not shop_active:
                    server.girl.handle_event(event)

        elif event.type == SDL_MOUSEBUTTONDOWN:
            if shop_active:
                mx, my = event.x, 600 - 1 - event.y
                handle_shop_click(mx, my)
        else:
            if not shop_active:
                server.girl.handle_event(event)


def handle_shop_click(mx, my):
    pass


def buy_item(item_type, price):
    pass


def pause(): pass
def resume(): pass