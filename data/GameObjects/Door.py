import pygame
from pygame.locals import SRCALPHA
from data.editor import *
from data.utils.SpriteLoader import load_sprite

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
        self.background = load_sprite('wall.png', (w,h))
        self.door_size = (88,122)
        door_sprite_name = 'door_blue.png' if self.player_id == 0 else 'door_red.png'
        self.door_sprite = load_sprite(door_sprite_name, self.door_size)
        self.image = pygame.Surface((w,h), SRCALPHA)
        self.image.blit(self.background, (0,0))
        self.image.blit(self.door_sprite, (0, self.rect.h - self.door_size[1]))
        self.selectable = True

    def update(self, cam = None):
        if cam:
            self.rect = pygame.Rect(*(cam.get_offset(self.org_rect)))
            self.image = pygame.Surface((self.rect.w,self.rect.h), SRCALPHA)
            self.image.blit(self.background, (0,0))
            self.image.blit(self.door_sprite, (0,self.rect.h - self.door_size[1]))

    def outline(self, surface, camera):
        border = (self.org_rect[0],self.org_rect[1],self.org_rect[2],self.org_rect[3])
        color = invert_color(self.color)
        camera.draw_rect(surface, color, border, 5)

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
        door_sprite_name = 'door_blue.png' if self.player_id == 0 else 'door_red.png'
        self.door_sprite = load_sprite(door_sprite_name, self.door_size)

    def on_collision(self, collider):
        if collider.player_id == self.player_id:
            self.image.set_alpha(150)
            collider.grounded = False

    def on_collision_exit(self, collider):
        if collider.player_id == self.player_id:
            self.image.set_alpha(255)

    def as_string(self):
        rect_int = [ int(self.org_rect.x), int(self.org_rect.y), int(self.org_rect.w), int(self.org_rect.h) ]
        return 'Door, {},{},{},{}, {}\n'.format(*rect_int, self.player_id)
