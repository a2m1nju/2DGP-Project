from pico2d import *
import game_framework
import game_world
import play_mode
import server
from subway import Subway
from merchant import Merchant


def init():
    server.subway = Subway('./배경/플랫폼.png', 800, 300, 1600, 600, 0, is_looping=False)
    pass


def finish():
    pass

def update():
    pass


def draw():
    pass


def handle_events():
    pass


def pause(): pass
def resume(): pass