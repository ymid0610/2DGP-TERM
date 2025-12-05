import random
from pico2d import *

import game_framework
import game_world

from kirby import Kirby
from grass import Grass, Floor
from background import Ground

import common

def handle_events():
    event_list = get_events()
    arrow_keys = (SDLK_LEFT, SDLK_RIGHT, SDLK_UP, SDLK_DOWN)
    wasd_keys = (SDLK_w, SDLK_a, SDLK_s, SDLK_d)

    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        if event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
            return
        # 키 입력은 지정한 키셋에 따라 분기
        if event.type in (SDL_KEYDOWN, SDL_KEYUP):
            # 방향키 또는 우측 컨트롤 -> kirby1
            if event.key in arrow_keys or event.key == SDLK_RCTRL:
                if common.kirby1 is not None:
                    common.kirby1.handle_event(event)
                continue
            # WASD 또는 좌측 컨트롤 -> kirby2
            if event.key in wasd_keys or event.key == SDLK_LCTRL:
                if common.kirby2 is not None:
                    common.kirby2.handle_event(event)
                continue
        # 기타 이벤트(마우스 등)는 기본적으로 kirby로 전달
        if common.kirby1 is not None:
            common.kirby1.handle_event(event)

def init():
    common.background = Ground()
    game_world.add_object(common.background, 0)

    common.floor = Floor()
    game_world.add_object(common.floor, 0)
    game_world.add_collision_pair('grass:kirby', common.floor, None)

    common.grass = Grass()
    game_world.add_object(common.grass, 0)
    game_world.add_collision_pair('grass:kirby', common.grass, None)


    common.kirby1 = Kirby()
    game_world.add_object(common.kirby1, 1)
    game_world.add_collision_pair('grass:kirby', None, common.kirby1)
    game_world.add_collision_pair('kirby1:kirby2', common.kirby1, None)

    common.kirby2 = Kirby()
    common.kirby2.x = -20.0
    game_world.add_object(common.kirby2, 1)
    game_world.add_collision_pair('grass:kirby', None, common.kirby2)
    game_world.add_collision_pair('kirby1:kirby2', None, common.kirby2)

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

