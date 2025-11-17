from pico2d import *
import game_framework
import game_world
import server
from subway import Subway
from merchant import Merchant

font = None

def init():
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

def update():
    game_world.update()
    game_world.handle_collisions()

    if server.girl.x > 1550:
        import play_mode
        game_framework.change_mode(play_mode)

def draw():
    clear_canvas()
    game_world.render()

    if font:
        font.draw(50, 520, f'COINS: {server.coin_count}', (255, 255, 255))
        font.draw(server.girl.x - 30, server.girl.y + 110, f'HP: {server.girl.hp}', (255, 0, 0))

    update_canvas()

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            elif event.key == SDLK_SPACE:
                for merchant in game_world.all_objects():
                    if isinstance(merchant, Merchant):
                        if game_world.collide(server.girl, merchant):
                            merchant.try_buy()
            else:
                server.girl.handle_event(event)
        else:
            server.girl.handle_event(event)


def pause(): pass
def resume(): pass