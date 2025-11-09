from pico2d import *
import game_framework
import play_mode

def init():
    global game_over_image
    game_over_image = load_image('./배경/게임오버.png')


def finish():
    global game_over_image
    game_over_image = None


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
            else:
                game_framework.change_mode(play_mode)

def update():
    pass


def draw():
    clear_canvas()
    game_over_image.draw(800, 300, 1600, 600)

    update_canvas()


def pause():
    pass


def resume():
    pass