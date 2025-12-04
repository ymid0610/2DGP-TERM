import game_framework
from pico2d import *
import play_mode
from button import *
import game_world

def init():
    global button
    button = Fight(400, 300), Setting(400, 100)
    game_world.add_objects(button, 1)

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
            mouse_x, mouse_y = e.x, 720 - e.y
            # 버튼 클릭 여부 확인
            if button[0].is_clicked(mouse_x, mouse_y):
                game_framework.change_mode(play_mode)
            elif button[1].is_clicked(mouse_x, mouse_y):
                print("Settings button clicked")
