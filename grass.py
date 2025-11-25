from pico2d import *

class Grass:
    def __init__(self):
        self.x = 240
        self.y = 300
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