import pygame
from pygame.locals import *

pygame.font.init()

class UIManager:
    def __init__(self):
        self.elements = []
        self.selected = -1

    def add(self, element):
        if element in self.elements:
            raise ValueError(f'{element} is already in the list')

        self.elements.append(element)

    def remove(self, element):
        if not element in self.elements:
            raise ValueError(f'{element} is not in the list')

        self.elements.remove(element)


    def update(self, mouse_position, mouse_pressed, events):
        for i,el in enumerate(self.elements):
            if el.is_hovered(mouse_position) and mouse_pressed:
                self.selected = i
                break
        else:
            self.selected = -1

        if self.selected != -1:
            self.elements[self.selected].update(mouse_position, (mouse_pressed, 0), events)
        return self.selected

    def draw(self, surface):
        for el in self.elements:
            el.draw(surface)

class UIElement:
    def __init__(self, x,y):
        self.x, self.y = x,y

    def draw(self, surface):
        raise NotImplementedError("UI Element draw")

    def update(self):
        raise NotImplementedError("UI Element draw")

class Slider(UIElement):
    def __init__(self, x,y,w,h, min_value,max_value, bg_color, fg_color):
        super().__init__(x,y)
        self.w,self.h = w,h
        self.min_value, self.max_value = min_value, max_value
        self.value = self.max_value
        self.draw_w = 0
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.w_ratio = self.w / self.max_value
        self.bg_color = bg_color
        self.fg_color = fg_color

        if self.min_value > self.max_value:
            raise ValueError(f"Min value can't be superior to max value : {self}")

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, self.fg_color, (self.x, self.y, self.draw_w, self.h))

    #Update is only called when the UI Element is the selected one
    def update(self, mouse_position, mouse_pressed, events):
        if mouse_pressed[0]:
            #normalize
            x = (mouse_position[0] - self.x) / self.w
            self.set_value(x)

    def is_hovered(self, mouse_position):
        return self.rect.collidepoint(mouse_position)

    def set_value(self, value):
        #clamp self.draw_w in [0, self.w]
        self.draw_w = max(0, min(value * self.w, self.w))

        #denormalize
        self.value = (value * (self.max_value - self.min_value) + self.min_value)

        #clamp self.value in [self.min_value; self.max_value]
        self.value = max(self.min_value, min(self.value, self.max_value))

BUTTON_TEXT = pygame.font.SysFont("Arial Black", 42)

class Button(UIElement):
    def set_text(self, text):
        self.text = BUTTON_TEXT.render(text, 1, (255,255,255))

    def __init__(self, x,y,w,h, text, color, callback, args):
        super().__init__(x,y)
        self.rect = pygame.Rect(self.x, self.y, w, h)
        self.color = color
        self.callback = callback
        self.args = args
        self.set_text(text)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        surface.blit(self.text, (self.x, self.y))

    def update(self, mouse_position, mouse_pressed, events):
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if mouse_pressed[0]:
                    self.callback(self, self.args)

    def is_hovered(self, mouse_position):
        return self.rect.collidepoint(mouse_position)

    def destroy(self, UIManager):
        UIManager.remove(self)
