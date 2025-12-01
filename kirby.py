from pico2d import *
from sdl2 import *

from state_machine import StateMachine
import game_world
import game_framework

from grass import *

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
JUMP_SPEED_KPH = 5  # Km / Hour
JUMP_SPEED_MPM = (JUMP_SPEED_KPH * 1000.0 / 60.0) # M / Minute
JUMP_SPEED_MPS = (JUMP_SPEED_MPM / 60.0) # M / Second
JUMP_SPEED_PPS = (JUMP_SPEED_MPS * PIXEL_PER_METER) # Pixel / Second
SUPER_JUMP_SPEED_PPS = JUMP_SPEED_PPS * 1.2 # 슈퍼 점프 속도

# 중력
GRAVITY = 1.6 # m/s^2
GRAVITY_PPS = GRAVITY * PIXEL_PER_METER

# 커비 액션 속도
TIME_PER_ACTION = 0.75 # 액션 초
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION # 초당 액션
FRAMES_PER_ACTION = 12 # 액션당 프레임 수

# 더블탭 허용 시간 (초)
DOUBLE_TAP_TIME = 0.25

time_out = lambda e: e[0] == 'TIMEOUT'
after_delay_time_out = lambda e: e[0] == 'AFTER_DELAY_TIMEOUT'
fall_out = lambda e: e[0] == 'FALLOUT'
hit = lambda e: e[0] == 'HIT'

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and (e[1].key == SDLK_RIGHT or e[1].key == SDLK_d)
def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and (e[1].key == SDLK_RIGHT or e[1].key == SDLK_d)
def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and (e[1].key == SDLK_LEFT or e[1].key == SDLK_a)
def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and (e[1].key == SDLK_LEFT or e[1].key == SDLK_a)
def up_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and (e[1].key == SDLK_UP or e[1].key == SDLK_w)
def up_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and (e[1].key == SDLK_UP or e[1].key == SDLK_w)
def down_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and (e[1].key == SDLK_DOWN or e[1].key == SDLK_s)
def down_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and (e[1].key == SDLK_DOWN or e[1].key == SDLK_s)
def attack_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and (e[1].key == SDLK_LCTRL or e[1].key == SDLK_RCTRL)
def attack_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and (e[1].key == SDLK_LCTRL or e[1].key == SDLK_RCTRL)

# 더블탭 이벤트 판정용 함수
def right_double_tap(e):
    return e[0] == 'DOUBLE_TAP' and e[1] == 'RIGHT'
def left_double_tap(e):
    return e[0] == 'DOUBLE_TAP' and e[1] == 'LEFT'

class Kirby: #부모 클래스 커비
    def __init__(self):
        # 초기값
        self.x, self.y = 240.0, 600.0
        self.frame = 0
        self.face_dir = 1
        self.dir = 0
        self.flag = None
        self.vy= 0.0
        self.yv = 0.0
        self._last_tap = {'RIGHT': 0.0, 'LEFT': 0.0}
        self.stopped = False
        self.hp = 100

        # 디버깅용 폰트
        self.font = load_font('Resource/Font/ENCR10B.TTF', 16)

        # 상태 객체들
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
        self.GUARD = Guard(self)
        self.WIN = Win(self)
        self.STAR = Star(self)

        # 상태 다이어그램
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE : {right_double_tap: self.DASH, left_double_tap: self.DASH,
                             right_down: self.WALK, left_down: self.WALK, left_up: self.WALK, right_up: self.WALK,
                             down_down: self.DOWN, up_down: self.IDLE_JUMP, attack_down: self.IDLE_SLASH_ATTACK,
                             time_out: self.WALK, fall_out: self.STAR, hit: self.HIT},
                self.DOWN: {right_down: self.WALK, left_down: self.WALK,
                            right_up: self.WALK, left_up: self.WALK, down_up: self.IDLE,
                            attack_down: self.GUARD, hit: self.HIT},
                self.WALK: {right_double_tap: self.IDLE, left_double_tap: self.IDLE, hit: self.HIT,
                            right_up: self.IDLE, left_up: self.IDLE, right_down: self.IDLE, left_down: self.IDLE,
                            up_down: self.IDLE_JUMP, attack_down: self.IDLE_SLASH_ATTACK, fall_out: self.STAR},
                self.DASH: {right_double_tap: self.IDLE, left_double_tap: self.IDLE, hit: self.HIT,
                            right_down: self.IDLE, left_down: self.IDLE, left_up: self.IDLE, right_up: self.IDLE,
                            attack_down: self.IDLE_DASH_ATTACK, up_down: self.IDLE_JUMP,
                            down_down: self.FALL, fall_out: self.STAR},
                self.IDLE_DASH_ATTACK: {time_out: self.DASH_ATTACK, after_delay_time_out: self.WALK, hit: self.HIT,
                                        left_down: self.IDLE, left_up: self.IDLE,
                                        right_down: self.IDLE, right_up: self.IDLE},
                self.DASH_ATTACK: {after_delay_time_out: self.IDLE_DASH_ATTACK,
                                   left_down: self.IDLE, left_up: self.IDLE,
                                   right_down: self.IDLE, right_up: self.IDLE,
                                   fall_out: self.STAR},
                self.IDLE_JUMP: {left_double_tap: self.IDLE_JUMP, right_double_tap: self.IDLE_JUMP, hit: self.HIT,
                                 left_down: self.IDLE_JUMP, right_down: self.IDLE_JUMP, left_up: self.IDLE_JUMP, right_up: self.IDLE_JUMP,
                                 time_out: self.IDLE_SUPER_JUMP, up_up: self.IDLE_RISE, attack_down: self.IDLE_JUMP_ATTACK},
                self.IDLE_RISE: {left_double_tap: self.IDLE_RISE, right_double_tap: self.IDLE_RISE, hit: self.HIT,
                                 left_down: self.IDLE_RISE, right_down: self.IDLE_RISE, left_up: self.IDLE_RISE, right_up: self.IDLE_RISE,
                                 time_out: self.JUMP, attack_down: self.SPIN_ATTACK, up_down: self.IDLE_SUPER_JUMP},
                self.JUMP: {left_double_tap: self.JUMP, right_double_tap: self.JUMP, hit: self.HIT,
                            left_down: self.JUMP, right_down: self.JUMP, left_up: self.JUMP, right_up: self.JUMP,
                            time_out: self.IDLE_FALL, attack_down: self.SPIN_ATTACK},
                self.SPIN_ATTACK: {left_double_tap: self.SPIN_ATTACK, right_double_tap: self.SPIN_ATTACK,
                                   left_down: self.SPIN_ATTACK, right_down: self.SPIN_ATTACK, left_up: self.SPIN_ATTACK, right_up: self.SPIN_ATTACK,
                                   time_out: self.IDLE_FALL},
                self.IDLE_SUPER_JUMP: {time_out: self.SUPER_JUMP, attack_down: self.SPIN_ATTACK, hit: self.HIT,
                                       left_double_tap: self.IDLE_SUPER_JUMP, right_double_tap: self.IDLE_SUPER_JUMP,
                                       left_down: self.IDLE_SUPER_JUMP, right_down: self.IDLE_SUPER_JUMP,
                                       left_up: self.IDLE_SUPER_JUMP, right_up: self.IDLE_SUPER_JUMP},
                self.SUPER_JUMP: {time_out: self.END_SUPER_JUMP, attack_down: self.END_SUPER_JUMP, up_down: self.SUPER_JUMP,
                                  left_double_tap: self.SUPER_JUMP, right_double_tap: self.SUPER_JUMP,
                                  left_down: self.SUPER_JUMP, right_down: self.SUPER_JUMP, hit: self.HIT,
                                  left_up: self.SUPER_JUMP, right_up: self.SUPER_JUMP, fall_out: self.STAR},
                self.END_SUPER_JUMP: {time_out: self.FALL, fall_out: self.STAR,
                                      left_double_tap: self.END_SUPER_JUMP, right_double_tap: self.END_SUPER_JUMP,
                                      left_down: self.END_SUPER_JUMP, right_down: self.END_SUPER_JUMP,
                                      left_up: self.END_SUPER_JUMP, right_up: self.END_SUPER_JUMP},
                self.IDLE_FALL: {left_double_tap: self.IDLE_FALL, right_double_tap: self.IDLE_FALL, hit: self.HIT,
                                 left_down: self.IDLE_FALL, right_down: self.IDLE_FALL, left_up: self.IDLE_FALL, right_up: self.IDLE_FALL,
                                 time_out: self.IDLE, attack_down: self.JUMP_ATTACK, up_down: self.IDLE_SUPER_JUMP, fall_out: self.STAR},
                self.FALL: {time_out: self.IDLE,
                            left_double_tap: self.FALL, right_double_tap: self.FALL,
                            left_down: self.FALL, right_down: self.FALL,
                            left_up: self.FALL, right_up: self.FALL},
                self.IDLE_SLASH_ATTACK: {time_out: self.SLASH_ATTACK, down_down: self.DOWN, hit: self.HIT,
                                         left_double_tap: self.IDLE, right_double_tap: self.IDLE,
                                        left_down: self.IDLE, left_up: self.IDLE,
                                        right_down: self.IDLE, right_up: self.IDLE},
                self.SLASH_ATTACK: {after_delay_time_out: self.IDLE_ATTACK, attack_down: self.RAPID_ATTACK,
                                    left_double_tap: self.SLASH_ATTACK, right_double_tap: self.SLASH_ATTACK,
                                    left_down: self.SLASH_ATTACK, right_down: self.SLASH_ATTACK, left_up: self.SLASH_ATTACK, right_up: self.SLASH_ATTACK},
                self.IDLE_ATTACK: {time_out: self.IDLE, after_delay_time_out: self.IDLE, attack_down: self.RAPID_ATTACK,
                                   left_double_tap: self.DASH, right_double_tap: self.DASH,
                                   left_down: self.IDLE, right_down: self.IDLE, hit: self.HIT,
                                   left_up: self.IDLE, right_up: self.IDLE},
                self.RAPID_ATTACK: {after_delay_time_out: self.IDLE_ATTACK, attack_up: self.IDLE_ATTACK,
                                    left_double_tap: self.RAPID_ATTACK, right_double_tap: self.RAPID_ATTACK,
                                    left_down: self.RAPID_ATTACK, right_down: self.RAPID_ATTACK,
                                    left_up: self.RAPID_ATTACK, right_up: self.RAPID_ATTACK},
                self.IDLE_JUMP_ATTACK: {time_out: self.RISE_JUMP_ATTACK, hit: self.HIT,
                                        left_double_tap: self.IDLE, right_double_tap: self.IDLE,
                                        left_down: self.IDLE, left_up: self.IDLE,
                                        right_down: self.IDLE, right_up: self.IDLE},
                self.RISE_JUMP_ATTACK: {left_double_tap: self.RISE_JUMP_ATTACK, right_double_tap: self.RISE_JUMP_ATTACK,
                                        left_down: self.RISE_JUMP_ATTACK, right_down: self.RISE_JUMP_ATTACK,
                                        left_up: self.RISE_JUMP_ATTACK, right_up: self.RISE_JUMP_ATTACK,
                                        time_out: self.JUMP_ATTACK},
                self.JUMP_ATTACK: {time_out: self.FALL_JUMP_ATTACK,
                                   left_double_tap: self.JUMP_ATTACK, right_double_tap: self.JUMP_ATTACK,
                                   left_down: self.JUMP_ATTACK, right_down: self.JUMP_ATTACK,
                                   left_up: self.JUMP_ATTACK, right_up: self.JUMP_ATTACK},
                self.FALL_JUMP_ATTACK: {time_out: self.END_JUMP_ATTACK, fall_out: self.STAR,
                                        left_double_tap: self.FALL_JUMP_ATTACK, right_double_tap: self.FALL_JUMP_ATTACK,
                                        left_down: self.FALL_JUMP_ATTACK, right_down: self.FALL_JUMP_ATTACK,
                                        left_up: self.FALL_JUMP_ATTACK, right_up: self.FALL_JUMP_ATTACK},
                self.END_JUMP_ATTACK: {time_out: self.IDLE,
                                       left_double_tap: self.DASH, right_double_tap: self.DASH,
                                       left_down: self.IDLE, right_down: self.IDLE,
                                       left_up: self.IDLE, right_up: self.IDLE},
                self.HIT: {time_out: self.FALL,
                           left_double_tap: self.HIT, right_double_tap: self.HIT,
                           left_down: self.HIT, right_down: self.HIT,
                           left_up: self.HIT, right_up: self.HIT},
                self.GUARD: {right_down: self.WALK, left_down: self.WALK,
                             right_up: self.WALK, left_up: self.WALK,
                             up_down: self.IDLE_JUMP, down_down: self.DOWN,
                             time_out: self.IDLE, attack_down: self.IDLE_SLASH_ATTACK},
                self.STAR: {time_out: self.IDLE,
                            left_double_tap: self.STAR, right_double_tap: self.STAR,
                            left_down: self.STAR, right_down: self.STAR,
                            left_up: self.STAR, right_up: self.STAR}
            }
        )
    def update(self):
        if not self.stopped:
            self.y += self.yv * game_framework.frame_time * PIXEL_PER_METER
            self.yv -= GRAVITY_PPS * game_framework.frame_time # 기본중력 적용
        else:
            if self.yv < 0:
                self.yv = 0.0
        self.state_machine.update()
    def handle_event(self, event):
        # 더블탭 감지: 빠르게 같은 방향으로 두 번 누르면 ('DOUBLE_TAP', 'RIGHT'|'LEFT') 이벤트 발생
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_RIGHT or event.key == SDLK_d:
                now = get_time()
                if now - self._last_tap['RIGHT'] <= DOUBLE_TAP_TIME:
                    self.face_dir = 1
                    self.dir = 1
                    self._last_tap['RIGHT'] = 0.0
                    self.state_machine.handle_state_event(('DOUBLE_TAP', 'RIGHT'))
                    return
                else:
                    self._last_tap['RIGHT'] = now
            elif event.key == SDLK_LEFT or event.key == SDLK_a:
                now = get_time()
                if now - self._last_tap['LEFT'] <= DOUBLE_TAP_TIME:
                    self.face_dir = -1
                    self.dir = -1
                    self._last_tap['LEFT'] = 0.0
                    self.state_machine.handle_state_event(('DOUBLE_TAP', 'LEFT'))
                    return
                else:
                    self._last_tap['LEFT'] = now
        # 기본 입력은 기존대로 전달
        self.state_machine.handle_state_event(('INPUT', event))
    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())
        draw_rectangle(*self.get_base_bb())
        self.font.draw(self.x, self.y - 96, f'(hp = {self.hp:3}, {self.x:5.5}, {self.y:5.5})', (255, 0, 0))
    def get_bb(self):
        state_machine = getattr(self, 'state_machine', None)
        if state_machine is not None:
            cur = getattr(state_machine, 'cur_state', None)
        if cur is not None and hasattr(cur, 'get_bb'):
            try:
                return cur.get_bb()
            except Exception:
                pass
        return self.get_base_bb()
    def get_base_bb(self):
        return (self.x - (11 * SCALE), self.y - (19 * SCALE), self.x + (11 * SCALE), self.y + (3 * SCALE))
    def handle_collision(self, group, other):
        if group == 'grass:kirby':
            if self.yv < 0:
                self.stopped = True
                self.yv = 0.0
                if self.state_machine.cur_state in (self.DASH_ATTACK, self.FALL_JUMP_ATTACK, self.END_JUMP_ATTACK):
                    pass
                else:
                    self.y += other.get_bb()[3] - self.get_bb()[1]
        elif group == 'kirby1:kirby2':
            try:
                my_bb = self.get_bb()
                other_bb = other.get_bb()
                if my_bb == self.get_base_bb() and other_bb == other.get_base_bb():
                    return
            except Exception:
                # 안전장치: bb 조회 실패 시 기존 로직 진행
                pass
            # 충돌시 공격상태가 아닐경우
            if self.state_machine.cur_state not in (self.SLASH_ATTACK, self.RAPID_ATTACK, self.SPIN_ATTACK,
                                                    self.DASH_ATTACK,
                                                    self.JUMP_ATTACK, self.RISE_JUMP_ATTACK, self.FALL_JUMP_ATTACK,
                                                    self.END_JUMP_ATTACK,
                                                    self.GUARD, self.FALL, self.HIT):
                self.state_machine.handle_state_event(('HIT', None))
    def take_damage(self, amount):
        self.hp -= amount

    # 키 입력에 따른 상태 플래그 판단 함수
    def judgement_key_flag(self, e):
        initial = False
        if right_up(e) or left_up(e):
            if self.flag == 'LEFT' and right_up(e):
                self.dir = self.face_dir = -1
            elif self.flag == 'RIGHT' and left_up(e):
                self.dir = self.face_dir = 1
            elif self.flag == 'IDLE':
                if right_up(e):
                    self.flag = 'LEFT'
                    self.dir = self.face_dir = -1
                elif left_up(e):
                    self.flag = 'RIGHT'
                    self.dir = self.face_dir = 1
            else:
                self.flag = 'IDLE'
                self.dir = 0
        elif right_down(e) or right_double_tap(e):
            if self.flag == 'LEFT':
                self.flag = 'IDLE'
                self.dir = 0
            else:
                self.flag = 'RIGHT'
                self.dir = self.face_dir = 1
        elif left_down(e) or left_double_tap(e):
            if self.flag == 'RIGHT':
                self.flag = 'IDLE'
                self.dir = 0
            else:
                self.flag = 'LEFT'
                self.dir = self.face_dir = -1
        else:
            if self.dir >= 1:
                self.flag = 'RIGHT'
            elif self.dir <= -1:
                self.flag = 'LEFT'
            else:
                self.flag = 'IDLE'
            initial = True
        return initial

class Idle: #커비 대기 상태
    image = None
    pattern = [0,1,2,0,1,2,0,1,2,0,1,2,3,3,3,3]
    def __init__(self, kirby):
        self.kirby = kirby
        if Idle.image == None:
            Idle.image = load_image('Resource/Character/KirbyIdle.png')
    def enter(self, e):
        if time_out(e) or after_delay_time_out(e):
            if self.kirby.flag == 'LEFT':
                self.kirby.face_dir = -1
            elif self.kirby.flag == 'RIGHT':
                self.kirby.face_dir = 1
            self.kirby.dir = 0
        else:
            self.kirby.dir = 0
        self.kirby.frame = 0
    def exit(self, e):
        if attack_down(e):
            self.kirby.flag = 'IDLE'
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(Idle.pattern)
        if self.kirby.y < 0 - (48 * SCALE):
            self.kirby.state_machine.handle_state_event(('FALLOUT', None))
        if self.kirby.flag == 'LEFT' or self.kirby.flag == 'RIGHT':
            self.kirby.flag = None
            self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
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
        self.kirby.frame = 0
        self.kirby.dir = 0
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
        self.kirby.frame = 0
        if right_down(e) or left_up(e):
            self.kirby.dir = self.kirby.face_dir = 1
        elif left_down(e) or right_up(e):
            self.kirby.dir = self.kirby.face_dir = -1
        else:
            self.kirby.dir = self.kirby.face_dir
    def exit(self, e):
        if attack_down(e):
            if self.kirby.face_dir == 1:
                self.kirby.flag = 'RIGHT'
            else:
                self.kirby.flag = 'LEFT'
        print(f'{self.kirby.dir}, {self.kirby.flag}')
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 12
        if self.kirby.y < 0 - (48 * SCALE):
            self.kirby.state_machine.handle_state_event(('FALLOUT', None))
        self.kirby.stopped = False
        self.kirby.x += self.kirby.dir * WALK_SPEED_PPS * game_framework.frame_time
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
        self.kirby.frame = 0
        self.kirby.dir = 3 * self.kirby.face_dir
    def exit(self, e):
        pass
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8
        if self.kirby.y < 0 - (48 * SCALE):
            self.kirby.state_machine.handle_state_event(('FALLOUT', None))
        self.kirby.x += self.kirby.dir * WALK_SPEED_PPS * game_framework.frame_time
        self.kirby.stopped = False
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
        if attack_down(e):
            self.kirby.flag = 'TIMEOUT'
        elif after_delay_time_out(e):
            self.kirby.flag = 'AFTER_DELAY_TIMEOUT'
    def exit(self, e):
        pass
    def do(self):
        if get_time() - self.kirby.wait_time > 0.25 / ACTION_PER_TIME:
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
        self.kirby.frame = 0
        self.kirby.wait_time = get_time()
        self.kirby.flag = 'TIMEOUT'
        self.kirby.dir = 5 * self.kirby.face_dir
    def exit(self, e):
        self.kirby.dir = self.kirby.face_dir
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 2
        if self.kirby.y < 0 - (48 * SCALE):
            self.kirby.state_machine.handle_state_event(('FALLOUT', None))
        self.kirby.x += self.kirby.dir * WALK_SPEED_PPS * game_framework.frame_time
        self.kirby.stopped = False
        if get_time() - self.kirby.wait_time > 0.75 / ACTION_PER_TIME:
            if self.kirby.flag == 'TIMEOUT':
                self.kirby.state_machine.handle_state_event(('AFTER_DELAY_TIMEOUT', None))
    def draw(self):
        if self.kirby.face_dir == 1:
            DashAttack.image.clip_draw(int(self.kirby.frame) * 96, 0, 96, 48, self.kirby.x, self.kirby.y, 96 * SCALE, 48 * SCALE)
        else:
            DashAttack.image.clip_composite_draw((int(self.kirby.frame) % 2) * 96, 0, 96, 48, 0, 'h', self.kirby.x,self.kirby.y, 96 * SCALE, 48 * SCALE)
        draw_rectangle(*self.get_bb())
    def get_bb(self):
        return (self.kirby.x - (96 * SCALE / 2) + (10 * SCALE), self.kirby.y - (48 * SCALE / 2) - (0 * SCALE),
                self.kirby.x + (96 * SCALE / 2) - (10 * SCALE), self.kirby.y + (48 * SCALE / 2) - (14 * SCALE))

class IdleJump: #커비 점프 대기 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        self.animation = True
        if IdleJump.image == None:
            IdleJump.image = load_image('Resource/Character/KirbyIdleJump.png')
    def enter(self, e):
        initial = self.kirby.judgement_key_flag(e)
        if initial:
            self.kirby.frame = 0
            self.kirby.frame_time = get_time()
            self.animation = True
    def exit(self, e):
        pass
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 2
        if not self.animation:
            if get_time() - self.kirby.wait_time > self.kirby.frame_time:
                self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
        else:
            if self.kirby.frame >= 1:
                self.kirby.frame_time = get_time() - self.kirby.frame_time
                self.kirby.wait_time = get_time()
                self.animation = False
    def draw(self):
        if self.kirby.face_dir == 1:
            IdleJump.image.clip_draw(int(self.kirby.frame) * 48, 0, 48, 48, self.kirby.x, self.kirby.y, 48 * SCALE, 48 * SCALE)
        else:
            IdleJump.image.clip_composite_draw(int(self.kirby.frame) * 48, 0, 48, 48, 0, 'h', self.kirby.x,self.kirby.y, 48 * SCALE, 48 * SCALE)

class IdleRise: #커비 점프 상승 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        if IdleRise.image == None:
            IdleRise.image = load_image('Resource/Character/KirbyIdleRise.png')
    def enter(self, e):
        initial = self.kirby.judgement_key_flag(e)
        if initial:
            self.kirby.frame = 0
            self.kirby.yv = JUMP_SPEED_PPS
    def exit(self, e):
        print(f'{self.kirby.stopped}, IdleRise')
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 2
        self.kirby.stopped = False
        if self.kirby.yv - GRAVITY_PPS * game_framework.frame_time <= 0: # 다음 프레임에서 속도가 0 이하가 되면(최고점 도달)
            self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
        if self.kirby.flag == 'RIGHT' or self.kirby.flag == 'LEFT':
            self.kirby.x += self.kirby.dir * WALK_SPEED_PPS * game_framework.frame_time
    def draw(self):
        if self.kirby.face_dir == 1:
            IdleRise.image.clip_draw(int(self.kirby.frame) * 48, 0, 48, 48, self.kirby.x, self.kirby.y, 48 * SCALE, 48 * SCALE)
        else:
            IdleRise.image.clip_composite_draw(int(self.kirby.frame) * 48, 0, 48, 48, 0, 'h', self.kirby.x,self.kirby.y, 48 * SCALE, 48 * SCALE)

class Jump: #커비 점프 상태 (공중제비 애니메이션)
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        self.animation = True
        if Jump.image == None:
            Jump.image = load_image('Resource/Character/KirbyJump.png')
    def enter(self, e):
        initial = self.kirby.judgement_key_flag(e)
        if initial:
            self.kirby.frame = 0
            self.kirby.frame_time = get_time()
            self.animation = True
    def exit(self, e):
        pass
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 7
        self.kirby.stopped = False
        self.kirby.yv = 0 # 체공을 위해 중력 무시
        if self.kirby.flag == 'RIGHT' or self.kirby.flag == 'LEFT':
            self.kirby.x += self.kirby.dir * WALK_SPEED_PPS * game_framework.frame_time
        if not self.animation:
            if get_time() - self.kirby.wait_time > self.kirby.frame_time:
                self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
        else:
            if 4 <= self.kirby.frame < 5:
                self.kirby.frame_time = get_time()
            elif self.kirby.frame >= 6:
                self.kirby.frame_time = get_time() - self.kirby.frame_time
                self.kirby.wait_time = get_time()
                self.animation = False
    def draw(self):
        if self.kirby.face_dir == 1:
            Jump.image.clip_draw(int(self.kirby.frame) * 48, 0, 48, 96, self.kirby.x, self.kirby.y, 48 * SCALE, 96 * SCALE)
        else:
            Jump.image.clip_composite_draw((int(self.kirby.frame) % 7) * 48, 0, 48, 96, 0, 'h', self.kirby.x,self.kirby.y, 48 * SCALE, 96 * SCALE)

class SpinAttack: #커비 공중베기 공격 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        if SpinAttack.image == None:
            SpinAttack.image = load_image('Resource/Character/KirbySpinAttack.png')
    def enter(self, e):
        initial = self.kirby.judgement_key_flag(e)
        if initial:
            self.kirby.frame = 0
            self.kirby.wait_time = get_time()
    def exit(self, e):
        pass
    def do(self):
        self.kirby.frame = (self.kirby.frame + 3 * FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8
        self.kirby.stopped = False
        self.kirby.yv = 0  # 체공을 위해 중력 무시
        if self.kirby.flag == 'RIGHT' or self.kirby.flag == 'LEFT':
            self.kirby.x += self.kirby.dir * WALK_SPEED_PPS * game_framework.frame_time
        if get_time() - self.kirby.wait_time > 1 / ACTION_PER_TIME:
            self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        if self.kirby.face_dir == 1:
            SpinAttack.image.clip_draw(int(self.kirby.frame) * 48, 0, 48, 48, self.kirby.x, self.kirby.y - (7 * SCALE), 48 * SCALE, 48 * SCALE)
        else:
            SpinAttack.image.clip_composite_draw(int(self.kirby.frame) * 48, 0, 48, 48, 0, 'h', self.kirby.x,self.kirby.y - (7 * SCALE), 48 * SCALE, 48 * SCALE)
        draw_rectangle(*self.get_bb())
    def get_bb(self):
        return (self.kirby.x - (48 * SCALE / 2), self.kirby.y - (48 * SCALE / 2) - (7 * SCALE),
                self.kirby.x + (48 * SCALE / 2), self.kirby.y + (48 * SCALE / 2) - (7 * SCALE))

class IdleSuperJump:  # 커비 슈퍼 점프 대기 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        self.animation = True
        self.next_animation = False
        if IdleSuperJump.image == None:
            IdleSuperJump.image = load_image('Resource/Character/KirbyIdleRise.png')
    def enter(self, e):
        initial = self.kirby.judgement_key_flag(e)
        if initial:
            self.kirby.frame = 0
            self.animation = True
            self.next_animation = False
            self.kirby.yv = SUPER_JUMP_SPEED_PPS
    def exit(self, e):
        if not self.animation and not self.next_animation:
            IdleSuperJump.image = load_image('Resource/Character/KirbyIdleRise.png')
        print(f'{self.kirby.dir}, {self.kirby.flag}, IdleSuperJump')
    def do(self):
        if not self.animation and not self.next_animation: # 모든 애니메이션 종료 후 대기 시간 체크
            if get_time() - self.kirby.wait_time > self.kirby.frame_time and self.kirby.yv - GRAVITY_PPS * game_framework.frame_time <= 0: # 다음 프레임에서 속도가 0 이하가 되면(최고점 도달):
                self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
        else: # 애니메이션 재생
            if self.animation: # 첫번째 애니메이션 재생
                self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 2
                if self.kirby.frame < 1:
                    self.kirby.frame_time = get_time()
                if self.kirby.yv - GRAVITY_PPS * game_framework.frame_time <= 20:
                    self.animation = False
                    self.next_animation = True
                    self.kirby.frame = 0
                    self.kirby.wait_time = self.kirby.frame_time = get_time()
                    IdleSuperJump.image = load_image('Resource/Character/KirbyIdleSuperJump.png')
            elif self.next_animation: # 두번째 애니메이션 재생
                self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 3
                if 0 <= self.kirby.frame < 1:
                    self.kirby.frame_time = get_time()
                if self.kirby.frame >= 2:
                    self.kirby.frame_time = get_time() - self.kirby.frame_time
                    self.kirby.wait_time = get_time()
                    self.next_animation = False
        if self.kirby.flag == 'RIGHT' or self.kirby.flag == 'LEFT':
            self.kirby.x += self.kirby.dir * WALK_SPEED_PPS * game_framework.frame_time
        self.kirby.stopped = False
    def draw(self):
        if self.kirby.face_dir == 1:
            IdleSuperJump.image.clip_draw(int(self.kirby.frame) * 48, 0, 48, 48, self.kirby.x, self.kirby.y, 48 * SCALE, 48 * SCALE)
        else:
            IdleSuperJump.image.clip_composite_draw(int(self.kirby.frame) * 48, 0, 48, 48, 0, 'h', self.kirby.x, self.kirby.y, 48 * SCALE, 48 * SCALE)

class SuperJump:  # 커비 슈퍼 점프 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        if SuperJump.image == None:
            SuperJump.image = load_image('Resource/Character/KirbySuperJump.png')
    def enter(self, e):
        initial = self.kirby.judgement_key_flag(e)
        if initial:
            if up_down(e):
                self.kirby.yv = JUMP_SPEED_PPS / 2
                self.kirby.stopped = False
            else:
                self.kirby.frame = 0
                self.kirby.wait_time = get_time()
    def exit(self, e):
        pass
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8
        if self.kirby.y < 0 - (48 * SCALE):
            self.kirby.state_machine.handle_state_event(('FALLOUT', None))
        if self.kirby.stopped:
            self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
        if get_time() - self.kirby.wait_time > 3 / ACTION_PER_TIME:
            self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
        if self.kirby.flag == 'RIGHT' or self.kirby.flag == 'LEFT':
            self.kirby.x += 1.5 * self.kirby.dir * WALK_SPEED_PPS * game_framework.frame_time
    def draw(self):
        if self.kirby.face_dir == 1:
            SuperJump.image.clip_draw(int(self.kirby.frame) * 48, 0, 48, 48, self.kirby.x, self.kirby.y + (3 * SCALE), 48 * SCALE, 48 * SCALE)
        else:
            SuperJump.image.clip_composite_draw((int(self.kirby.frame) % 8) * 48, 0, 48, 48, 0, 'h', self.kirby.x,self.kirby.y + (3 * SCALE), 48 * SCALE, 48 * SCALE)

class EndSuperJump:  # 커비 슈퍼 점프 종료 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        self.animation = True
        self.next_animation = False
        if EndSuperJump.image == None:
            EndSuperJump.image = load_image('Resource/Character/KirbyIdleSuperJump.png')
    def enter(self, e):
        initial = self.kirby.judgement_key_flag(e)
        if initial:
            self.kirby.frame = 3
            self.animation = True
            self.next_animation = False
            EndSuperJump.image = load_image('Resource/Character/KirbyIdleSuperJump.png')
    def exit(self, e):
        if not self.animation and not self.next_animation and self.kirby.vy >= JUMP_SPEED_PPS:
            EndSuperJump.image = load_image('Resource/Character/KirbyIdleSuperJump.png')
        print(f'{self.kirby.dir}, {self.kirby.flag}, EndSuperJump')
    def do(self):
        if self.kirby.y < 0 - (48 * SCALE):
            self.kirby.state_machine.handle_state_event(('FALLOUT', None))
        if not self.animation and not self.next_animation: # 두번째 애니메이션 변경 후 낙하 체크
            self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 2
            if self.kirby.stopped:
                self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
        else: # 애니메이션 재생
            if self.animation: # 첫번째 애니메이션 재생
                self.kirby.frame = self.kirby.frame - FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time
                if 1 <= self.kirby.frame < 2:
                    self.kirby.frame_time = get_time()
                if self.kirby.frame <= 0:
                    self.kirby.frame = 0
                    self.kirby.frame_time = get_time() - self.kirby.frame_time
                    self.kirby.wait_time = get_time()
                    self.animation = False
                    self.next_animation = True
            elif self.next_animation: # 두번째 애니메이션 재생
                if get_time() - self.kirby.wait_time > self.kirby.frame_time:
                    EndSuperJump.image = load_image('Resource/Character/KirbyIdleFall.png')
                    self.next_animation = False
        self.kirby.stopped = False
        if self.kirby.flag == 'RIGHT' or self.kirby.flag == 'LEFT':
            self.kirby.x += self.kirby.dir * WALK_SPEED_PPS * game_framework.frame_time
    def draw(self):
        if self.kirby.face_dir == 1:
            EndSuperJump.image.clip_draw(int(self.kirby.frame) * 48, 0, 48, 48, self.kirby.x, self.kirby.y, 48 * SCALE, 48 * SCALE)
        else:
            EndSuperJump.image.clip_composite_draw(int(self.kirby.frame) * 48, 0, 48, 48, 0, 'h', self.kirby.x, self.kirby.y, 48 * SCALE, 48 * SCALE)

class IdleFall: #커비 점프 낙하 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        if IdleFall.image == None:
            IdleFall.image = load_image('Resource/Character/KirbyIdleFall.png')
    def enter(self, e):
        initial = self.kirby.judgement_key_flag(e)
        if initial:
            self.kirby.frame = 0
    def exit(self, e):
        pass
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 2
        if self.kirby.y < 0 - (48 * SCALE):
            self.kirby.state_machine.handle_state_event(('FALLOUT', None))
        if self.kirby.flag == 'RIGHT' or self.kirby.flag == 'LEFT':
            self.kirby.x += self.kirby.dir * WALK_SPEED_PPS * game_framework.frame_time
        if self.kirby.stopped:
            self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        if self.kirby.face_dir == 1:
            IdleFall.image.clip_draw(int(self.kirby.frame) * 48, 0, 48, 48, self.kirby.x, self.kirby.y, 48 * SCALE, 48 * SCALE)
        else:
            IdleFall.image.clip_composite_draw(int(self.kirby.frame) * 48, 0, 48, 48, 0, 'h', self.kirby.x,self.kirby.y, 48 * SCALE, 48 * SCALE)

class Fall: #커비 점프 착지 및 구르기 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        self.kirby.frame = 0
        self.animation = True
        if Fall.image == None:
            Fall.image = load_image('Resource/Character/KirbyFall.png')
    def enter(self, e):
        initial = self.kirby.judgement_key_flag(e)
        if initial:
            self.kirby.frame = 0
            self.animation = True
            self.kirby.dir *= 2
    def exit(self, e):
        pass
    def do(self):
        self.kirby.frame = (self.kirby.frame + 1.5 * FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 12
        self.kirby.x += self.kirby.dir * WALK_SPEED_PPS * game_framework.frame_time
        self.kirby.stopped = False
        if self.kirby.y < 0 - (48 * SCALE):
            self.kirby.state_machine.handle_state_event(('FALLOUT', None))
        if not self.animation:
            if get_time() - self.kirby.wait_time > self.kirby.frame_time:
                self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
        else:
            if 9 <= self.kirby.frame < 10:
                self.kirby.frame_time = get_time()
            elif self.kirby.frame >= 11:
                self.kirby.frame_time = get_time() - self.kirby.frame_time
                self.kirby.wait_time = get_time()
                self.animation = False
    def draw(self):
        if self.kirby.face_dir == 1:
            Fall.image.clip_draw(int(self.kirby.frame) * 48, 0, 48, 96, self.kirby.x, self.kirby.y - (3 * SCALE), 48 * SCALE, 96 * SCALE)
        else:
            Fall.image.clip_composite_draw(int(self.kirby.frame) * 48, 0, 48, 96, 0, 'h', self.kirby.x,self.kirby.y - (3 * SCALE), 48 * SCALE, 96 * SCALE)

class IdleAttack: #커비 공격 대기 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        self.flag = None
        if IdleAttack.image == None:
            IdleAttack.image = load_image('Resource/Character/KirbyIdleAttack.png')
    def enter(self, e):
        if after_delay_time_out(e): # 끝나는 모션
            self.flag = 'AFTER_DELAY_TIMEOUT'
            if self.kirby.flag == 'LEFT':
                self.kirby.face_dir = -1
            elif self.kirby.flag == 'RIGHT':
                self.kirby.face_dir = 1
        self.kirby.frame = 0
        self.kirby.wait_time = get_time()
    def exit(self, e):
        if self.kirby.dir != 0:
            if right_down(e) or right_up(e):
                self.kirby.flag = 'IDLE'
                self.kirby.face_dir = 1
            elif left_down(e) or left_up(e):
                self.kirby.flag = 'IDLE'
                self.kirby.face_dir = -1
        else: # 정지상태 a 키 진입
            if self.kirby.flag == 'IDLE':
                if right_down(e) or left_up(e):
                    self.kirby.flag = 'RIGHT'
                    self.kirby.face_dir = 1
                elif left_down(e) or right_up(e):
                    self.kirby.flag = 'LEFT'
                    self.kirby.face_dir = -1
            elif self.kirby.flag == 'RIGHT':
                if left_down(e) or right_up(e):
                    self.kirby.flag = 'IDLE'
            elif self.kirby.flag == 'LEFT':
                if right_down(e) or left_up(e):
                    self.kirby.flag = 'IDLE'
        print(f'{self.kirby.dir}, {self.kirby.face_dir}, {self.kirby.flag}, IdleAttack')
    def do(self):
        if get_time() - self.kirby.wait_time > 0.25 / ACTION_PER_TIME:
            if self.flag == 'AFTER_DELAY_TIMEOUT':
                self.kirby.state_machine.handle_state_event(('AFTER_DELAY_TIMEOUT', None))
            else:
                self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        if self.kirby.face_dir == 1:
            IdleAttack.image.clip_draw(int(self.kirby.frame) * 96, 0, 96, 48, self.kirby.x, self.kirby.y - (11 * SCALE), 96 * SCALE, 48 * SCALE)
        else:
            IdleAttack.image.clip_composite_draw(int(self.kirby.frame) * 96, 0, 96, 48, 0, 'h', self.kirby.x, self.kirby.y - (11 * SCALE), 96 * SCALE, 48 * SCALE)

class IdleSlashAttack: #커비 베기 공격 대기 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        self.animation = True
        if IdleSlashAttack.image == None:
            IdleSlashAttack.image = load_image('Resource/Character/KirbyIdleSlashAttack.png')
    def enter(self, e):
        self.kirby.frame = 0
        self.animation = True
    def exit(self, e):
        if self.kirby.dir != 0:
            self.kirby.flag = 'IDLE'
            if right_down(e) or right_up(e):
                self.kirby.face_dir = 1
            elif left_down(e) or left_up(e):
                self.kirby.face_dir = -1
            else:
                if self.kirby.face_dir == 1:
                    self.kirby.flag = 'RIGHT'
                elif self.kirby.face_dir == -1:
                    self.kirby.flag = 'LEFT'
        else:
            if right_down(e) or left_up(e):
                self.kirby.flag = 'RIGHT'
                self.kirby.face_dir = 1
            elif left_down(e) or right_up(e):
                self.kirby.flag = 'LEFT'
                self.kirby.face_dir = -1
        print(f'{self.kirby.dir}, {self.kirby.flag}, IdleSlashAttack')
    def do(self):
        if self.kirby.y < 0 - (48 * SCALE):
            self.kirby.state_machine.handle_state_event(('FALLOUT', None))
        if not self.animation:
            if get_time() - self.kirby.wait_time > self.kirby.frame_time:
                self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
        else:
            self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 5
            if 2 <= self.kirby.frame < 3:
                self.kirby.frame_time = get_time()
            if self.kirby.frame >= 4:
                self.kirby.frame_time = get_time() - self.kirby.frame_time
                self.kirby.wait_time = get_time()
                self.animation = False
    def draw(self):
        if self.kirby.face_dir == 1:
            IdleSlashAttack.image.clip_draw(int(self.kirby.frame) * 96, 0, 96, 48, self.kirby.x, self.kirby.y, 96 * SCALE, 48 * SCALE)
        else:
            IdleSlashAttack.image.clip_composite_draw(int(self.kirby.frame) * 96, 0, 96, 48, 0, 'h', self.kirby.x,self.kirby.y, 96 * SCALE, 48 * SCALE)

class SlashAttack: #커비 베기 공격 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        self.animation = True
        if SlashAttack.image == None:
            SlashAttack.image = load_image('Resource/Character/KirbySlashAttack.png')
    def enter(self, e):
        if right_up(e) or left_up(e):
            if self.kirby.flag == 'LEFT' and right_up(e):  # 왼쪽 키다운
                self.kirby.flag = 'LEFT'
            elif self.kirby.flag == 'RIGHT' and left_up(e):  # 오른쪽 키다운
                self.kirby.flag = 'RIGHT'
            elif self.kirby.flag == 'IDLE':  # 둘다 키다운
                if right_up(e):
                    self.kirby.flag = 'LEFT'
                elif left_up(e):
                    self.kirby.flag = 'RIGHT'
            else:  # 키다운 없음
                self.kirby.flag = 'IDLE'  # 정지 상태 변경
        elif right_down(e) or right_double_tap(e):
            if self.kirby.flag == 'LEFT':  # 왼쪽 키다운
                    self.kirby.flag = 'IDLE'  # 정지 상태 변경
            else:  # 키다운 없음
                    self.kirby.flag = 'RIGHT'
        elif left_down(e) or left_double_tap(e):
            if self.kirby.flag == 'RIGHT':  # 오른쪽 키다운
                self.kirby.flag = 'IDLE'  # 정지 상태 변경
            else:  # 키다운 없음
                self.kirby.flag = 'LEFT'
        else:  # 최초 진입
            self.kirby.frame = 0
            self.animation = True
    def exit(self, e):
        if after_delay_time_out(e):
            if self.kirby.flag == 'IDLE':
                self.kirby.dir = 0
        print(f'{self.kirby.dir}, {self.kirby.flag}, SlashAttack')
    def do(self):
        if not self.animation:
            if get_time() - self.kirby.wait_time > self.kirby.frame_time:
                self.kirby.state_machine.handle_state_event(('AFTER_DELAY_TIMEOUT', None))
                print(f'{self.kirby.dir}, {self.kirby.flag}, SlashAttack AD')
        else:
            self.kirby.frame = (self.kirby.frame + 3 * FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8
            if 5 <= self.kirby.frame < 6:
                self.kirby.frame_time = get_time()
            if self.kirby.frame >= 7:
                self.kirby.frame_time = get_time() - self.kirby.frame_time
                self.kirby.wait_time = get_time()
                self.animation = False
    def draw(self):
        if self.kirby.face_dir == 1:
            SlashAttack.image.clip_draw(int(self.kirby.frame) * 96, 0, 96, 48, self.kirby.x, self.kirby.y - (7 * SCALE), 96 * SCALE, 48 * SCALE)
        else:
            SlashAttack.image.clip_composite_draw(int(self.kirby.frame) * 96, 0, 96, 48, 0, 'h', self.kirby.x,self.kirby.y - (7 * SCALE), 96 * SCALE, 48 * SCALE)
        draw_rectangle(*self.get_bb())
    def get_bb(self):
        return (self.kirby.x - (96 * SCALE / 2), self.kirby.y - (48 * SCALE / 2) - (7 * SCALE),
                self.kirby.x + (96 * SCALE / 2), self.kirby.y + (48 * SCALE / 2) - (7 * SCALE))

class RapidAttack: #커비 연속 공격 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        if RapidAttack.image == None:
            RapidAttack.image = load_image('Resource/Character/KirbyRapidAttack.png')
    def enter(self, e):
        if right_up(e) or left_up(e):
            if self.kirby.flag == 'LEFT' and right_up(e):  # 왼쪽 키다운
                self.kirby.flag = 'LEFT'
            elif self.kirby.flag == 'RIGHT' and left_up(e):  # 오른쪽 키다운
                self.kirby.flag = 'RIGHT'
            elif self.kirby.flag == 'IDLE':  # 둘다 키다운
                if right_up(e):
                    self.kirby.flag = 'LEFT'
                elif left_up(e):
                    self.kirby.flag = 'RIGHT'
            else:  # 키다운 없음
                self.kirby.flag = 'IDLE'  # 정지 상태 변경
        elif right_down(e) or right_double_tap(e):
            if self.kirby.flag == 'LEFT':  # 왼쪽 키다운
                self.kirby.flag = 'IDLE'  # 정지 상태 변경
            else:  # 키다운 없음
                self.kirby.flag = 'RIGHT'
        elif left_down(e) or left_double_tap(e):
            if self.kirby.flag == 'RIGHT':  # 오른쪽 키다운
                self.kirby.flag = 'IDLE'  # 정지 상태 변경
            else:  # 키다운 없음
                self.kirby.flag = 'LEFT'
        else:  # 최초 진입
            self.kirby.wait_time = get_time()
    def exit(self, e):
        print(f'{self.kirby.dir}, {self.kirby.flag}, RapidAttack')
    def do(self):
        self.kirby.frame = (self.kirby.frame + 3 * FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 9
        if get_time() - self.kirby.wait_time > 1 / ACTION_PER_TIME:
            self.kirby.state_machine.handle_state_event(('AFTER_DELAY_TIMEOUT', None))
    def draw(self):
        if self.kirby.face_dir == 1:
            RapidAttack.image.clip_draw(int(self.kirby.frame) * 96, 0, 96, 48, self.kirby.x, self.kirby.y - (7 * SCALE), 96 * SCALE, 48 * SCALE)
        else:
            RapidAttack.image.clip_composite_draw(int(self.kirby.frame) * 96, 0, 96, 48, 0, 'h', self.kirby.x,self.kirby.y - (7 * SCALE), 96 * SCALE, 48 * SCALE)
        draw_rectangle(*self.get_bb())
    def get_bb(self):
        return (self.kirby.x - (96 * SCALE / 2), self.kirby.y - (48 * SCALE / 2) - (7 * SCALE),
                self.kirby.x + (96 * SCALE / 2), self.kirby.y + (48 * SCALE / 2) - (7 * SCALE))

class IdleJumpAttack: #커비 점프 베기 공격 대기 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        if IdleJumpAttack.image == None:
            IdleJumpAttack.image = load_image('Resource/Character/KirbyIdleJumpAttack.png')
        self.animation = True
    def enter(self, e):
        self.kirby.frame = 0
        self.animation = True
    def exit(self, e):
        if self.kirby.dir != 0:
            self.kirby.flag = 'IDLE'
            if right_down(e) or right_up(e):
                self.kirby.face_dir = 1
            elif left_down(e) or left_up(e):
                self.kirby.face_dir = -1
            else:
                if self.kirby.face_dir == 1:
                    self.kirby.flag = 'RIGHT'
                elif self.kirby.face_dir == -1:
                    self.kirby.flag = 'LEFT'
        else:
            if right_down(e) or left_up(e):
                self.kirby.flag = 'RIGHT'
                self.kirby.face_dir = 1
            elif left_down(e) or right_up(e):
                self.kirby.flag = 'LEFT'
                self.kirby.face_dir = -1
        print(f'{self.kirby.dir}, {self.kirby.flag}, IdleJumpAttack')
    def do(self):
        if not self.animation:
            if get_time() - self.kirby.wait_time > self.kirby.frame_time:
                self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
        else:
            self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 4
            if 1 <= self.kirby.frame < 2:
                self.kirby.frame_time = get_time()
            if self.kirby.frame >= 3:
                self.kirby.frame_time = get_time() - self.kirby.frame_time
                self.kirby.wait_time = get_time()
                self.animation = False
    def draw(self):
        if self.kirby.face_dir == 1:
            IdleJumpAttack.image.clip_draw(int(self.kirby.frame) * 96, 0, 96, 48, self.kirby.x, self.kirby.y - (11 * SCALE), 96 * SCALE, 48 * SCALE)
        else:
            IdleJumpAttack.image.clip_composite_draw(int(self.kirby.frame) * 96, 0, 96, 48, 0, 'h', self.kirby.x, self.kirby.y - (11 * SCALE), 96 * SCALE, 48 * SCALE)

class RiseJumpAttack: #커비 점프 상승 베기 공격 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        if RiseJumpAttack.image == None:
            RiseJumpAttack.image = load_image('Resource/Character/KirbyRiseJumpAttack.png')
    def enter(self, e):
        initial = self.kirby.judgement_key_flag(e)
        if initial:
            self.kirby.frame = 0
            self.kirby.yv = JUMP_SPEED_PPS
    def exit(self, e):
        print(f'{self.kirby.dir}, {self.kirby.flag}, RiseJumpAttack')
    def do(self):
        self.kirby.stopped = False
        if self.kirby.flag == 'RIGHT' or self.kirby.flag == 'LEFT':
            self.kirby.x += self.kirby.dir * WALK_SPEED_PPS * game_framework.frame_time
        if self.kirby.yv - GRAVITY_PPS * game_framework.frame_time <= 10:
            self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        if self.kirby.face_dir == 1:
            RiseJumpAttack.image.clip_draw(int(self.kirby.frame) * 96, 0, 96, 48, self.kirby.x, self.kirby.y - (11 * SCALE), 96 * SCALE, 48 * SCALE)
        else:
            RiseJumpAttack.image.clip_composite_draw(int(self.kirby.frame) * 96, 0, 96, 48, 0, 'h', self.kirby.x, self.kirby.y - (11 * SCALE), 96 * SCALE, 48 * SCALE)
        draw_rectangle(*self.get_bb())
    def get_bb(self):
        return (self.kirby.x - (96 * SCALE / 2) + (12 * SCALE), self.kirby.y - (48 * SCALE / 2) - (7 * SCALE),
                self.kirby.x + (96 * SCALE / 2) - (12 * SCALE), self.kirby.y + (48 * SCALE / 2) - (7 * SCALE))

class JumpAttack: #커비 점프 공격 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        self.animation = True
        if JumpAttack.image == None:
            JumpAttack.image = load_image('Resource/Character/KirbyJumpAttack.png')
    def enter(self, e):
        initial = self.kirby.judgement_key_flag(e)
        if initial:
            self.kirby.frame = 0
            self.animation = True
    def exit(self, e):
        print(f'{self.kirby.dir}, {self.kirby.flag}, JumpAttack')
    def do(self):
        if self.kirby.stopped:
            self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
        if not self.animation:
            if get_time() - self.kirby.wait_time > self.kirby.frame_time:
                self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
        else:
            self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 7
            if 4 <= self.kirby.frame < 5:
                self.kirby.frame_time = get_time()
            if self.kirby.frame >= 6:
                self.kirby.frame_time = get_time() - self.kirby.frame_time
                self.kirby.wait_time = get_time()
                self.animation = False
        if self.kirby.flag == 'RIGHT' or self.kirby.flag == 'LEFT':
            self.kirby.x += self.kirby.dir * WALK_SPEED_PPS * game_framework.frame_time
    def draw(self):
        if self.kirby.face_dir == 1:
            JumpAttack.image.clip_draw(int(self.kirby.frame) * 96, 0, 96, 48, self.kirby.x, self.kirby.y, 96 * SCALE, 48 * SCALE)
        else:
            JumpAttack.image.clip_composite_draw(int(self.kirby.frame) * 96, 0, 96, 48, 0, 'h', self.kirby.x, self.kirby.y, 96 * SCALE, 48 * SCALE)
    def get_bb(self):
        return (self.kirby.x - (96 * SCALE / 2) + (12 * SCALE), self.kirby.y - (48 * SCALE / 2),
                self.kirby.x + (96 * SCALE / 2) - (12 * SCALE), self.kirby.y + (48 * SCALE / 2))

class FallJumpAttack: #커비 점프 낙하 베기 공격 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        if FallJumpAttack.image == None:
            FallJumpAttack.image = load_image('Resource/Character/KirbyFallJumpAttack.png')
    def enter(self, e):
        initial = self.kirby.judgement_key_flag(e)
        if initial:
            self.kirby.frame = 0
    def exit(self, e):
        print(f'{self.kirby.dir}, {self.kirby.flag}, FallJumpAttack')
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 2
        if self.kirby.y < 0 - (48 * SCALE):
            self.kirby.state_machine.handle_state_event(('FALLOUT', None))
        if self.kirby.flag == 'RIGHT' or self.kirby.flag == 'LEFT':
            self.kirby.x += self.kirby.dir * WALK_SPEED_PPS * game_framework.frame_time
        if self.kirby.stopped:
            self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        if self.kirby.face_dir == 1:
            FallJumpAttack.image.clip_draw(int(self.kirby.frame) * 96, 0, 96, 48, self.kirby.x, self.kirby.y - (2 * SCALE), 96 * SCALE, 48 * SCALE)
        else:
            FallJumpAttack.image.clip_composite_draw(int(self.kirby.frame) * 96, 0, 96, 48, 0, 'h', self.kirby.x, self.kirby.y - (2 * SCALE), 96 * SCALE, 48 * SCALE)
    def get_bb(self):
        return (self.kirby.x - (96 * SCALE / 2) + (15 * SCALE), self.kirby.y - (48 * SCALE / 2) - (7 * SCALE),
                self.kirby.x + (96 * SCALE / 2) - (15 * SCALE), self.kirby.y + (48 * SCALE / 2) + (4 * SCALE))

class EndJumpAttack: #커비 점프 베기 공격 착지 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        self.animation = True
        if EndJumpAttack.image == None:
            EndJumpAttack.image = load_image('Resource/Character/KirbyEndJumpAttack.png')
    def enter(self, e):
        self.kirby.frame = 0
        self.animation = True
        self.kirby.frame_time = get_time()
    def exit(self, e):
        if self.kirby.dir != 0: # 이동상태에서 진입
            self.kirby.flag = 'IDLE'
            if right_down(e) or right_up(e):
                self.kirby.face_dir = 1
            elif left_down(e) or left_up(e):
                self.kirby.face_dir = -1
            else:
                if self.kirby.face_dir == 1:
                    self.kirby.flag = 'RIGHT'
                elif self.kirby.face_dir == -1:
                    self.kirby.flag = 'LEFT'
        else: # 정지상태에서 진입
            if right_down(e) or left_up(e):
                self.kirby.flag = 'RIGHT'
                self.kirby.face_dir = 1
            elif left_down(e) or right_up(e):
                self.kirby.flag = 'LEFT'
                self.kirby.face_dir = -1
        print(f'{self.kirby.dir}, {self.kirby.flag}, EndJumpAttack')
    def do(self):
        if not self.animation:
            if get_time() - self.kirby.wait_time > self.kirby.frame_time:
                self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
        else:
            self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 2
            if self.kirby.frame >= 1:
                self.kirby.frame_time = get_time() - self.kirby.frame_time
                self.kirby.wait_time = get_time()
                self.animation = False
    def draw(self):
        if self.kirby.face_dir == 1:
            EndJumpAttack.image.clip_draw(int(self.kirby.frame) * 96, 0, 96, 48, self.kirby.x, self.kirby.y - (11 * SCALE), 96 * SCALE, 48 * SCALE)
        else:
            EndJumpAttack.image.clip_composite_draw(int(self.kirby.frame) * 96, 0, 96, 48, 0, 'h', self.kirby.x, self.kirby.y - (11 * SCALE), 96 * SCALE, 48 * SCALE)
        draw_rectangle(*self.get_bb())
    def get_bb(self):
        return (self.kirby.x - (96 * SCALE / 2) + (14 * SCALE), self.kirby.y - (48 * SCALE / 2) - (14 * SCALE),
                self.kirby.x + (96 * SCALE / 2) - (14 * SCALE), self.kirby.y + (48 * SCALE / 2) - (35 * SCALE))

class Hit: #커비 피격 상태
    image = None
    def __init__(self, kirby):
        self.kirby = kirby
        self.animation = True
        if Hit.image == None:
            Hit.image = load_image('Resource/Character/KirbyHit.png')
    def enter(self, e):
        initial = self.kirby.judgement_key_flag(e)
        if initial:
            self.kirby.frame = 0
            self.animation = True
            self.kirby.hp -= 1
    def exit(self, e):
        pass
    def do(self):
        if not self.animation:
            if get_time() - self.kirby.wait_time > self.kirby.frame_time:
                self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
        else:
            self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 16
            if 14 <= self.kirby.frame < 15:
                self.kirby.frame_time = get_time()
            if self.kirby.frame >= 15:
                self.kirby.frame_time = get_time() - self.kirby.frame_time
                self.kirby.wait_time = get_time()
                self.animation = False
    def draw(self):
        if self.kirby.face_dir == 1:
            Hit.image.clip_composite_draw(int(self.kirby.frame) * 48, 0, 48, 48, 0, 'h', self.kirby.x,self.kirby.y - (8 * SCALE), 48 * SCALE, 48 * SCALE)
        else:
            Hit.image.clip_draw(int(self.kirby.frame) * 48, 0, 48, 48, self.kirby.x, self.kirby.y - (8 * SCALE), 48 * SCALE, 48 * SCALE)

class Guard: #커비 가드 상태
    image = None
    pattern = [0, 0, 0, 0, 1, 1, 1, 1]
    def __init__(self, kirby):
        self.kirby = kirby
        if Guard.image == None:
            Guard.image = load_image('Resource/Character/KirbyGuard.png')
    def enter(self, e):
        self.kirby.frame = 0
        self.kirby.wait_time = get_time()
    def exit(self, e):
        pass
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(Guard.pattern)
        if (get_time() - self.kirby.wait_time > 2 / ACTION_PER_TIME):
            self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
    def draw(self):
        if self.kirby.face_dir == 1:
            Guard.image.clip_draw(Guard.pattern[int(self.kirby.frame)] * 48, 0, 48, 48, self.kirby.x, self.kirby.y, 48 * SCALE, 48 * SCALE)
        else:
            Guard.image.clip_composite_draw(Guard.pattern[int(self.kirby.frame)] * 48, 0, 48, 48, 0, 'h', self.kirby.x,self.kirby.y, 48 * SCALE, 48 * SCALE)

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

class Star: #커비 별 상태
    image = None
    pattern = [0, 0, 1, 1]
    def __init__(self, kirby):
        self.kirby = kirby
        self.dir = 0
        self.tx, self.ty = 640, 480
        if Star.image == None:
            Star.image = load_image('Resource/Character/KirbyStar.png')
    def enter(self, e):
        initial = self.kirby.judgement_key_flag(e)
        if initial:
            self.kirby.frame = 0
            self.kirby.hp -= 10
    def exit(self, e):
        self.kirby.stopped = False
    def do(self):
        self.kirby.frame = (self.kirby.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % len(Star.pattern)
        self.kirby.stopped = True
        if self.distance_less_than(self.tx, self.ty, self.kirby.x, self.kirby.y, 0.5):
            self.kirby.state_machine.handle_state_event(('TIMEOUT', None))
        else:
            self.move_little(self.tx, self.ty)
    def draw(self):
        if self.kirby.face_dir == 1:
            Star.image.clip_draw(Star.pattern[int(self.kirby.frame)] * 48, 0, 48, 48, self.kirby.x, self.kirby.y, 48 * SCALE, 48 * SCALE)
        else:
            Star.image.clip_composite_draw(Star.pattern[int(self.kirby.frame)] * 48, 0, 48, 48, 0, 'h', self.kirby.x,self.kirby.y, 48 * SCALE, 48 * SCALE)
    def move_little(self, tx, ty):
        self.dir = math.atan2(ty - self.kirby.y, tx - self.kirby.x)
        distance = 3 * WALK_SPEED_PPS * game_framework.frame_time
        self.kirby.x += distance * math.cos(self.dir)
        self.kirby.y += distance * math.sin(self.dir)
    def distance_less_than(self, x1, y1, x2, y2, r):
        distance = (x1 - x2) ** 2 + (y1 - y2) ** 2
        return distance < (PIXEL_PER_METER * r) ** 2