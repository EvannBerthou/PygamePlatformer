import pygame
from pygame.locals import *
from data.utils.SpriteLoader import load_sprite

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


    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        for i,el in enumerate(self.elements):
            if el.is_hovered(mouse_position) and mouse_pressed:
                self.selected = i
                break
        else:
            self.selected = -1

        if self.selected != -1:
            self.elements[self.selected].update(mouse_position, (mouse_pressed, 0), mouse_rel, events)
        return self.selected

    def draw(self, surface):
        for el in self.elements:
            el.draw(surface)

    def clear(self):
        for element in self.elements:
            self.remove(element)

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
    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
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


class Button(UIElement):
    def set_text(self, text):
        self.text = self.font.render(text, 1, (255,255,255))

    def __init__(self, x,y,w,h, text, color, callback, args, center_text = False, font_size = 46):
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), font_size)
        super().__init__(x,y)
        self.rect = pygame.Rect(self.x, self.y, w, h)
        self.color = color
        self.callback = callback
        self.args = args
        self.set_text(text)
        self.center_text = center_text

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        if self.center_text:
            rect = self.text.get_rect(center=self.rect.center)
            surface.blit(self.text, rect)
        else:
            surface.blit(self.text, self.rect)

    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if mouse_pressed[0]:
                    self.callback(self, self.args)

    def is_hovered(self, mouse_position):
        return self.rect.collidepoint(mouse_position)

    def destroy(self, UIManager):
        UIManager.remove(self)

class ScrollView(UIElement):
    def __init__(self, x,y,w,h, bg_color):
        super().__init__(x,y)
        self.rect = pygame.Rect(x,y,w,h)
        self.elements = []
        self.bg_color = bg_color
        self.surface = pygame.Surface((w,h))
        self.org_rects = {}
        self.y = 0

    def add(self, element):
        if element in self.elements:
            print(f'{element} is already in {self}')
            return

        element.rect.x += self.rect.x
        element.rect.y += self.rect.y
        self.elements.append(element)

    def is_hovered(self, mouse_position):
        return self.rect.collidepoint(mouse_position)

    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        if mouse_pressed[0] == 1:
            self.update_surface(mouse_rel[1])

        for el in self.elements:
            if el.is_hovered(mouse_position):
                el.update(mouse_position, mouse_pressed, mouse_rel, events)

    def update_surface(self, rel):
        self.surface.fill(self.bg_color)
        self.y += rel

        if rel < 0 and self.elements[-1].rect.bottom < self.rect.h:
            self.y -= rel
            rel = 0

        if rel > 0 and self.elements[0].rect.top > 0:
            self.y = 0
            rel = 0

        for element in self.elements:
            element.rect.y += rel
            element.y += rel
            element.draw(self.surface)

    def draw(self, surface):
        surface.blit(self.surface, (0,0))

    def clear(self):
        self.elements.clear()

class SearchBar(UIElement):
    def __init__(self, x,y,w,h, callback_function):
        super().__init__(x,y)
        self.rect = pygame.Rect(x,y,w,h)
        self.elements = []
        self.callback_function = callback_function
        self.surface = pygame.Surface((w,h))
        self.glass_icon = load_sprite('seach_icon.png', (32,32))

        self.text = ""
        self.cursor = 0

        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 38)
        self.text_to_render = self.font.render(self.text, 1, (255,255,255))

    def key_pressed(self, event):
        if event.key == K_BACKSPACE: self.remove_letter()
        elif event.key == K_RETURN: return
        else: self.add_letter(event.unicode)
        self.callback_function(self.text)

    def add_letter(self, char):
        self.text += char
        self.cursor += 1
        self.text_to_render = self.font.render(self.text, 1, (255,255,255))

    def remove_letter(self):
        letter = self.text[self.cursor - 1] if self.cursor < len(self.text) else ""
        self.text = self.text[:self.cursor - 1] + self.text[self.cursor:]
        self.cursor -= 1
        if self.cursor < 0: self.cursor = 0

        self.text_to_render = self.font.render(self.text, 1, (255,255,255))

    def draw(self, surface):
        surface.blit(self.glass_icon, (self.x, self.y))
        pygame.draw.line(surface, (100,100,100), (self.rect.x, self.rect.y + self.rect.h),
                                                 (self.rect.x + self.rect.w, self.rect.y + self.rect.h), 2)
        surface.blit(self.text_to_render, (self.x + 35, self.y))

    def is_hovered(self, mouse_position):
        return False

class Toggle(UIElement):
    def __init__(self, x,y,w,h, text, callback_function):
        super().__init__(x,y)
        self.rect = pygame.Rect(x,y,w,h)
        self.surface = pygame.Surface((w,h), SRCALPHA)
        self.callback_function = callback_function

        self.activated = False

        pygame.draw.rect(self.surface, (200,200,200), (0,0,h,h))
        font = pygame.font.SysFont(pygame.font.get_default_font(), 38)
        text_to_render = font.render(text, 1, (255,255,255))
        self.surface.blit(text_to_render, (h + 5,0))

    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.activated = not self.activated
                self.callback_function(self.activated)

    def draw(self, surface):
        surface.blit(self.surface, (self.rect.x, self.rect.y))

    def is_hovered(self, mouse_position):
        return self.rect.collidepoint(mouse_position)

class DropDown(UIElement):
    def __init__(self, x,y,w,h, choices, selected_color, menu_color, callback):
        super().__init__(x,y)
        self.case_height = h
        h *= len(choices) + 1
        self.rect = pygame.Rect(x,y,w,h)
        self.surface = pygame.Surface((w, h), SRCALPHA)

        self.callback = callback

        self.selected_color = selected_color
        self.menu_color = menu_color

        self.choices = choices
        self.selected_choice = self.choices[0]
        self.opened = False

        self.surface.fill(self.selected_color)

        self.ui_manager = UIManager()
        for i,choice in enumerate(self.choices):
            btn = Button(self.rect.x, self.rect.y + self.case_height * (i + 1), self.rect.w, self.case_height,
                            choice, self.menu_color, self.set_choice, choice, font_size = 32)
            self.ui_manager.add(btn)

        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 32)
        choice_text = self.font.render(self.selected_choice, 1, (255,255,255))
        self.surface.blit(choice_text, (0,0))

    def set_choice(self, btn, choice):
        self.selected_choice = choice
        pygame.draw.rect(self.surface, self.selected_color, (0,0, self.rect.w, self.case_height))
        choice_text = self.font.render(self.selected_choice, 1, (255,255,255))
        self.surface.blit(choice_text, (0,0))
        self.callback(self.selected_choice)

    def draw(self, surface):
        if self.opened:
            surface.blit(self.surface, (self.rect.x, self.rect.y))
            self.ui_manager.draw(surface)
        else:
            surface.blit(self.surface, (self.rect.x, self.rect.y),
                        (0,0, self.rect.w, self.case_height))


    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        if self.opened:
            self.ui_manager.update(mouse_position, mouse_pressed, mouse_rel, events)
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.opened = not self.opened

    def is_hovered(self, mouse_position):
        return self.rect.collidepoint(mouse_position)
