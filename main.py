import os
import pygame
from pygame.locals import *

from player import Player
from Wall import Wall
from Door import Door
from SpawnPoint import SpawnPoint

from SaveManager import load_map

DESING_W, DESING_H = 1920,1080

class Game:
    def __init__(self):
        self.w, self.h =  1152,648
        self.win = pygame.display.set_mode((self.w,self.h))
        self.blitting_surface = pygame.Surface((DESING_W,DESING_H))
        self.running = True

        background_img = pygame.image.load('Resources/background.png')
        self.background = pygame.transform.scale(background_img, (DESING_W, DESING_H))

        self.player_1 = Player(K_q, K_d, K_SPACE, 0)
        self.player_2 = Player(K_LEFT, K_RIGHT, K_UP, 1)

        self.sol = Wall(0,DESING_H - 300,DESING_W,300)

        self.colliders = [
                Wall(-10,0,10,DESING_H), #MUR GAUCHE
                Wall(DESING_W,0,20,DESING_H), #MUR DROIT
                Door(100, DESING_H - 372,70,70, 0),
                Door(600, DESING_H - 372,70,70, 1),
                self.sol]

        self.clock = pygame.time.Clock()

        self.load_map()

    def run(self):
        while self.running:
            tick = self.clock.tick(60)

            keyboard_input = pygame.key.get_pressed()

            self.win.fill((0,0,0,))
            self.blitting_surface.fill((0,0,0))
            self.blitting_surface.blit(self.background, (0,0))

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False

            #UPDATE
            self.player_1.update(self.colliders + [self.player_2], keyboard_input, tick)
            self.player_2.update(self.colliders + [self.player_1], keyboard_input, tick)

            #DRAW
            self.player_1.draw(self)
            self.player_2.draw(self)
            for col in self.colliders:
                col.draw(self.blitting_surface)

            blit = pygame.transform.scale(self.blitting_surface, (self.w, self.h))
            self.win.blit(blit, blit.get_rect())
            pygame.display.update()

    def load_map(self, file_path = 'map'):
        self.colliders.clear()
        self.colliders = load_map(file_path)
        for col in self.colliders.copy():
            if isinstance(col, SpawnPoint):
                player = col.player_id
                if player == 0:
                    self.player_1.set_position(col.get_position())
                elif player == 1:
                    self.player_2.set_position(col.get_position())
                else:
                    raise ValueError("Spawn point's Player_id is not valid")
                self.colliders.remove(col)

game = Game()
game.run()
