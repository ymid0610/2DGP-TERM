import random
from pico2d import *

import game_framework
import game_world

from kirby import Kirby
from grass import Grass, Floor

kirby = None
grass = None

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
    global floor
    floor = Floor()
    game_world.add_object(floor, 0)
    game_world.add_collision_pair('grass:kirby', floor, None)

    global grass
    grass = Grass()
    game_world.add_object(grass, 0)
    game_world.add_collision_pair('grass:kirby', grass, None)

    global kirby
    kirby = Kirby()
    game_world.add_object(kirby, 1)
    game_world.add_collision_pair('grass:kirby', None, kirby)
    #game_world.add_collision_pair('kirby:AI_kirby', kirby, None)

def update():
    game_world.update()
    game_world.handle_collision()

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def finish():
    game_world.clear()

def pause(): pass
def resume(): pass

