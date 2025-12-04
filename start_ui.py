import game_framework
from pico2d import *
import play_mode
from button import *
import game_world

mouse_x, mouse_y = 0, 0
# 파이트 버튼 객체 생성

def init():
    global button
    button = ButtonFight(400, 300)
    game_world.add_object(button, 1)

def finish():
    global button
    game_world.remove_object(button)
    del button

def update():
    pass

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def handle_events():
    event = get_events()
    # 마우스 클릭 및 위치 이벤트 감지
    for e in event:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_MOUSEBUTTONDOWN:
            mouse_x, mouse_y = e.x, e.y
            if button.is_clicked(mouse_x, 720 - mouse_y):
                game_framework.change_mode(play_mode)
