import game_framework
from pico2d import *
import select_character
from button import Fight, Setting
import game_world

SCREEN_HEIGHT = 720

buttons = []
clicked_button = None

def init():
    global buttons, clicked_button
    buttons = [Fight(400, 300), Setting(400, 100)]
    game_world.add_objects(buttons, 1)
    clicked_button = None

def finish():
    game_world.clear()
    buttons.clear()

def select_button(index):
    """선택 인덱스를 설정하고 버튼들의 clicked 상태를 갱신한다."""
    global clicked_button
    clicked_button = index
    for i, b in enumerate(buttons):
        b.clicked = (i == clicked_button)

def clear_selection():
    global clicked_button
    clicked_button = None
    for b in buttons:
        b.clicked = False

def update():
    if clicked_button is None:
        for b in buttons:
            b.clicked = False
    else:
        for i, b in enumerate(buttons):
            b.clicked = (i == clicked_button)

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def handle_mouse_down(x, y):
    # y 좌표 변환(픽셀 좌표 -> 게임 좌표)
    gy = SCREEN_HEIGHT - y
    for i, b in enumerate(buttons):
        if b.is_clicked(x, gy):
            select_button(i)
            # 즉시 동작 (마우스 클릭 시 엔터와 동일한 동작 수행)
            activate_selected()
            return

def activate_selected():
    if clicked_button is None:
        return
    if clicked_button == 0:
        game_framework.change_mode(select_character)
    elif clicked_button == 1:
        print("Settings button clicked")

def handle_events():
    global clicked_button
    events = get_events()
    for e in events:
        if e.type == SDL_QUIT:
            game_framework.quit()
        elif e.type == SDL_MOUSEBUTTONDOWN:
            handle_mouse_down(e.x, e.y)
        elif e.type == SDL_KEYDOWN:
            if e.key == SDLK_DOWN or e.key == SDLK_RIGHT:
                if clicked_button is None:
                    select_button(0)
                else:
                    select_button((clicked_button + 1) % len(buttons))
            elif e.key == SDLK_UP or e.key == SDLK_LEFT:
                if clicked_button is None:
                    select_button(len(buttons) - 1)
                else:
                    select_button((clicked_button - 1) % len(buttons))
            elif e.key == SDLK_RETURN:
                activate_selected()
            elif e.key == SDLK_ESCAPE:
                game_framework.quit()
