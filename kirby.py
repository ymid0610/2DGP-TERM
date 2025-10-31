from pico2d import *
from sdl2 import *

from state_machine import StateMachine

import game_world
import game_framework

# 크기 배율 변수
SCALE = 4 # 배율

# 픽셀-미터 변환 변수
PIXEL_PER_METER = (10.0 / 0.5)  # 10 Pixel 50 cm

# 커비 걷기 속도
WALK_SPEED_KPH = 10  # Km / Hour
WALK_SPEED_MPM = (WALK_SPEED_KPH * 1000.0 / 60.0) # M / Minute
WALK_SPEED_MPS = (WALK_SPEED_MPM / 60.0) # M / Second
WALK_SPEED_PPS = (WALK_SPEED_MPS * PIXEL_PER_METER) # Pixel / Second

# 커비 점프 속도
JUMP_SPEED_KPH = 50  # Km / Hour
JUMP_SPEED_MPM = (JUMP_SPEED_KPH * 1000.0 / 60.0) # M / Minute
JUMP_SPEED_MPS = (JUMP_SPEED_MPM / 60.0) # M / Second
JUMP_SPEED_PPS = (JUMP_SPEED_MPS * PIXEL_PER_METER) # Pixel / Second

# 중력
GRAVITY = 9.8 # m/s^2
GRAVITY_PPS = GRAVITY * PIXEL_PER_METER

# 커비 액션 속도
TIME_PER_ACTION = 1 # 액션 초
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION # 초당 액션
FRAMES_PER_ACTION = 12 # 액션당 프레임 수

time_out = lambda e: e[0] == 'TIMEOUT'
after_delay_time_out = lambda e: e[0] == 'AFTER_DELAY_TIMEOUT'

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT
def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT
def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT
def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT
def up_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_UP
def up_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_UP
def down_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_DOWN
def down_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_DOWN
def a_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a
def a_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_a

class Kirby: #부모 클래스 커비
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0

        self.IDLE = Idle(self)
        self.DOWN = Down(self)
        self.WALK = Walk(self)
        self.DASH = Dash(self)
        self.IDLE_DASH_ATTACK = IdleDashAttack(self)
        self.DASH_ATTACK = DashAttack(self)
        self.IDLE_JUMP = IdleJump(self)
        self.IDLE_RISE = IdleRise(self)
        self.JUMP = Jump(self)
        self.SPIN_ATTACK = SpinAttack(self)
        self.IDLE_SUPER_JUMP = IdleSuperJump(self)
        self.SUPER_JUMP = SuperJump(self)
        self.END_SUPER_JUMP = EndSuperJump(self)
        self.IDLE_FALL = IdleFall(self)
        self.FALL = Fall(self)
        self.IDLE_LAND = IdleLand(self)
        self.IDLE_ATTACK = IdleAttack(self)
        self.IDLE_SLASH_ATTACK = IdleSlashAttack(self)
        self.SLASH_ATTACK = SlashAttack(self)
        self.RAPID_ATTACK = RapidAttack(self)
        self.IDLE_JUMP_ATTACK = IdleJumpAttack(self)
        self.RISE_JUMP_ATTACK = RiseJumpAttack(self)
        self.JUMP_ATTACK = JumpAttack(self)
        self.FALL_JUMP_ATTACK = FallJumpAttack(self)
        self.END_JUMP_ATTACK = EndJumpAttack(self)
        self.HIT = Hit(self)
        self.IDLE_GUARD = IdleGuard(self)
        self.GUARD = Guard(self)
        self.WIN = Win(self)
        self.STAR = Star(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE : {right_down: self.WALK, left_down: self.WALK, left_up: self.WALK, right_up: self.WALK,
                             down_down: self.DOWN, up_down: self.IDLE_JUMP},
                self.DOWN: {right_down: self.WALK, left_down: self.WALK,
                            right_up: self.WALK, left_up: self.WALK, down_up: self.IDLE},
                self.WALK: {right_up: self.IDLE, left_up: self.IDLE, right_down: self.IDLE, left_down: self.IDLE,
                            time_out: self.DASH, up_down: self.IDLE_JUMP},
                self.DASH: {right_down: self.IDLE, left_down: self.IDLE, left_up: self.IDLE, right_up: self.IDLE,
                            a_down: self.IDLE_DASH_ATTACK, up_down: self.IDLE_JUMP},
                self.IDLE_DASH_ATTACK: {time_out: self.DASH_ATTACK, after_delay_time_out: self.WALK,
                                        left_down: self.IDLE, left_up: self.IDLE,
                                        right_down: self.IDLE, right_up: self.IDLE},
                self.DASH_ATTACK: {after_delay_time_out: self.IDLE_DASH_ATTACK,
                                   left_down: self.IDLE, left_up: self.IDLE,
                                   right_down: self.IDLE, right_up: self.IDLE},
                self.IDLE_JUMP: {time_out: self.IDLE_RISE},
                self.IDLE_RISE: {left_down: self.IDLE_RISE, right_down: self.IDLE_RISE, left_up: self.IDLE_RISE, right_up: self.IDLE_RISE,
                                 time_out: self.JUMP},
                self.JUMP: {time_out: self.IDLE_FALL},
                self.IDLE_FALL: {time_out: self.IDLE},
            }
        )

    def update(self):
        self.state_machine.update()
    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())
    def get_bb(self):
        return self.x - (11 * SCALE), self.y - (19 * SCALE), self.x + (11 * SCALE), self.y + (3 * SCALE)

class Idle: #커비 대기 상태
    image = None
    pattern = [0,1,2,0,1,2,0,1,2,0,1,2,3,3,3,3]
    def __init__(self, kirby):
        self.kirby = kirby
        if Idle.image == None:
            Idle.image = load_image('Resource/Character/KirbyIdle.png')
    def enter(self, e):
        self.kirby.dir = 0
    def exit(self, e):
        pass
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(Idle.pattern)
    def draw(self):
        if self.kirby.face_dir == 1: # right
            Idle.image.clip_draw(Idle.pattern[int(self.kirby.frame)] * 48, 0, 48, 48, self.kirby.x, self.kirby.y, 48 * SCALE, 48 * SCALE)
        else:
            Idle.image.clip_composite_draw((Idle.pattern[int(self.kirby.frame)] % 12) * 48, 0, 48, 48, 0, 'h', self.kirby.x,self.kirby.y, 48 * SCALE, 48 * SCALE)

class Down: #커비 앉기 상태
    image = None
    pattern = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1]
    def __init__(self, kirby):
        self.kirby = kirby
        if Down.image == None:
            Down.image = load_image('Resource/Character/KirbyDown.png')
    def enter(self, e):
        self.kirby.dir = 0
        pass
    def exit(self, e):
        pass
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(Down.pattern)
    def draw(self):
        if self.kirby.face_dir == 1:
            Down.image.clip_draw(Down.pattern[int(self.kirby.frame)] * 48, 0, 48, 48, self.kirby.x, self.kirby.y, 48 * SCALE, 48 * SCALE)
        else:
            Down.image.clip_composite_draw((Down.pattern[int(self.kirby.frame)] % 12) * 48, 0, 48, 48, 0, 'h', self.kirby.x,self.kirby.y, 48 * SCALE, 48 * SCALE)
        draw_rectangle(*self.get_bb())
    def get_bb(self):
        return self.kirby.x - (12 * SCALE), self.kirby.y - (19 * SCALE), self.kirby.x + (12 * SCALE), self.kirby.y - (4 * SCALE)

class Walk: #커비 걷기 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        if Walk.image == None:
            Walk.image = load_image('Resource/Character/KirbyWalk.png')
    def enter(self, e):
        self.kirby.wait_time = get_time()
        if right_down(e) or left_up(e):
            self.kirby.dir = self.kirby.face_dir = 1
        elif left_down(e) or right_up(e):
            self.kirby.dir = self.kirby.face_dir = -1
    def exit(self, e):
        pass
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 12
        self.kirby.x += self.kirby.dir * WALK_SPEED_PPS * game_framework.frame_time
        if get_time() - self.kirby.wait_time > 24 * FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time:
            self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        if self.kirby.face_dir == 1: # right
            Walk.image.clip_draw(int(self.kirby.frame) * 48, 0, 48, 48, self.kirby.x, self.kirby.y, 48 * SCALE, 48 * SCALE)
        else: # face_dir == -1: # left
            Walk.image.clip_composite_draw((int(self.kirby.frame) % 12) * 48, 0, 48, 48, 0, 'h', self.kirby.x, self.kirby.y, 48 * SCALE, 48 * SCALE)

class Dash: #커비 대쉬 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        if Dash.image == None:
            Dash.image = load_image('Resource/Character/KirbyDash.png')
    def enter(self, e):
        self.kirby.dir = 3 * self.kirby.face_dir
    def exit(self, e):
        pass
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8
        self.kirby.x += self.kirby.dir * WALK_SPEED_PPS * game_framework.frame_time
    def draw(self):
        if self.kirby.face_dir == 1:  # right
            Dash.image.clip_draw(int(self.kirby.frame) * 48, 0, 48, 48, self.kirby.x, self.kirby.y, 48 * SCALE,48 * SCALE)
        else:  # face_dir == -1: # left
            Dash.image.clip_composite_draw((int(self.kirby.frame) % 12) * 48, 0, 48, 48, 0, 'h', self.kirby.x, self.kirby.y, 48 * SCALE, 48 * SCALE)

class IdleDashAttack: #커비 대쉬 공격 대기 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        if IdleDashAttack.image == None:
            IdleDashAttack.image = load_image('Resource/Character/KirbyIdleDashAttack.png')
    def enter(self, e):
        self.kirby.wait_time = get_time()
        if a_down(e):
            self.kirby.flag = 'TIMEOUT'
        elif after_delay_time_out(e):
            self.kirby.flag = 'AFTER_DELAY_TIMEOUT'
    def exit(self, e):
        pass
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 1
        if get_time() - self.kirby.wait_time > 12 * FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time:
            if self.kirby.flag == 'TIMEOUT':
                self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
            elif self.kirby.flag == 'AFTER_DELAY_TIMEOUT':
                self.kirby.state_machine.handle_state_event(('AFTER_DELAY_TIMEOUT', None))
    def draw(self):
        if self.kirby.face_dir == 1:
            IdleDashAttack.image.clip_draw(0, 0, 48, 48, self.kirby.x, self.kirby.y, 48 * SCALE, 48 * SCALE)
        else:
            IdleDashAttack.image.clip_composite_draw(0, 0, 48, 48, 0, 'h', self.kirby.x,self.kirby.y, 48 * SCALE, 48 * SCALE)

class DashAttack: #커비 대쉬 공격 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        if DashAttack.image == None:
            DashAttack.image = load_image('Resource/Character/KirbyDashAttack.png')
    def enter(self, e):
        self.kirby.wait_time = get_time()
        self.kirby.flag = 'TIMEOUT'
        self.kirby.dir = 5 * self.kirby.face_dir
    def exit(self, e):
        self.kirby.dir = self.kirby.face_dir
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 2
        self.kirby.x += self.kirby.dir * WALK_SPEED_PPS * game_framework.frame_time
        if get_time() - self.kirby.wait_time > 24 * FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time:
            if self.kirby.flag == 'TIMEOUT':
                self.kirby.state_machine.handle_state_event(('AFTER_DELAY_TIMEOUT', None))
    def draw(self):
        if self.kirby.face_dir == 1:
            DashAttack.image.clip_draw(int(self.kirby.frame) * 96, 0, 96, 48, self.kirby.x, self.kirby.y, 96 * SCALE, 48 * SCALE)
        else:
            DashAttack.image.clip_composite_draw((int(self.kirby.frame) % 2) * 96, 0, 96, 48, 0, 'h', self.kirby.x,self.kirby.y, 96 * SCALE, 48 * SCALE)

class IdleJump: #커비 점프 대기 상태
    image = None
    pattern = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1]
    def __init__(self, kirby):
        self.kirby = kirby
        if IdleJump.image == None:
            IdleJump.image = load_image('Resource/Character/KirbyIdleJump.png')
    def enter(self, e):
        self.kirby.wait_time = get_time()
    def exit(self, e):
        pass
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(Down.pattern)
        if get_time() - self.kirby.wait_time > 24 * FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time:
            self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        if self.kirby.face_dir == 1:
            IdleJump.image.clip_draw(IdleJump.pattern[int(self.kirby.frame)] * 48, 0, 48, 48, self.kirby.x, self.kirby.y, 48 * SCALE, 48 * SCALE)
        else:
            IdleJump.image.clip_composite_draw(IdleJump.pattern[int(self.kirby.frame)] * 48, 0, 48, 48, 0, 'h', self.kirby.x,self.kirby.y, 48 * SCALE, 48 * SCALE)

class IdleRise: #커비 점프 상승 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        if IdleRise.image == None:
            IdleRise.image = load_image('Resource/Character/KirbyIdleRise.png')
        self.vy = 0.0
    def enter(self, e):
        if right_up(e) or left_up(e):
            if self.kirby.flag == 'LEFT' and right_up(e):
                self.kirby.dir = self.kirby.face_dir = -1
            elif self.kirby.flag == 'RIGHT' and left_up(e):
                self.kirby.dir = self.kirby.face_dir = 1
            else:
                self.kirby.flag = 'IDLE'
                self.kirby.dir = self.kirby.face_dir
        elif right_down(e):
            self.kirby.flag = 'RIGHT'
            self.kirby.dir = self.kirby.face_dir = 1
        elif left_down(e):
            self.kirby.flag = 'LEFT'
            self.kirby.dir = self.kirby.face_dir = -1
        else:
            self.vy = JUMP_SPEED_PPS
            if self.kirby.dir >= 1:
                self.kirby.flag = 'RIGHT'
            elif self.kirby.dir <= -1:
                self.kirby.flag = 'LEFT'
            else:
                self.kirby.flag = 'IDLE'
    def exit(self, e):
        pass
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 2
        self.kirby.y += self.vy * game_framework.frame_time
        self.vy -= GRAVITY_PPS * game_framework.frame_time
        if self.kirby.flag == 'RIGHT' or self.kirby.flag == 'LEFT':
            self.kirby.x += self.kirby.dir * WALK_SPEED_PPS * game_framework.frame_time
        if self.vy <= 0:
            self.kirby.state_machine.handle_state_event(('TIMEOUT', None))

    def draw(self):
        if self.kirby.face_dir == 1:
            IdleRise.image.clip_draw(int(self.kirby.frame) * 48, 0, 48, 48, self.kirby.x, self.kirby.y, 48 * SCALE, 48 * SCALE)
        else:
            IdleRise.image.clip_composite_draw(int(self.kirby.frame) * 48, 0, 48, 48, 0, 'h', self.kirby.x,self.kirby.y, 48 * SCALE, 48 * SCALE)

class Jump: #커비 점프 상태 (공중제비 애니메이션)
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        if Jump.image == None:
            Jump.image = load_image('Resource/Character/KirbyJump.png')
    def enter(self, e):
        self.kirby.wait_time = get_time()
    def exit(self, e):
        pass
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 7
        if get_time() - self.kirby.wait_time > 12 * FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time:
            self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        if self.kirby.face_dir == 1:
            Jump.image.clip_draw(int(self.kirby.frame) * 48, 0, 48, 96, self.kirby.x, self.kirby.y, 48 * SCALE, 96 * SCALE)
        else:
            Jump.image.clip_composite_draw((int(self.kirby.frame) % 7) * 48, 0, 48, 96, 0, 'h', self.kirby.x,self.kirby.y, 48 * SCALE, 96 * SCALE)

class SpinAttack: #커비 공중베기 공격 상태
    def __init__(self, kirby):
        self.kirby = kirby
    def enter(self, e):
        pass
    def exit(self, e):
        pass
    def do(self):
        pass
    def draw(self):
        pass

class IdleSuperJump:  # 커비 슈퍼 점프 대기 상태
    def __init__(self, kirby):
        self.kirby = kirby
    def enter(self, e):
        pass
    def exit(self, e):
        pass
    def do(self):
        pass
    def draw(self):
        pass

class SuperJump:  # 커비 슈퍼 점프 상태
    def __init__(self, kirby):
        self.kirby = kirby
    def enter(self, e):
        pass
    def exit(self, e):
        pass
    def do(self):
        pass
    def draw(self):
        pass

class EndSuperJump:  # 커비 슈퍼 점프 종료 상태
    def __init__(self, kirby):
        self.kirby = kirby
    def enter(self, e):
        pass
    def exit(self, e):
        pass
    def do(self):
        pass
    def draw(self):
        pass

class IdleFall: #커비 점프 낙하 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        if IdleFall.image == None:
            IdleFall.image = load_image('Resource/Character/KirbyIdleFall.png')
        self.vy = 0.0
    def enter(self, e):
        if right_up(e) or left_up(e):
            if self.kirby.flag == 'LEFT' and right_up(e):
                self.kirby.dir = self.kirby.face_dir = -1
            elif self.kirby.flag == 'RIGHT' and left_up(e):
                self.kirby.dir = self.kirby.face_dir = 1
            else:
                self.kirby.flag = 'IDLE'
                self.kirby.dir = self.kirby.face_dir
        elif right_down(e):
            self.kirby.flag = 'RIGHT'
            self.kirby.dir = self.kirby.face_dir = 1
        elif left_down(e):
            self.kirby.flag = 'LEFT'
            self.kirby.dir = self.kirby.face_dir = -1
        else:
            self.vy = 0.0
            if self.kirby.dir >= 1:
                self.kirby.flag = 'RIGHT'
            elif self.kirby.dir <= -1:
                self.kirby.flag = 'LEFT'
            else:
                self.kirby.flag = 'IDLE'
    def exit(self, e):
        pass
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 2
        self.kirby.y -= self.vy * game_framework.frame_time
        self.vy += GRAVITY_PPS * game_framework.frame_time
        if self.kirby.flag == 'RIGHT' or self.kirby.flag == 'LEFT':
            self.kirby.x += self.kirby.dir * WALK_SPEED_PPS * game_framework.frame_time
        if self.vy >= JUMP_SPEED_PPS:
            self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        if self.kirby.face_dir == 1:
            IdleFall.image.clip_draw(int(self.kirby.frame) * 48, 0, 48, 48, self.kirby.x, self.kirby.y, 48 * SCALE, 48 * SCALE)
        else:
            IdleFall.image.clip_composite_draw(int(self.kirby.frame) * 48, 0, 48, 48, 0, 'h', self.kirby.x,self.kirby.y, 48 * SCALE, 48 * SCALE)

class Fall: #커비 점프 착지 상태 (강한 착지)
    def __init__(self, kirby):
        self.kirby = kirby
    def enter(self, e):
        pass
    def exit(self, e):
        pass
    def do(self):
        pass
    def draw(self):
        pass

class IdleLand: #커비 점프 착지 상태 (가벼운 착지)
    def __init__(self, kirby):
        self.kirby = kirby
    def enter(self, e):
        pass
    def exit(self, e):
        pass
    def do(self):
        pass
    def draw(self):
        pass

class IdleAttack: #커비 공격 대기 상태
    def __init__(self, kirby):
        self.kirby = kirby
    def enter(self, e):
        pass
    def exit(self, e):
        pass
    def do(self):
        pass
    def draw(self):
        pass

class IdleSlashAttack: #커비 베기 공격 대기 상태
    def __init__(self, kirby):
        self.kirby = kirby
    def enter(self, e):
        pass
    def exit(self, e):
        pass
    def do(self):
        pass
    def draw(self):
        pass

class SlashAttack: #커비 베기 공격 상태
    def __init__(self, kirby):
        self.kirby = kirby
    def enter(self, e):
        pass
    def exit(self, e):
        pass
    def do(self):
        pass
    def draw(self):
        pass

class RapidAttack: #커비 연속 공격 상태
    def __init__(self, kirby):
        self.kirby = kirby
    def enter(self, e):
        pass
    def exit(self, e):
        pass
    def do(self):
        pass
    def draw(self):
        pass

class IdleJumpAttack: #커비 점프 베기 공격 대기 상태
    def __init__(self, kirby):
        self.kirby = kirby
    def enter(self, e):
        pass
    def exit(self, e):
        pass
    def do(self):
        pass
    def draw(self):
        pass

class RiseJumpAttack: #커비 점프 상승 베기 공격 상태
    def __init__(self, kirby):
        self.kirby = kirby
    def enter(self, e):
        pass
    def exit(self, e):
        pass
    def do(self):
        pass
    def draw(self):
        pass

class JumpAttack: #커비 점프 공격 상태
    def __init__(self, kirby):
        self.kirby = kirby
    def enter(self, e):
        pass
    def exit(self, e):
        pass
    def do(self):
        pass
    def draw(self):
        pass

class FallJumpAttack: #커비 점프 낙하 베기 공격 상태
    def __init__(self, kirby):
        self.kirby = kirby
    def enter(self, e):
        pass
    def exit(self, e):
        pass
    def do(self):
        pass
    def draw(self):
        pass

class EndJumpAttack: #커비 점프 베기 공격 착지 상태
    def __init__(self, kirby):
        self.kirby = kirby
    def enter(self, e):
        pass
    def exit(self, e):
        pass
    def do(self):
        pass
    def draw(self):
        pass

class Hit: #커비 피격 상태
    def __init__(self, kirby):
        self.kirby = kirby
    def enter(self, e):
        pass
    def exit(self, e):
        pass
    def do(self):
        pass
    def draw(self):
        pass

class IdleGuard: #커비 가드 대기 상태
    def __init__(self, kirby):
        self.kirby = kirby
    def enter(self, e):
        pass
    def exit(self, e):
        pass
    def do(self):
        pass
    def draw(self):
        pass

class Guard: #커비 가드 상태
    def __init__(self, kirby):
        self.kirby = kirby
    def enter(self, e):
        pass
    def exit(self, e):
        pass
    def do(self):
        pass
    def draw(self):
        pass

class Win: #커비 승리 상태
    def __init__(self, kirby):
        self.kirby = kirby
    def enter(self, e):
        pass
    def exit(self, e):
        pass
    def do(self):
        pass
    def draw(self):
        pass

class Star: #커비 별 상태 (종료)
    def __init__(self, kirby):
        self.kirby = kirby
    def enter(self, e):
        pass
    def exit(self, e):
        pass
    def do(self):
        pass
    def draw(self):
        pass