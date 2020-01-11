import math
import pygame
from pygame.locals import *
from ..editor import *

class SpawnPoint(pygame.sprite.Sprite):
    def get_points(self, lenght = None, offset=(0,0)):
        x,y = (30+offset[0],26+offset[1])
        if lenght == None: lenght = self.lenght
        sqrt3 = (math.sqrt(3) / 3) * lenght
        sqrt6 = (math.sqrt(3) / 6) * lenght
        return [
                (x, y + sqrt3),
                (x - lenght / 2, y - sqrt6),
                (x + lenght / 2, y - sqrt6)
        ]

    def __init__(self, x,y, lenght, color, player_id):
        super().__init__()
        self.lenght = lenght
        self.rect = pygame.Rect(x,y,lenght,lenght)
        self.org_rect = self.rect.copy()
        self.color = color
        self.player_id = player_id
        self.image = pygame.Surface((self.rect.w + 10, self.rect.h + 10), SRCALPHA)
        self.selectable = True

        self.points = self.get_points()

    def update(self, cam = None):
        self.rect = pygame.Rect(*(cam.get_offset(self.org_rect)))
        self.points = self.get_points()
        pygame.draw.polygon(self.image, self.color, self.points)

    def outline(self, surface, camera):
        color = (255,0,0)
        pts = self.get_points(self.lenght / camera.zoom, offset=self.org_rect)
        camera.draw_polygon(surface, color, pts, 5)

    def move(self, mp):
        self.org_rect = pygame.Rect(mp[0] - self.lenght / 2,
                                    mp[1] - self.lenght / 2,
                                    self.org_rect[2], self.org_rect[3])

    def get_properties(self):
        return ["Player_Id"]

    def switch_player_id(self, btn, args):
        self.player_id = (self.player_id + 1) % 2
        btn.set_text(f"player : {self.player_id}")

    def as_string(self):
        center_int = (int(v) for v in self.org_rect.center)
        return 'Spawn, {},{}, {}\n'.format(*center_int, self.player_id)

    def get_position(self):
        return (self.rect.center)
