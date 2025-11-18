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
inventory_ui = None
inventory_active = False
inventory_font = None

item_database = {
    'hp': [],
    'power': [],
    'speed': []
}

shop_items = []
item_slots = []

def init():
    global font, shop_ui, shop_active, item_database, item_slots
    global inventory_ui, inventory_active, inventory_font

    if shop_ui is None:
        shop_ui = load_image('./UI/상점1.png')

    if inventory_ui is None:
        inventory_ui = load_image('./UI/인벤토리1.png')

    if inventory_font is None:
        inventory_font = load_font('ENCR10B.TTF', 25)

    if font is None:
        font = load_font('ENCR10B.TTF', 20)

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

                    item_data = {'image': image, 'price': price, 'path': full_path}
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
    global font, inventory_font

    clear_canvas()
    game_world.render()

    if font is None:
        from pico2d import load_font
        font = load_font('ENCR10B.TTF', 25)

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


def handle_events():
    global shop_active, inventory_active  # [추가]

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()

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
            if shop_active:
                mx, my = event.x, 600 - 1 - event.y
                handle_shop_click(mx, my)

        else:
            if not shop_active and not inventory_active:
                server.girl.handle_event(event)


def handle_shop_click(mx, my):
    for i, slot_pos in enumerate(item_slots):
        if i < len(shop_items):
            sx, sy = slot_pos
            if (sx - 30 <= mx <= sx + 30) and (sy - 105 <= my <= sy - 80):
                buy_item(i)
                break


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