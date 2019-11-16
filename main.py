import pygame
from pygame.locals import *

from player import Player
from Wall import Wall
from Door import Door

DESING_W, DESING_H = 1920,1080

class Game:
    def __init__(self):
        self.w, self.h =  1152,648
        self.win = pygame.display.set_mode((self.w,self.h))
        self.blitting_surface = pygame.Surface((DESING_W,DESING_H))
        self.running = True

        self.player = Player()

        self.sol = Wall(0,DESING_H - 300,DESING_W,300)

        self.colliders = [
                Wall(-10,0,10,DESING_H), #MUR GAUCHE
                Wall(DESING_W,0,20,DESING_H), #MUR DROIT
                Door(100, DESING_H - 372,70,70),
                self.sol]

        self.clock = pygame.time.Clock()

    def run(self):
        while self.running:
            tick = self.clock.tick(60)

            keyboard_input = pygame.key.get_pressed()

            self.win.fill((0,0,0,))
            self.blitting_surface.fill((0,0,0))

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False

            #UPDATE
            self.player.update(self.colliders, keyboard_input, tick)

            #DRAW
            self.player.draw(self)
            for col in self.colliders:
                col.draw(self.blitting_surface)

            blit = pygame.transform.scale(self.blitting_surface, (self.w, self.h))
            self.win.blit(blit, blit.get_rect())
            pygame.display.update()

game = Game()
game.run()
