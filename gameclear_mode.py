from pico2d import *
import game_framework
import play_mode
import platform_mode

game_clear_image = None

def init():
    global game_clear_image
    game_clear_image = load_image('./배경/클리어.png')


def finish():
    global game_clear_image
    game_clear_image = None


def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN:
            global clearanim_music
            if clearanim_music:
                clearanim_music.stop()
            game_framework.quit()

def update():
    pass


def draw():
    clear_canvas()
    game_clear_image.draw(800, 300, 1600, 600)
    update_canvas()


def pause():
    pass


def resume():
    pass