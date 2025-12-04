from pico2d import *

class Button:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = None
        self.clicked = False

    def is_clicked(self, mouse_x, mouse_y):
        return (self.x <= mouse_x <= self.x + self.width and
                self.y <= mouse_y <= self.y + self.height)
    def draw(self):
        if self.image:
            self.image.draw(self.x + self.width // 2, self.y + self.height // 2)
        if self.clicked:
            draw_rectangle(*self.get_bb())

    def get_bb(self):
        return (self.x, self.y, self.x + self.width, self.y + self.height)

class Fight(Button):
    def __init__(self, x, y):
        super().__init__(x, y, 426, 325)
        self.image = load_image('Resource/UI/ButtonFight.png')

class Setting(Button):
    def __init__(self, x, y):
        super().__init__(x, y, 86, 86)
        self.image = load_image('Resource/UI/Setting.png')