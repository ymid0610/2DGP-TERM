from pico2d import *
from kirby import Kirby
import game_world

def handle_events():
    global running
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            running = False
        else:
            kirby.handle_event(event)

def reset_world():
    global kirby
    kirby = Kirby()
    game_world.add_object(kirby, 1)

def update_world():
    game_world.update()

def render_world():
    clear_canvas()
    game_world.render()
    update_canvas()

running = True
open_canvas()
reset_world()

# game loop
while running:
    handle_events()
    update_world()
    render_world()
    delay(0.01)

# finalization code
close_canvas()