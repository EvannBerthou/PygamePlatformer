import pygame

class Wall:
    def __init__(self, x,y,w,h, color = (255,0,0)):
        self.rect = pygame.Rect(x,y,w,h)
        self.color = color
        self.collide = True

    def draw(self, surface, camera = None):
        if camera:
            camera.draw_rect(surface, self.color, self.rect)
        else:
            pygame.draw.rect(surface, self.color, self.rect)

    def has_collision(self, player_id):
        return self.collide

    def get_properties():
        return ["ColorPicker"]
