import pygame

class Wall:
    def __init__(self, x,y,w,h, color = (255,0,0)):
        self.rect = pygame.Rect(x,y,w,h)
        self.color = color
        self.collide = True

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
