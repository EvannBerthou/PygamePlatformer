import pygame
from pygame.locals import *
from data.Level import LevelManager

DESING_W, DESING_H = 1920,1080

class Game:
    def __init__(self):
        self.w, self.h =  1152,648
        self.win = pygame.display.set_mode((self.w,self.h))
        self.blitting_surface = pygame.Surface((DESING_W,DESING_H), HWSURFACE)
        self.running = True

        self.clock = pygame.time.Clock()
        self.level_manager = LevelManager((DESING_W, DESING_H))

    def run(self):
        while self.running:
            tick = self.clock.tick()
            self.blitting_surface.fill((0,0,0))

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False

            self.level_manager.update(tick)
            self.level_manager.draw(self.blitting_surface)

            blit = pygame.transform.scale(self.blitting_surface, (self.w, self.h))
            self.win.blit(blit, blit.get_rect())
            pygame.display.update()

game = Game()
game.run()
