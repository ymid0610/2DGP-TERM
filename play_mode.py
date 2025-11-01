import random
from pico2d import *

import game_framework
import game_world

from kirby import Kirby

kirby = None

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            kirby.handle_event(event)

def init():
    global kirby
    kirby = Kirby()
    game_world.add_object(kirby, 1)

def update():
    game_world.update()

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def finish():
    game_world.clear()

def pause(): pass
def resume(): pass

