from pico2d import *
import game_world
import game_framework
import server


class Merchant:
    images = None

    def __init__(self, x, y, item_type):
        if Merchant.images is None:
            Merchant.images = {
                'hp': load_image('./상인/상인1.png'),
                'power': load_image('./상인/상인2.png'),
                'item': load_image('./상인/상인3.png')
            }
        self.x, self.y = x, y
        self.item_type = item_type
        self.font = load_font('ENCR10B.TTF', 16)

    def update(self):
        pass

    def draw(self):
        pass

    def get_bb(self):
        return self.x - 30, self.y - 45, self.x + 30, self.y + 45

    def handle_collision(self, group, other):
        pass

    def try_buy(self):
        pass