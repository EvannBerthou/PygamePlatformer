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
        if mouse_pressed[0][0] == 1:
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
        self.glass_icon = load_sprite('seach_icon.png', (64,64))

        self.text = ""
        self.cursor = 0

        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 70)
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
        surface.blit(self.text_to_render, (self.x + 70, self.y))

    def is_hovered(self, mouse_position):
        return False

class Toggle(UIElement):
    def __init__(self, x,y,w,h, text, callback_function):
        super().__init__(x,y)
        self.rect = pygame.Rect(x,y,w,h)
        self.surface = pygame.Surface((w,h), SRCALPHA)
        self.callback_function = callback_function

        self.activated = False

        self.tick = load_sprite('tick.png', (h,h))
        font = pygame.font.SysFont(pygame.font.get_default_font(), 38)
        self.text_to_render = font.render(text, 1, (255,255,255))

        self.update_surface()

    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.activated = not self.activated
                self.callback_function(self.activated)
                self.update_surface()

    def update_surface(self):
        h = self.rect.h
        self.surface.fill((0,0,0,0))
        pygame.draw.rect(self.surface, (200,200,200), (0,0,h,h))
        if self.activated:
            self.surface.blit(self.tick, (0,0))
        self.surface.blit(self.text_to_render, (h + 5,0))

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

class LevelButton(Button):
    def __init__(self, x,y,w,h, map_name, map_author, color, callback, args, center_text = False, font_size = 46):
        super().__init__(x,y,w,h, " ", color, callback, args)
        self.map_name = self.font.render(map_name, 1, (255,255,255))
        self.map_author = self.font.render(map_author, 1,(200,200,200))

        self.map_name_height = self.map_name.get_height()

    def draw(self, surface):
        Button.draw(self, surface)
        surface.blit(self.map_name, self.rect)
        surface.blit(self.map_author, (self.rect.x, self.rect.y + self.map_name_height))

class Grid(UIElement):
    def __init__(self, x,y,w,h, w_size, h_size, w_gap, h_gap):
        super().__init__(x,y)
        self.ui_manager = UIManager()
        self.rect = pygame.Rect(x,y,w,h)
        self.w_size, self.h_size = w_size, h_size
        self.w_gap, self.h_gap = w_gap, h_gap
        self.line = 0
        self.row = 0

    def add(self, ui_class, ui_params):
        if (self.line != 0 or self.row != 0) and self.row * (self.w_size + self.w_gap) + self.w_size > self.rect.w:
            self.line += 1
            self.row = 0

        x = self.row  * (self.w_size + self.w_gap)
        y = self.line * (self.h_size + self.h_gap)

        ui_element = ui_class(x,y,self.w_size,self.h_size, *ui_params)
        self.ui_manager.add(ui_element)
        self.row += 1

    def update_positions(self, offset):
        self.rect.x += offset[0]
        self.rect.y += offset[1]
        for element in self.ui_manager.elements:
            element.rect.x += offset[0]
            element.rect.y += offset[1]


    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        self.ui_manager.update(mouse_position, mouse_pressed, mouse_rel, events)

    def draw(self, surface):
        self.ui_manager.draw(surface)

    def is_hovered(self, mouse_position):
        return self.rect.collidepoint(mouse_position)
