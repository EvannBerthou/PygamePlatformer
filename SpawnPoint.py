import math
import pygame
from Color import invert_color

class SpawnPoint:
    def __init__(self, x,y, lenght, color, player_id):
        self.rect = pygame.Rect(x,y,lenght,lenght)
        sqrt3 = (math.sqrt(3) / 3) * lenght
        sqrt6 = (math.sqrt(3) / 6) * lenght
        self.points = [
                (x, y + sqrt3),
                (x - lenght / 2, y - sqrt6),
                (x + lenght / 2, y - sqrt6)
        ]
        self.color = color
        self.player_id = player_id


    def draw(self, surface, camera = None):
        pygame.draw.polygon(surface, self.color, self.points)

    def outline(self, surface, camera):
        return
        color = invert_color(self.color)
        pygame.draw.polygon(surface, color, self.points)

    def get_properties(self):
        return ["Player_Id"]

    def switch_player_id(self, btn, args):
        self.player_id = (self.player_id + 1) % 2
        btn.set_text(f"player : {self.player_id}")
