import math
import pygame
from Color import invert_color

class SpawnPoint:
    def get_points(self, lenght = None):
        x,y = self.rect.x, self.rect.y
        if lenght == None: lenght = self.lenght
        sqrt3 = (math.sqrt(3) / 3) * lenght
        sqrt6 = (math.sqrt(3) / 6) * lenght
        return [
                (x, y + sqrt3),
                (x - lenght / 2, y - sqrt6),
                (x + lenght / 2, y - sqrt6)
        ]

    def __init__(self, x,y, lenght, color, player_id):
        self.lenght = lenght
        self.rect = pygame.Rect(x,y,lenght,lenght)
        self.color = color
        self.player_id = player_id

        self.points = self.get_points()


    def draw(self, surface, camera = None):
        if camera:
            camera.draw_polygon(surface, self.color, self.points)
        else:
            pygame.draw.polygon(surface, self.color, self.points)

    def outline(self, surface, camera):
        color = (255,0,0)
        pts = self.get_points(self.lenght + 10)
        camera.draw_polygon(surface, color, pts, 5)

    def get_properties(self):
        return ["Player_Id"]

    def switch_player_id(self, btn, args):
        self.player_id = (self.player_id + 1) % 2
        btn.set_text(f"player : {self.player_id}")
