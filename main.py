import pygame
from pygame.locals import *

from player import Player

DESING_W, DESING_H = 1920,1080

class Game:
    def __init__(self):
        self.w, self.h =  1152,648
        self.win = pygame.display.set_mode((self.w,self.h))
        self.blitting_surface = pygame.Surface((DESING_W,DESING_H))
        self.running = True

        self.player = Player()

        self.sol = pygame.Rect(0,DESING_H - 300,DESING_W,300)

        self.colliders = [
                pygame.Rect(-10,0,10,DESING_H), #MUR GAUCHE
                pygame.Rect(DESING_W,0,20,DESING_H), #MUR DROIT
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
                pygame.draw.rect(self.blitting_surface, (255,0,0), col)

            blit = pygame.transform.scale(self.blitting_surface, (self.w, self.h))
            self.win.blit(blit, blit.get_rect())
            pygame.display.update()

game = Game()
game.run()
