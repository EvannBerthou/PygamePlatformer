import pygame

class Door:
    def __init__(self, x,y,w,h, player_id, color = (0,255,0)):
        self.rect = pygame.Rect(x,y,w,h)
        self.color = color
        self.collide = False
        self.border = 10
        self.player_id = player_id

        self.lines = [
                # TOP
                ((self.rect.x,self.rect.y), (self.rect.x+self.rect.w,self.rect.y)),
                # LEFT
                ((self.rect.x,self.rect.y-(self.border/2-1)), (self.rect.x,self.rect.y+self.rect.h)),
                # RIGHT
                ((self.rect.x+self.rect.w,self.rect.y-(self.border/2-1)),
                    (self.rect.x+self.rect.w,self.rect.y+self.rect.h)),
                # BOTTOM
                ((self.rect.x,self.rect.y+self.rect.h), (self.rect.x+self.rect.w,self.rect.y+self.rect.h))
        ]

    def draw(self, surface, camera = None):
        for l in self.lines:
            pygame.draw.line(surface, self.color, l[0], l[1], self.border)

    def has_collision(self, player_id):
        return self.player_id == player_id
