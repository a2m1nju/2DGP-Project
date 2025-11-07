from pico2d import *

class Grass:
    def __init__(self):
        self.image = load_image('grass.png')

    def update(self):
        pass

    def draw(self):
        self.image.draw(400, 30)
        self.image.draw(1200, 30)
        draw_rectangle(*self.get_bb()) # 바운딩 박스 그리기

    # 잔디 그 부분을 바운딩
    def get_bb(self):
        return 0, 0, 1600, 50

    # 충돌처리 -> 없으면 오류남
    def handle_collision(self, group, other):
        if group == 'grass:ball':
           pass

