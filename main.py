from pico2d import open_canvas, delay, close_canvas
import game_framework

#import play_mode as start_mode
import start_mode
import play_mode
import stage2_mode
import stage3_mode
import intro_mode


open_canvas(1600, 600)
game_framework.run(start_mode)
close_canvas()
