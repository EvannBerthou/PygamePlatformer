import pygame
from data.editor import *

class Wall(pygame.sprite.Sprite):
    def __init__(self, x,y,w,h, color = (255,0,0)):
        super().__init__()
        self.org_rect = pygame.Rect(int(x),int(y),int(w),int(h))
        self.rect = pygame.Rect(x,y,w,h)
        self.color = color
        self.collide = True
        self.image = pygame.Surface((w,h))
        self.image.fill(self.color)
        self.selectable = True

        self.before_drag = None

    def update(self, cam = None):
        if cam:
            self.rect = pygame.Rect(*(cam.get_offset(self.org_rect)))
            self.image = pygame.Surface((self.rect.w,self.rect.h))
            self.image.fill(self.color)

    def outline(self, surface, camera):
        border = (self.org_rect[0],self.org_rect[1],self.org_rect[2],self.org_rect[3])
        color = invert_color(self.color)
        camera.draw_rect(surface, color, border, 5)

    def move(self, mp, drag_start, constraint):
        if constraint == "vertical":
            self.org_rect.x = self.before_drag[0] + mp[0] - drag_start[0]
        elif constraint == "horizontal":
            self.org_rect.y = self.before_drag[1] + mp[1] - drag_start[1]
        else:
            self.org_rect.x = self.before_drag[0] + mp[0] - drag_start[0]
            self.org_rect.y = self.before_drag[1] + mp[1] - drag_start[1]

    def has_collision(self, player_id):
        return self.collide

    def get_properties(self):
        return ["ColorPicker"]

    def on_collision(self, collider):
        return

    def on_collision_exit(self, collider):
        return

    def as_string(self):
        color_int = (int(v) for v in self.color)
        rect_int = [ int(self.org_rect.x), int(self.org_rect.y), int(self.org_rect.w), int(self.org_rect.h) ]
        return 'Wall, {},{},{},{}, {},{},{}\n'.format(*rect_int, *color_int)
