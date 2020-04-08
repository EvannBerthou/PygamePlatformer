import pygame

from UI import InputField

class Transform:
    def __init__(self, x,y, UIManager):
        self.x, self.y = x,y
        self.w, self.h = 320,110
        self.x_if = InputField(x,y, 150, 50, None, None, text_type=int, char_limit=4)
        self.y_if = InputField(x+160,y, 150, 50, None, None, text_type=int, char_limit=4)
        self.w_if = InputField(x,y+60, 150, 50, None, None, text_type=int, char_limit=4)
        self.h_if = InputField(x+160,y+60, 150, 50, None, None, text_type=int, char_limit=4)
        UIManager.add(self.x_if)
        UIManager.add(self.y_if)
        UIManager.add(self.w_if)
        UIManager.add(self.h_if)

    def draw(self, surface):
        surface.blit(self.x_if.image, (self.x_if.rect))
        surface.blit(self.y_if.image, (self.y_if.rect))
        surface.blit(self.w_if.image, (self.w_if.rect))
        surface.blit(self.h_if.image, (self.h_if.rect))

    def get_transform(self):
        x = self.x_if.text
        if x == '':
            x = 0
        y = self.y_if.text
        if y == '':
            y = 0
        w = self.w_if.text
        if w == '':
            w = 0
        h = self.h_if.text
        if h == '':
            h = 0
        return pygame.Rect(int(x),int(y),int(w),int(h))

    def set_transform(self, rect):
        position = rect.topleft
        size = rect.size
        self.x_if.set_text(position[0])
        self.y_if.set_text(position[1])
        self.w_if.set_text(size[0])
        self.h_if.set_text(size[1])

    def destroy(self, UIManager):
        UIManager.remove(self.x_if)
        UIManager.remove(self.y_if)
        UIManager.remove(self.w_if)
        UIManager.remove(self.h_if)

