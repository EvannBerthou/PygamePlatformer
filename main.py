import os
import pygame
from pygame.locals import *

from player import Player
from Wall import Wall
from Door import Door
from SpawnPoint import SpawnPoint
from Plate import Plate

from SaveManager import load_map

DESING_W, DESING_H = 1920,1080

class Background(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        background_img = pygame.image.load('Resources/background.png').convert()
        self.image = pygame.transform.scale(background_img,(DESING_W,DESING_H))
        self.rect = self.image.get_rect()

    def on_collision(self, collider):
        return

    def has_collision(self, player_id):
        return False

class Game:
    def __init__(self):
        self.w, self.h =  1152,648
        self.win = pygame.display.set_mode((self.w,self.h))
        self.blitting_surface = pygame.Surface((DESING_W,DESING_H), HWSURFACE)
        self.running = True

        self.player_1 = Player(K_q, K_d, K_SPACE, 0)
        self.player_2 = Player(K_LEFT, K_RIGHT, K_UP, 1)

        self.sol = Wall(0,DESING_H - 300,DESING_W,300)

        self.all_colliders = pygame.sprite.Group(
                Background(), self.player_1, self.player_2)

        self.clock = pygame.time.Clock()

        self.load_map()

    def run(self):
        while self.running:
            tick = self.clock.tick()
            print(self.clock.get_fps())

            keyboard_input = pygame.key.get_pressed()

            self.blitting_surface.fill((0,0,0))

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False

            self.all_colliders.update()

            #UPDATE
            self.player_1.c_update(self.all_colliders.sprites(), keyboard_input, tick)
            self.player_2.c_update(self.all_colliders.sprites(), keyboard_input, tick)

            #DRAW
            self.all_colliders.draw(self.blitting_surface)
            blit = pygame.transform.scale(self.blitting_surface, (self.w, self.h))
            self.win.blit(blit, blit.get_rect())
            pygame.display.update()

    def load_map(self, file_path = 'map'):
        colliders = load_map(file_path)
        for col in colliders:
            if isinstance(col, Plate):
                print("plate id",col.linked_to_id)
                if col.linked_to_id != -1:
                    linked_to = colliders[col.linked_to_id]
                    col.linked_to = linked_to
            if isinstance(col, SpawnPoint):
                player = col.player_id
                if player == 0:
                    self.player_1.set_position(col.get_position())
                elif player == 1:
                    self.player_2.set_position(col.get_position())
                else:
                    raise ValueError("Spawn point's Player_id is not valid")
            else:
                self.all_colliders.add(col)

game = Game()
game.run()
