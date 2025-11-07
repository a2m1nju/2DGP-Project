import random
from pico2d import *

import game_framework
import game_world

from boy import Boy
from grass import Grass
from ball import Ball
from zombie import Zombie

boy = None

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            boy.handle_event(event)

def init():
    global boy

    zombies = [Zombie() for i in range(4)]
    game_world.add_objects(zombies, 1)

    grass = Grass()
    game_world.add_object(grass, 0)
    # 추가
    game_world.add_collision_pair('grass:ball', grass, None)

    boy = Boy()
    game_world.add_object(boy, 1)

    # 바닥에 공 배치
    global balls
    balls = [Ball(random.randint(300, 1600), 60, 0) for i in range(20)]
    game_world.add_objects(balls, 1)

    # 충돌검사가 필요한 페어를 등록
    game_world.add_collision_pair('boy:ball', boy, None) # [[boy],[]]
    for ball in balls:
        game_world.add_collision_pair('boy:ball', None, ball) # [[boy],[ball1, ball2, ...]]




def update():
    game_world.update()
    game_world.handle_collisions()
    # 게임 내 모든 객체가 업뎃이 끝나서 그에 따른 충돌 검사 필요
    # 복잡해질수록 이렇게 쓰지 않음 -> 객체지향방법 : 충돌 검사 담당 객체를 따로 만듦
    #for ball in balls.copy(): # copy()를 사용해서 for문 도는 중에 리스트에서 제거해도 문제 없게 함
        #if game_world.collide(boy, ball):
            #print('COLLISION boy : ball')
            #boy.ball_count += 1 # 소년이 가지고 있는 볼 카운트 증가
            #game_world.remove_object(ball) # 이것만 있으면 오류 생김
            # 게임 월드 안에 골이 있다가 삭제되서 없어지는 거 -> balls 리스트 안에는 남아있음
            # -> balls 리스트 안에도 제거 필요
            #balls.remove(ball) # 근데 문제가 있긴함 -> for문 도는 중에 리스트에서 제거하면 안좋음



def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def finish():
    game_world.clear()

def pause(): pass
def resume(): pass

