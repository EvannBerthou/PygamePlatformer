import pygame
from pygame.locals import *
from data.utils.SpriteLoader import load_sprite

pygame.font.init()

class UIManager(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.selected = -1

    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        for i,el in enumerate(self.sprites()):
            if el.is_hovered(mouse_position):
                self.sprites()[self.selected].update(mouse_position, mouse_pressed, mouse_rel, events)
                self.selected = i
                break
        else:
            self.selected = -1

        return self.selected

class UIElement(pygame.sprite.Sprite):
    def __init__(self, x,y):
        super().__init__()
        self.x, self.y = x,y
        self.rect = pygame.Rect(x,y,1,1)

class Slider(UIElement):
    def __init__(self, x,y,w,h, min_value,max_value, bg_color, fg_color, callback = None, linked_text = None, whole_numbers = False
        super().__init__(x,y)
        self.w,self.h = w,h
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.image = pygame.Surface(self.rect.size)
        self.min_value, self.max_value = min_value, max_value
        self.value = self.max_value
        self.draw_w = 0
        self.w_ratio = self.w / self.max_value
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.callback = callback
        self.linked_text = linked_text
        self.draw()
        self.whole_numbers = whole_numbers

        if self.min_value > self.max_value:
            raise ValueError(f"Min value can't be superior to max value : {self}")

    def draw(self):
        self.image.fill(self.bg_color)
        pygame.draw.rect(self.image, self.fg_color, (0,0, self.draw_w, self.h))

    #Update is only called when the UI Element is the selected one
    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        if mouse_pressed[0]:
            #normalize
            x = (mouse_position[0] - self.x) / self.w
            self.set_value(x)
            self.draw()
            if self.callback: self.callback()
            if self.linked_text: self.linked_text.set_text(str(int(self.value)))

    def is_hovered(self, mouse_position):
        return self.rect.collidepoint(mouse_position)

    def set_value(self, value):
        if self.whole_numbers:
            ceiled_value = round(value * (self.max_value - self.min_value) + self.min_value)
            self.draw_w = max(0, min(ceiled_value / self.max_value* self.w, self.w))
            self.value = max(self.min_value, min(ceiled_value, self.max_value))
        else:
            #clamp self.draw_w in [0, self.w]
            self.draw_w = max(0, min(value * self.w, self.w))

            #denormalize
            self.value = (value * (self.max_value - self.min_value) + self.min_value)

            #clamp self.value in [self.min_value; self.max_value]
            self.value = max(self.min_value, min(self.value, self.max_value))
        self.draw()


class Button(UIElement):
    def set_text(self, text):
        self.text = self.font.render(text, 1, (255,255,255))
        w,h = self.rect.size
        self.image.fill(self.color)
        if self.center_text:
            rect = ((w - self.text.get_width()) / 2, (h - self.text.get_height()) / 2)
            self.image.blit(self.text, rect)
        else:
            self.image.blit(self.text, (0,0))

    def __init__(self, x,y,w,h, text, color, callback, args, center_text = False, font_size = 86, offset = None):
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), font_size)
        super().__init__(x,y)
        self.rect = pygame.Rect(self.x, self.y, w, h)
        self.image = pygame.Surface((w,h))
        self.color = color
        self.callback = callback
        self.args = args
        self.center_text = center_text
        self.set_text(text)
        self.hovered = False
        self.collision_rect = self.rect.copy()
        if offset:
            self.collision_rect.move_ip(offset)

    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.callback(self, self.args)

    def is_hovered(self, mouse_position):
        hovered = self.collision_rect.collidepoint(mouse_position)
        if hovered and not self.hovered:
            self.rect.inflate_ip(10,10)
        if not hovered and self.hovered:
            self.rect.inflate_ip(-10,-10)
        self.hovered = hovered
        return hovered

    def destroy(self, UIManager):
        UIManager.remove(self)

class ScrollView(UIElement):
    def __init__(self, x,y,w,h, bg_color, w_size, h_size, w_gap, h_gap):
        super().__init__(x,y)
        self.rect = pygame.Rect(x,y,w,h)
        self.image = pygame.Surface((w,h))
        self.grid = Grid(x,y,w,h, w_size, h_size, w_gap, h_gap)
        self.bg_color = bg_color
        self.org_rects = {}
        self.y = 0

    def add(self, ui_class, ui_params):
        self.grid.add(ui_class, ui_params)

    def is_hovered(self, mouse_position):
        return self.rect.collidepoint(mouse_position)

    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        self.grid.update(mouse_position, mouse_position, mouse_rel, events)
        if mouse_pressed[0] == 1:
            self.update_surface(mouse_rel[1])

        for el in self.grid.ui_manager.sprites():
            if el.is_hovered(mouse_position):
                el.update(mouse_position, mouse_pressed, mouse_rel, events)

    def update_surface(self, rel):
        self.y += rel

        if rel < 0 and self.grid.ui_manager.sprites()[-1].rect.bottom < self.rect.h:
            self.y -= rel
            rel = self.rect.h - self.grid.ui_manager.sprites()[-1].rect.bottom - self.grid.h_gap

        elif rel > 0 and self.grid.ui_manager.sprites()[0].rect.top > 0:
            self.y = 0
            rel = -(self.grid.ui_manager.sprites()[0].rect.top) + self.grid.h_gap

        self.grid.update_positions((0,rel))
        self.image = self.grid.image

    def clear(self):
        self.grid.clear()

class InputField(UIElement):
    def __init__(self, x,y,w,h, callback_function, icon, text_size = 70, text_type = str, char_limit = 0, offset = None):
        super().__init__(x,y)
        self.rect = pygame.Rect(x,y,w,h)
        self.elements = []
        self.callback_function = callback_function
        self.image = pygame.Surface((w,h), SRCALPHA)
        self.icon = None
        if icon:
            self.icon = load_sprite(icon, (64,64))

        self.text = ""
        self.cursor = 0
        self.text_offset = 70 if self.icon else 0
        self.text_width = 0

        self.font = pygame.font.SysFont(pygame.font.get_default_font(), text_size)
        self.text_to_render = self.font.render(self.text, 1, (255,255,255))
        self.selected = 0
        self.text_type = text_type
        self.char_limit = char_limit

        self.draw()

    def key_pressed(self, event):
        if event.key == K_BACKSPACE: self.remove_letter()
        elif event.key == K_RETURN: return
        else: self.add_letter(event.unicode)
        if self.callback_function: self.callback_function(self.text)
        self.text_width = self.text_to_render.get_width()
        self.draw()

    def add_letter(self, char):
        try:
            converted_char = self.text_type(char)
        except ValueError:
            print('Incorrect type')
            return
        if self.char_limit == 0 or len(self.text) < self.char_limit:
            if char.isalnum() or char == ' ':
                self.text += char
                self.cursor += 1
                self.text_to_render = self.font.render(self.text, 1, (255,255,255))

    def remove_letter(self):
        letter = self.text[self.cursor - 1] if self.cursor < len(self.text) else ""
        self.text = self.text[:self.cursor - 1] + self.text[self.cursor:]
        self.cursor -= 1
        if self.cursor < 0: self.cursor = 0

        self.text_to_render = self.font.render(self.text, 1, (255,255,255))

    def draw(self):
        self.image.fill((0,0,0,1))
        if self.icon:
            self.image.blit(self.icon, (0,0))
        #Bottom line
        pygame.draw.line(self.image, (100,100,100), (0,self.rect.h),
                                                    (self.rect.w, self.rect.y + self.rect.h), 2)
        if self.text != "":
            self.image.blit(self.text_to_render, (self.text_offset, 0))
        if self.selected:
            pygame.draw.line(self.image, (100,100,100), (self.text_offset + self.text_width, 0),
                                                        (self.text_offset + self.text_width, self.rect.h), 2)

    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        for event in events:
            if event.type == KEYDOWN:
                self.key_pressed(event)

    def is_hovered(self, mouse_position):
        self.draw()
        self.selected = self.rect.collidepoint(mouse_position)
        return self.selected

    def set_text(self, text):
        self.text = str(text)
        self.text_to_render = self.font.render(self.text, 1, (255,255,255))
        self.text_width = self.text_to_render.get_width()
        self.cursor = len(self.text)

class Toggle(UIElement):
    def __init__(self, x,y,w,h, text, callback_function):
        super().__init__(x,y)
        self.rect = pygame.Rect(x,y,w,h)
        self.image = pygame.Surface((w,h), SRCALPHA)
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
        self.image.fill((0,0,0,0))
        pygame.draw.rect(self.image, (200,200,200), (0,0,h,h))
        if self.activated:
            self.image.blit(self.tick, (0,0))
        self.image.blit(self.text_to_render, (h + 5,0))

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))

    def is_hovered(self, mouse_position):
        return self.rect.collidepoint(mouse_position)

class DropDown(UIElement):
    def __init__(self, x,y,w,h, choices, selected_color, menu_color, callback):
        super().__init__(x,y)
        self.case_height = h
        h *= len(choices) + 1
        self.choice_rect = pygame.Rect(x,y,w,self.case_height)
        self.rect = pygame.Rect(x,y,w,h)
        self.image = pygame.Surface((w, h), SRCALPHA)

        self.callback = callback

        self.selected_color = selected_color
        self.menu_color = menu_color

        self.choices = choices
        self.selected_choice = self.choices[0]
        self.opened = False

        self.image.fill(self.selected_color)

        self.ui_manager = UIManager()
        for i,choice in enumerate(self.choices):
            btn = Button(0, self.case_height * (i + 1), self.rect.w, self.case_height,
                            choice, self.menu_color, self.set_choice, choice, font_size = 32, offset = self.rect.topleft)
            self.ui_manager.add(btn)

        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 32)
        self.choice_text = self.font.render(self.selected_choice, 1, (255,255,255))
        self.image.blit(self.choice_text, (0,0))
        pygame.draw.rect(self.image, (0,0,0,0), (0, self.case_height, self.rect.w, self.rect.h))

    def set_choice(self, btn, choice):
        self.selected_choice = choice
        pygame.draw.rect(self.image, self.selected_color, (0,0, self.rect.w, self.case_height))
        self.choice_text = self.font.render(self.selected_choice, 1, (255,255,255))
        self.image.blit(self.choice_text, (0,0))
        self.callback(self.selected_choice)

    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        if self.opened:
            self.ui_manager.update(mouse_position, mouse_pressed, mouse_rel, events)
            self.image.fill(self.selected_color)
            self.image.blit(self.choice_text, (0,0))
            self.ui_manager.draw(self.image)
        for event in events:
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                self.opened = not self.opened
                if not self.opened:
                    pygame.draw.rect(self.image, (0,0,0,0), (0, self.case_height, self.rect.w, self.rect.h))
                if self.opened:
                    self.ui_manager.draw(self.image)

    def is_hovered(self, mouse_position):
        if self.opened:
            return self.rect.collidepoint(mouse_position)
        return self.choice_rect.collidepoint(mouse_position)

class LevelButton(Button):
    def __init__(self, x,y,w,h, map_name, map_author, color, callback, args, center_text = False, font_size = 46, offset = None):
        super().__init__(x,y,w,h, " ", color, callback, args, font_size = font_size, offset = offset)
        self.map_name = self.font.render(map_name, 1, (255,255,255))
        self.map_author = self.font.render(map_author, 1,(200,200,200))

        self.map_name_height = self.map_name.get_height()
        self.image.blit(self.map_name, (0,0))
        self.image.blit(self.map_author, (0,self.map_name_height))

class Grid(UIElement):
    def __init__(self, x,y,w,h, w_size, h_size, w_gap, h_gap):
        super().__init__(x,y)
        self.ui_manager = UIManager()
        self.rect = pygame.Rect(x,y,w,h)
        self.image = pygame.Surface((w,h), SRCALPHA)
        self.w_size, self.h_size = w_size, h_size
        self.w_gap, self.h_gap = w_gap, h_gap
        self.line = 0
        self.row = 0

    def add(self, ui_class, ui_params):
        if (self.line != 0 or self.row != 0) and self.row * (self.w_size + self.w_gap) + self.w_size > self.rect.w:
            self.line += 1
            self.row = 0

        x = self.row  * (self.w_size + self.w_gap) + self.w_gap
        y = self.line * (self.h_size + self.h_gap) + self.h_gap

        ui_element = ui_class(x,y,self.w_size,self.h_size, *ui_params, offset = (self.rect.x, self.rect.y))
        self.ui_manager.add(ui_element)
        self.row += 1
        self.ui_manager.draw(self.image)

    def update_positions(self, offset):
        self.rect.x += offset[0]
        self.rect.y += offset[1]
        for element in self.ui_manager.sprites():
            element.rect.x += offset[0]
            element.rect.y += offset[1]
        self.ui_manager.draw(self.image)


    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        self.ui_manager.update(mouse_position, mouse_pressed, mouse_rel, events)
        self.image.fill((0,0,0,0))
        self.ui_manager.draw(self.image)

    def is_hovered(self, mouse_position):
        return self.rect.collidepoint(mouse_position)

    def clear(self):
        self.line = 0
        self.row = 0
        self.ui_manager.empty()

class Image(UIElement):
    def __init__(self, x,y,w,h, image = None, color = None):
        super().__init__(x,y)
        self.rect = pygame.Rect(x,y,w,h)
        self.image = pygame.Surface((w,h), SRCALPHA)
        if image:
            self.image.blit(image, (0,0))
        if color:
            self.image.fill(color)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def update(self):
        return

    def is_hovered(self, mouse_position):
        return

class Text(UIElement):
    def set_text(self, text):
        text = str(text)
        self.image = self.font.render(text, 1, self.color)

    def __init__(self, x,y, text, size, color):
        super().__init__(x,y)
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), size)
        self.color = color
        self.set_text(text)
        self.rect = pygame.Rect((x,y), self.image.get_size())

    def is_hovered(self, mouse_position):
        return False
    
    def get_width(self):
        return self.image.get_width()
