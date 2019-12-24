import pygame
from pygame.locals import SRCALPHA
from ..editor import *

class Door(pygame.sprite.Sprite):
    def get_lines(self):
        return [
                ((0, 0), (self.rect.w, 0)),
                ((0, 0), (0, self.rect.h)),
                ((0, self.rect.h), (self.rect.w, self.rect.h)),
                ((self.rect.w, 0), (self.rect.w, self.rect.h))
        ]

    def __init__(self, x,y,w,h, color, player_id = 0):
        super().__init__()
        self.rect = pygame.Rect(int(x),int(y),int(w),int(h))
        self.org_rect = self.rect.copy()
        self.player_id = player_id
        self.color = (255,0,0) if self.player_id == 1 else (0,0,255)
        self.collide = False
        self.border = 10
        self.lines = self.get_lines()
        self.image = pygame.Surface((w,h), SRCALPHA)
        for l in self.lines:
            pygame.draw.line(self.image, self.color, l[0], l[1], self.border)

    def update(self, cam = None):
        if cam:
            self.rect = pygame.Rect(*(cam.get_offset(self.org_rect)))
            self.image = pygame.Surface((self.rect.w,self.rect.h), SRCALPHA)
            for l in self.lines:
                pygame.draw.line(self.image, self.color, l[0], l[1], self.border)

    def outline(self, surface, camera):
        color = invert_color(self.color)
        b = self.border
        #create lines for the border
        pts = [
            ((self.lines[0][0][0]+b,self.lines[0][0][1]+b),(self.lines[0][1][0]-b,self.lines[0][1][1]+b)),
            ((self.lines[1][0][0]+b,self.lines[1][0][1]+b),(self.lines[1][1][0]+b,self.lines[1][1][1]-b)),
            ((self.lines[2][0][0]+b,self.lines[2][0][1]-b),(self.lines[2][1][0]-b,self.lines[2][1][1]-b)),
            ((self.lines[3][0][0]-b,self.lines[3][0][1]+b),(self.lines[3][1][0]-b,self.lines[3][1][1]-b)),
        ]
        for pt in pts:
            camera.draw_line(self.image, color, pt[0], pt[1], self.border)

    def move(self, dx,dy,zoom,ratio):
        self.org_rect = pygame.Rect(self.org_rect[0] + dx * (1 / zoom) * ratio[0],
                                    self.org_rect[1] + dy * (1 / zoom) * ratio[1],
                                    self.org_rect[2], self.org_rect[3])

    def has_collision(self, player_id):
        return not self.player_id == player_id

    def get_properties(self):
        return ["Player_Id"]

    def switch_player_id(self, btn, args):
        self.switch_status()
        btn.set_text(f"player : {self.player_id}")

    def switch_status(self):
        self.player_id = (self.player_id + 1) % 2
        self.color = (255,0,0) if self.player_id == 1 else (0,0,255)

    def on_collision(self, collider):
        return

    def on_collision_exit(self, collider):
        return

    def as_string(self):
        rect_int = [ int(self.rect.x), int(self.rect.y), int(self.rect.w), int(self.rect.h) ]
        return 'Door, {},{},{},{}, {}\n'.format(*rect_int, self.player_id)
