import game_framework
from pico2d import *
import play_mode
from button import AddPlayer, RemovePlayer, Player1, Player2, Computer, Start
import game_world
from background import Space

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

buttons = []
clicked_button = None
player1, player2, computer = None, None, None
start = None

def init():
    background = Space()
    game_world.add_object(background, 0)

    global buttons, clicked_button, player1, player2
    player1 = Player1(140, 0)
    player2 = Player2(631, 0)
    buttons = [AddPlayer(631+486, 62 * 1.6),RemovePlayer(631+486, 0), player1, player2]
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
    global buttons, clicked_button
    if clicked_button is None:
        for b in buttons:
            b.clicked = False
    else:
        for i, b in enumerate(buttons):
            b.clicked = (i == clicked_button)
    global start
    if len(buttons) == 4:
        if start is None:
            start = Start(148, 400)
            game_world.add_object(start, 1)
            buttons.append(start)
        else:
            game_world.remove_object(start)
            buttons.remove(start)
            start = None
    buttons.sort(key=lambda btn: isinstance(btn, Start))

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
    global buttons, player1, player2, computer, clicked_button
    if clicked_button is None:
        return
    if clicked_button == 0:
        # Add Player 버튼 처리: 순서대로 Player1, Player2 추가
        if len(buttons) == 2 and player1 is None:
            player1 = Player1(140, 0)
            buttons.append(player1)
            game_world.add_object(player1, 1)
        elif len(buttons) >= 3:
            if player2 is None:
                player2 = Player2(631, 0)
                buttons.append(player2)
                game_world.add_object(player2, 1)
            elif computer is None:
                computer = Computer(631, 0)
                buttons.append(computer)
                game_world.add_object(computer, 1)
        else:
            return
    elif clicked_button == 1:
        # Remove Player 버튼 처리: 역순으로 Player2, Player1 제거
        if len(buttons) >= 4:
            if player2 is not None:
                game_world.remove_object(player2)
                buttons.remove(player2)
                player2 = None
            elif computer is not None:
                game_world.remove_object(computer)
                buttons.remove(computer)
                computer = None
        elif len(buttons) == 3 and player1 is not None:
            game_world.remove_object(player1)
            buttons.remove(player1)
            player1 = None
        else:
            return
    elif clicked_button == 3:
        # Player2 선택 시 컴퓨터 모드로 전환
        if len(buttons) >= 4 and player2 is not None:
            game_world.remove_object(player2)
            buttons.remove(player2)
            player2 = None
            computer = Computer(631, 0)
            buttons.append(computer)
            game_world.add_object(computer, 1)
        elif len(buttons) >= 4 and computer is not None:
            # 컴퓨터 모드 지우고 플레이어2 추가
            game_world.remove_object(computer)
            buttons.remove(computer)
            computer = None
            player2 = Player2(631, 0)
            buttons.append(player2)
            game_world.add_object(player2, 1)
        else:
            return
    elif clicked_button == 4:
        game_framework.change_mode(play_mode)

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
