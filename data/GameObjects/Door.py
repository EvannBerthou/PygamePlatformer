import pygame
from pygame.locals import SRCALPHA
from data.editor import *
from data.utils.SpriteLoader import load_sprite

class Door(pygame.sprite.Sprite):
    def __init__(self, x,y,w,h, color, player_id = 0):
        super().__init__()
        self.rect = pygame.Rect(int(x),int(y),int(w),int(h))
        self.org_rect = self.rect.copy()
        self.player_id = player_id
        self.color = (255,0,0) if self.player_id == 1 else (0,0,255)
        self.collide = False
        self.border = 10
        self.background = load_sprite('wall.png', (w,h))
        self.door_size = (88,122)
        self.door_sprite_blue = load_sprite('door_blue.png', self.door_size)
        self.door_sprite_red = load_sprite('door_red.png', self.door_size)
        door_sprite = self.door_sprite_blue if self.player_id == 0 else self.door_sprite_red
        self.image = pygame.Surface((w,h), SRCALPHA)
        self.image.blit(self.background, (0,0))
        self.image.blit(door_sprite, (0, self.rect.h - self.door_size[1]))
        self.selectable = True
        self.resizable = True
        self.before_drag = None

    def update(self, cam = None):
        if cam:
            self.rect = pygame.Rect(*(cam.get_offset(self.org_rect)))
            self.image = pygame.Surface((self.rect.w,self.rect.h), SRCALPHA)
            scaled_background = pygame.transform.scale(self.background, (self.rect.w, self.rect.h))
            self.image.blit(scaled_background, (0,0))
            door_sprite = self.door_sprite_blue if self.player_id == 0 else self.door_sprite_red
            scaled_door = pygame.transform.scale(door_sprite, cam.get_zoomed(self.door_size))
            self.image.blit(scaled_door, (0,self.rect.h - self.door_size[1] * cam.zoom))

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
        return not self.player_id == player_id

    def get_properties(self):
        return ["Transform","Player_Id"]

    def switch_player_id(self, btn, args):
        self.switch_status()
        btn.set_text(f"player : {self.player_id}")

    def switch_status(self):
        self.player_id = (self.player_id + 1) % 2
        self.color = (255,0,0) if self.player_id == 1 else (0,0,255)
        door_sprite = self.door_sprite_blue if self.player_id == 0 else self.door_sprite_red
        self.image.blit(door_sprite, (0, self.rect.h - self.door_size[1]))
        self.image.set_alpha(255)

    def on_collision(self, collider):
        if collider.player_id == self.player_id:
            self.image.set_alpha(150)

    def on_collision_exit(self, collider):
        if collider.player_id == self.player_id:
            self.image.set_alpha(255)

    def as_string(self):
        rect_int = [ int(self.org_rect.x), int(self.org_rect.y), int(self.org_rect.w), int(self.org_rect.h) ]
        return 'Door, {},{},{},{}, {}\n'.format(*rect_int, self.player_id)
