from pico2d import *

class Button:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = None
        self.clicked = False
        self.scale = 1.0

    def is_clicked(self, mouse_x, mouse_y):
        return (self.x <= mouse_x <= self.x + self.width * self.scale and
                self.y <= mouse_y <= self.y + self.height * self.scale)
    def draw(self):
        if self.image:
            self.image.draw(self.x + (self.width * self.scale) // 2,
                            self.y + (self.height * self.scale) // 2,
                            self.width * self.scale,
                            self.height * self.scale)
        if self.clicked:
            draw_rectangle(*self.get_bb())

    def get_bb(self):
        return (self.x - self.scale, self.y,
                self.x + self.width * self.scale - self.scale,
                self.y + self.height * self.scale)

class Fight(Button):
    def __init__(self, x, y):
        super().__init__(x, y, 426, 325)
        self.image = load_image('Resource/UI/ButtonFight.png')

class Setting(Button):
    def __init__(self, x, y):
        super().__init__(x, y, 86, 86)
        self.image = load_image('Resource/UI/Setting.png')

class AddPlayer(Button):
    def __init__(self, x, y):
        super().__init__(x, y, 34, 66)
        self.scale = 1.6
        self.image = load_image('Resource/UI/ButtonAdd.png')

class RemovePlayer(Button):
    def __init__(self, x, y):
        super().__init__(x, y, 33, 62)
        self.scale = 1.6
        self.image = load_image('Resource/UI/ButtonRemove.png')

class Player1(Button):
    def __init__(self, x, y):
        super().__init__(x, y, 983, 421)
        self.scale = 0.5
        self.image = load_image('Resource/UI/SelectKirby1p.png')

class Player2(Button):
    def __init__(self, x, y):
        super().__init__(x, y, 1132, 483)
        self.scale = 0.43
        self.image = load_image('Resource/UI/SelectKirby2p.png')

class Computer(Button):
    def __init__(self, x, y):
        super().__init__(x, y, 401, 179)
        self.scale = 1.21
        self.image = load_image('Resource/UI/SelectComputer.png')

class Start(Button):
    def __init__(self, x, y):
        super().__init__(x, y, 740, 166)
        self.scale = 1.38
        self.image = load_image('Resource/UI/ButtonStart.png')