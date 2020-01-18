import UI
import os
import pygame
from pygame.locals import *

class Menu:
    def __init__(self, main_menu):
        self.ui_manager = UI.UIManager()
        self.main_menu = main_menu

    def draw(self, surface):
        raise NotImplementedError('draw function not implemented for this menu {}', self)

class MainScreenMenu(Menu):
    def __init__(self, main_menu):
        super().__init__(main_menu)
        self.ui_manager.add(UI.Button(self.main_menu.game.w / 2 - 75, self.main_menu.game.h / 2 - 60, 150, 35,
                            "Load Map", (150,150,150),
                            self.main_menu.play, 'maps/map'))
        self.ui_manager.add(UI.Button(self.main_menu.game.w / 2 - 75, self.main_menu.game.h / 2, 150, 35,
                            "Options", (150,150,150),
                            self.main_menu.options, ''))
        self.ui_manager.add(UI.Button(self.main_menu.game.w / 2 - 75, self.main_menu.game.h / 2 + 60, 150, 35,
                            "Quit", (150,150,150),
                            self.main_menu.exit, ''))

    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        pass

    def draw(self, surface):
        self.ui_manager.draw(surface)

class LevelSelectorMenu(Menu):
    def load_level_list(self):
        path = os.path.join('.', 'maps')
        if not os.path.exists(path) or not os.path.isdir(path):
            print('No folder named "maps"')
            exit(1)

        maps_names = os.listdir(path)
        maps_paths = [os.path.join('maps', map_name) for map_name in maps_names]
        return maps_names, maps_paths

    def __init__(self, main_menu):
        super().__init__(main_menu)
        self.scrollview = UI.ScrollView(0,40,1000,main_menu.game.h, (75,0,130))
        self.ui_manager.add(self.scrollview)
        self.names, self.paths = self.load_level_list()
        for i, name in enumerate(self.names):
            self.scrollview.add(UI.Button(self.main_menu.game.w / 2 - 75, 10 + 50 * i, 150, 35,
                                name, (150,150,150),
                                self.main_menu.load_map, self.paths[i]))

        self.search_bar = UI.SearchBar(main_menu.game.w / 2 - 100,10,200,30, self.update_levels)
        self.ui_manager.add(self.search_bar)
        self.update_levels("")

    def draw(self, surface):
        self.ui_manager.draw(surface)

    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        for event in events:
            if event.type == KEYDOWN:
                self.search_bar.key_pressed(event)

    def update_levels(self, search):
        self.scrollview.clear()
        total = 0
        for i, name in enumerate(self.names):
            if search in name:
                self.scrollview.add(UI.Button(self.main_menu.game.w / 2 - 75, 10 + 50 * total, 150, 35,
                                    name, (150,150,150),
                                    self.main_menu.load_map, self.paths[i]))
                total += 1
        self.scrollview.update_surface(0)

class OptionMenu(Menu):
    def __init__(self, main_menu):
        super().__init__(main_menu)
        self.fullscreen_toggle = UI.Toggle(20,20,200,32, "Fullscreen", self.toggle_fullscreen)
        self.ui_manager.add(self.fullscreen_toggle)

    def draw(self, surface):
        pygame.draw.rect(surface, (150,150,150), (10,10, self.main_menu.game.w - 20, self.main_menu.game.h - 20))
        self.ui_manager.draw(surface)

    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        pass

    def toggle_fullscreen(self, active):
        if active:
            w,h = self.main_menu.game.w, self.main_menu.game.h
            self.main_menu.game.display = pygame.display.set_mode((w,h), FULLSCREEN, HWSURFACE)
        else:
            w,h = self.main_menu.game.w, self.main_menu.game.h
            self.main_menu.game.display = pygame.display.set_mode((w,h), HWSURFACE)

class MainMenu:
    def __init__(self, game):
        self.game = game
        self.menu = MainScreenMenu(self)

    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        self.menu.ui_manager.update(mouse_position, mouse_pressed, mouse_rel, events)
        self.menu.update(mouse_position, mouse_pressed, mouse_rel, events)

    def draw(self, surface):
        surface.fill((75,0,130))

    def draw_ui(self, surface):
        self.menu.draw(surface)

    def play(self, btn, args):
        self.menu = LevelSelectorMenu(self)

    def options(self, btn, args):
        self.menu = OptionMenu(self)

    def exit(self, btn, args):
        exit(0)

    def load_map(self, btn, args):
        self.game.load_map(args)
