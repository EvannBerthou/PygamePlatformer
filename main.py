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

        self.player_1 = Player(K_q, K_d, K_SPACE, 0)
        self.player_2 = Player(K_LEFT, K_RIGHT, K_UP, 1)
        self.player_2.rect.x += 105

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

game = Game()
game.run()
