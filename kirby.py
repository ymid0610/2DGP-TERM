from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_SPACE, SDLK_LEFT, SDLK_RIGHT, SDLK_UP, SDLK_DOWN, SDLK_a, SDLK_s, SDLK_d

from state_machine import StateMachine
import game_world

class Kirby: #부모 클래스 커비
    image = None
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0

        self.Idle = Idle(self)
        self.Down = Down(self)
        self.Walk = Walk(self)
        self.Dash = Dash(self)
        self.IdleDashAttack = IdleDashAttack(self)
        self.DashAttack = DashAttack(self)
        self.IdleJump = IdleJump(self)
        self.IdleRise = IdleRise(self)
        self.Jump = Jump(self)
        self.SpinAttack = SpinAttack(self)
        self.IdleSuperJump = IdleSuperJump(self)
        self.SuperJump = SuperJump(self)
        self.EndSuperJump = EndSuperJump(self)
        self.IdleFall = IdleFall(self)
        self.Fall = Fall(self)
        self.IdleLand = IdleLand(self)
        self.IdleAttack = IdleAttack(self)
        self.IdleSlashAttack = IdleSlashAttack(self)
        self.SlashAttack = SlashAttack(self)
        self.RapidAttack = RapidAttack(self)
        self.IdleJumpAttack = IdleJumpAttack(self)
        self.RiseJumpAttack = RiseJumpAttack(self)
        self.JumpAttack = JumpAttack(self)
        self.FallJumpAttack = FallJumpAttack(self)
        self.EndJumpAttack = EndJumpAttack(self)
        self.Hit = Hit(self)
        self.IdleGuard = IdleGuard(self)
        self.Guard = Guard(self)
        self.Win = Win(self)
        self.Star = Star(self)
        self.state_machine = StateMachine(self.Idle, {})
        if Kirby.image == None:
            Kirby.image = load_image('Resource/Character/KirbyIdle.png')

    def update(self):
        self.state_machine.update()
    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
    def draw(self):
        self.state_machine.draw()

class Idle: #커비 대기 상태
    def __init__(self, kirby):
        self.kirby = kirby
    def enter(self, e):
        self.kirby.dir = 0
    def exit(self, e):
        pass
    def do(self):
        self.kirby.frame = (self.kirby.frame + 1) % 2
    def draw(self):
        if self.kirby.face_dir == 1: # rightㅋ
            self.kirby.image.clip_draw(self.kirby.frame * 30, 0, 30, 40, self.kirby.x, self.kirby.y, 60, 80)

class Down: #커비 앉기 상태
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

class Walk: #커비 걷기 상태
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

class Dash: #커비 대쉬 상태
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

class IdleDashAttack: #커비 대쉬 공격 대기 상태
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

class DashAttack: #커비 대쉬 공격 상태
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

class IdleJump: #커비 점프 대기 상태
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

class IdleRise: #커비 점프 상승 상태
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

class Jump: #커비 점프 상태 (공중제비 애니메이션)
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