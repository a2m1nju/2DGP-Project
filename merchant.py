from pico2d import *
import game_world
import game_framework
import server


class Merchant:
    images = {}

    animation_info = {
        'hp': {
            'path': './상인/상인1.png',
            'height': 29,
            'sizes': [(0, 19), (31, 20), (62, 21), (93, 23)],
            'fps': 7
        },
        'power': {
            'path': './상인/상인2.png',
            'height': 28,
            'sizes': [(0, 23), (32, 23), (63, 24), (95, 25)],
            'fps': 7
        },
        'speed': {
            'path': './상인/상인3.png',
            'height': 28,
            'sizes': [(0, 19), (31, 20), (62, 21), (93, 23)],
            'fps': 7
        }
    }

    def __init__(self, x, y, item_type):
        self.x, self.y = x, y
        self.item_type = item_type
        self.font = load_font('ENCR10B.TTF', 16)

        info = Merchant.animation_info[self.item_type]

        if self.item_type not in Merchant.images:
            Merchant.images[self.item_type] = load_image(info['path'])
        self.image = Merchant.images[self.item_type]

        self.sizes = info['sizes']
        self.height = info['height']
        self.fps = info.get('fps', 7)
        self.frame = 0.0

        if self.item_type == 'hp':
            self.price = 30
            self.desc = "HP +30"
        elif self.item_type == 'power':
            self.price = 50
            self.desc = "Power UP"
        else:
            self.price = 40
            self.desc = "Speed UP"

    def update(self):
        self.frame = (self.frame + self.fps * game_framework.frame_time) % len(self.sizes)

    def draw(self):
        left, width = self.sizes[int(self.frame)]
        self.image.clip_draw(left, 0, width, self.height, self.x, self.y, 60, 90)

        self.font.draw(self.x - 20, self.y + 60, f'{self.price} G', (255, 255, 0))
        self.font.draw(self.x - 30, self.y - 60, self.desc, (255, 255, 255))

    def get_bb(self):
        return self.x - 30, self.y - 45, self.x + 30, self.y + 45

    def handle_collision(self, group, other):
        pass

    def try_buy(self):
        if server.coin_count >= self.price:
            server.coin_count -= self.price
            if server.girl:
                if self.item_type == 'hp':
                    max_hp = getattr(server.girl, 'max_hp', 100)
                    server.girl.hp = min(max_hp, server.girl.hp + 30)

                elif self.item_type == 'power':
                    if hasattr(server.girl, 'attack_power'):
                        server.girl.attack_power += 1
                    else:
                        print("Error: Girl 객체에 attack_power 속성이 없습니다.")

                elif self.item_type == 'speed':
                    pass

            return True
        return False