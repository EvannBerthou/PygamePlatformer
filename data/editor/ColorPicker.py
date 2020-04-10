import pygame

from UI import Slider


class ColorPicker:
    def __init__(self, x, y, UIManager):
        self.x, self.y = x, y
        self.w, self.h = 320, 190
        self.r = Slider(self.x + 10, self.y + 10, self.w - 20,
                        50, 0, 255, (150, 150, 150), (255, 0, 0))
        self.g = Slider(self.x + 10, self.y + 70, self.w - 20,
                        50, 0, 255, (150, 150, 150), (0, 255, 0))
        self.b = Slider(self.x + 10, self.y + 130, self.w - 20,
                        50, 0, 255, (150, 150, 150), (0, 0, 255))
        UIManager.add(self.r)
        UIManager.add(self.g)
        UIManager.add(self.b)

    def draw(self, surface):
        surface.blit(self.r.image, (self.r.rect.topleft))
        surface.blit(self.g.image, (self.g.rect.topleft))
        surface.blit(self.b.image, (self.b.rect.topleft))

    def get_color(self):
        return (self.r.value, self.g.value, self.b.value)

    def set_color(self, color):
        self.r.set_value(color[0] / 255)
        self.g.set_value(color[1] / 255)
        self.b.set_value(color[2] / 255)

    def destroy(self, UIManager):
        UIManager.remove(self.r)
        UIManager.remove(self.g)
        UIManager.remove(self.b)
