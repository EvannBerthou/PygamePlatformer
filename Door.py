import pygame

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
    def __init__(self, x,y,w,h, color = (0,255,0)):
        self.rect = (x,y,w,h)
        self.color = color
        self.collide = False
        self.border = 10
        self.player_id = 0
        self.lines = self.get_lines()

    def draw(self, surface, camera = None):
        for l in self.lines:
            if camera:
                camera.draw_line(surface, self.color, l[0], l[1], self.border)
            else:
                pygame.draw.line(surface, self.color, l[0], l[1], self.border)

    def has_collision(self, player_id):
        return self.player_id == player_id

    def get_properties():
        return ["ColorPicker", "Player_Id"]

    def switch_player_id(self, btn, args):
        self.player_id = (self.player_id + 1) % 2
        btn.set_text(f"player : {self.player_id}")
