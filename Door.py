import pygame
from Color import invert_color

class Door:
    def get_lines(self):
        return [
                # TOP
                ((self.rect[0],self.rect[1]), (self.rect[0]+self.rect[2],self.rect[1])),
                # LEFT
                ((self.rect[0],self.rect[1]-(self.border/2-1)), (self.rect[0],self.rect[1]+self.rect[3])),
                # RIGHT
                ((self.rect[0]+self.rect[2],self.rect[1]-(self.border/2-1)),
                    (self.rect[0]+self.rect[2],self.rect[1]+self.rect[3])),
                # BOTTOM
                ((self.rect[0],self.rect[1]+self.rect[3]), (self.rect[0]+self.rect[2],self.rect[1]+self.rect[3]))
        ]
    def __init__(self, x,y,w,h, player_id):
        self.rect = pygame.Rect(x,y,w,h)
        self.player_id = player_id
        self.color = (255,0,0) if self.player_id == 1 else (0,0,255)
        self.collide = False
        self.border = 10
        self.lines = self.get_lines()

    def draw(self, surface, camera = None):
        for l in self.lines:
            if camera:
                camera.draw_line(surface, self.color, l[0], l[1], self.border)
            else:
                pygame.draw.line(surface, self.color, l[0], l[1], self.border)

    def outline(self, surface, camera):
        color = invert_color(self.color)
        b = self.border
        #create lines for the border
        pts = [
            ((self.lines[0][0][0]-b,self.lines[0][0][1]-b),(self.lines[0][1][0]+b,self.lines[0][1][1]-b)),
            ((self.lines[1][0][0]-b,self.lines[1][0][1]-b),(self.lines[1][1][0]-b,self.lines[1][1][1]+b)),
            ((self.lines[2][0][0]+b,self.lines[2][0][1]-b),(self.lines[2][1][0]+b,self.lines[2][1][1]+b)),
            ((self.lines[3][0][0]-b,self.lines[3][0][1]+b),(self.lines[3][1][0]+b,self.lines[3][1][1]+b)),
        ]
        for pt in pts:
            camera.draw_line(surface, color, pt[0], pt[1], self.border)

    def has_collision(self, player_id):
        return not self.player_id == player_id

    def get_properties(self):
        return ["ColorPicker", "Player_Id"]

    def switch_player_id(self, btn, args):
        self.player_id = (self.player_id + 1) % 2
        btn.set_text(f"player : {self.player_id}")
