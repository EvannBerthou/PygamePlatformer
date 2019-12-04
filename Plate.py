import pygame
from Color import invert_color

class Plate:
    def __init__(self, x,y,w,h, color = (255,0,0)):
        self.rect = pygame.Rect(x,y,w,30)
        self.color = color
        self.collide = False
        self.linked_to_id = -1

    def draw(self, surface, camera = None):
        if camera:
            camera.draw_rect(surface, self.color, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)

    def outline(self, surface, camera):
        border = (self.rect[0] - 5,self.rect[1] - 5,self.rect[2] + 10,self.rect[3] + 10)
        color = invert_color(self.color)
        camera.draw_rect(surface,color,border)

    def has_collision(self, player_id):
        return self.collide

    def get_properties(self):
        return ["Linker"]

    def as_string(self):
        color_int = (int(v) for v in self.color)
        rect_int = [ int(self.rect.x), int(self.rect.y), int(self.rect.w), int(self.rect.h) ]
        print(self.linked_to_id)
        return 'Plate, {},{},{},{}, {},{},{}, {}\n'.format(*rect_int, *color_int, self.linked_to_id)
