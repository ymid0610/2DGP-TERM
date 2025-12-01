from pico2d import *

class Grass:
    def __init__(self, x = None, y = None):
        self.x = x if x is not None else 640
        self.y = y if y is not None else 240
        self.image = load_image('Resource/Map/Grass.png')

    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x, self.y)
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.x - 240, self.y + 24, self.x + 240, self.y + 24

    def handle_collision(self, group, other):
        pass

class Floor:
    def __init__(self):
        self.x = 640
        self.y = 24
        self.image = load_image('Resource/Map/GrassFloor.png')

    def update(self):
        pass

    def draw(self):
        self.image.draw(self.x, self.y)
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.x - 600, self.y + 24, self.x + 600, self.y + 24

    def handle_collision(self, group, other):
        pass