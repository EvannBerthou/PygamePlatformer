import pygame
from ..editor import *

class Plate(pygame.sprite.Sprite):
    def __init__(self, x,y,w,h, color = (255,0,0), linked_to_id = -1):
        super().__init__()
        self.org_rect = pygame.Rect(int(x),int(y),int(w),int(h))
        self.rect = self.org_rect.copy()
        self.color = color
        self.collide = False
        self.linked_to_id = linked_to_id
        self.linked_to = None
        self.players_on = []
        self.image = pygame.Surface((w,h))
        self.image.fill(self.color)
        self.selectable = True
        self.resizable = True
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

    def move(self, mp, drag_start, constraint, x_grid_size, y_grid_size):
        if constraint == 'snapping':
            x_cell = mp[0] // x_grid_size
            y_cell = mp[1] // y_grid_size
            corner_x = self.before_drag[0] // x_grid_size
            corner_y = self.org_rect.y // y_grid_size

            delta_x = (drag_start[0] - self.before_drag[0]) // x_grid_size
            delta_y = (drag_start[1] - self.before_drag[1]) // x_grid_size
            self.org_rect.x = (x_cell - delta_x) * x_grid_size
            self.org_rect.y = (y_cell - delta_y) * y_grid_size
        elif constraint == "vertical":
            self.org_rect.x = self.before_drag[0] + mp[0] - drag_start[0]
        elif constraint == "horizontal":
            self.org_rect.y = self.before_drag[1] + mp[1] - drag_start[1]
        else:
            self.org_rect.x = self.before_drag[0] + mp[0] - drag_start[0]
            self.org_rect.y = self.before_drag[1] + mp[1] - drag_start[1]

    def has_collision(self, player_id):
        return self.collide

    def get_properties(self):
        return ["Linker"]

    def on_collision(self, collider):
        if not self.players_on: #s'il n'y a aucun joueur sur la plaque
            self.linked_to.switch_status()
        if not collider in self.players_on:
            self.players_on.append(collider)

    def on_collision_exit(self, collider):
        self.players_on.remove(collider)
        if not self.players_on:
            self.linked_to.switch_status()

    def as_string(self):
        rect_int = [ int(self.org_rect.x), int(self.org_rect.y), int(self.org_rect.w), int(self.org_rect.h) ]
        return 'Plate, {},{},{},{}, {}\n'.format(*rect_int, self.linked_to_id)
