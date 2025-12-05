from pico2d import *

class Background:
    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.width = width
        self.height = height
        self.image = None
        self.x_scale = 2.5
        self.y_scale = 3.75

    def draw(self):
        if self.image:
            self.image.draw(self.x + (self.width * self.x_scale) // 2,
                            self.y + (self.height * self.y_scale) // 2,
                            self.width * self.x_scale,
                            self.height * self.y_scale)

    def update(self):
        pass

class Ground(Background):
    def __init__(self):
        super().__init__(512, 192)
        self.image = load_image('Resource/BackGround/BackGroundGround.png')

class Space(Background):
    def __init__(self):
        super().__init__(512, 192)
        self.image = load_image('Resource/BackGround/BackGroundSpace.png')