import UI
import os
import pygame
from data.utils.ConfigManager import load_config
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
        x_pos = self.main_menu.game.DESING_W / 2 - 150
        y_center = self.main_menu.game.DESING_H / 2
        self.ui_manager.add(UI.Button(x_pos, y_center - 120, 300, 70,
                            "Load Map", (150,150,150),
                            self.main_menu.play, 'maps/map',
                            center_text = True, font_size = 64))
        self.ui_manager.add(UI.Button(x_pos, y_center, 300, 70,
                            "Options", (150,150,150),
                            self.main_menu.options, '',
                            center_text = True, font_size = 64))
        self.ui_manager.add(UI.Button(x_pos, y_center + 120, 300, 70,
                            "Quit", (150,150,150),
                            self.main_menu.exit, '',
                            center_text = True, font_size = 64))

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
        self.scrollview = UI.ScrollView(0,40,main_menu.game.DESING_W,main_menu.game.DESING_H, (75,0,130))
        self.ui_manager.add(self.scrollview)
        self.names, self.paths = self.load_level_list()
        for i, name in enumerate(self.names):
            self.scrollview.add(UI.Button(self.main_menu.game.DESING_W / 2 - 75, 20 + 50 * i, 300, 70,
                                name, (150,150,150),
                                self.main_menu.load_map, self.paths[i]))

        self.search_bar = UI.SearchBar(main_menu.game.DESING_W / 2 - 200,10,400,60, self.update_levels)
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
                self.scrollview.add(UI.Button(self.main_menu.game.DESING_W / 2 - 150, 50 + 75 * total, 300, 70,
                                    name, (150,150,150),
                                    self.main_menu.load_map, self.paths[i],
                                    center_text = True, font_size = 64))
                total += 1
        self.scrollview.update_surface(0)

class OptionMenu(Menu):
    def __init__(self, main_menu):
        super().__init__(main_menu)
        self.fullscreen_toggle = UI.Toggle(20,20,400,64, "Fullscreen", self.toggle_fullscreen)
        self.ui_manager.add(self.fullscreen_toggle)

        self.resolution_dropdown = UI.DropDown(20,100,400,60,
                                                ["1920x1080", "1366x768", "1280x720", "1152x664", "960x540","640x360"],
                                                (100,100,100), (75,75,75), self.change_resolution)

        self.ui_manager.add(self.resolution_dropdown)

        self.ui_manager.add(UI.Button(main_menu.game.DESING_W - 250, main_menu.game.DESING_H - 100, 200,60,
                                        "Back", (200,200,200), main_menu.main_menu, [],
                                        center_text = True, font_size = 70))

        self.fullscreen_toggle.activated = main_menu.game.config['fullscreen'] == 1
        self.fullscreen_toggle.update_surface()
        self.resolution_dropdown.set_choice(None, "{}x{}".format(main_menu.game.w, main_menu.game.h))

    def draw(self, surface):
        pygame.draw.rect(surface, (150,150,150),
                        (10,10, self.main_menu.game.DESING_W - 20, self.main_menu.game.DESING_H - 20))
        self.ui_manager.draw(surface)

    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        pass

    def toggle_fullscreen(self, active):
        self.main_menu.game.fullscreen = active
        if active:
            w,h = self.main_menu.game.w, self.main_menu.game.h
            self.main_menu.game.display = pygame.display.set_mode((w,h), FULLSCREEN, HWSURFACE)
        else:
            w,h = self.main_menu.game.w, self.main_menu.game.h
            self.main_menu.game.display = pygame.display.set_mode((w,h), HWSURFACE)

    def change_resolution(self, resolution):
        parts = resolution.split('x')
        w,h = int(parts[0]), int(parts[1])
        self.main_menu.game.update_screen_size((w,h))
        fullscreen = FULLSCREEN if self.main_menu.game.fullscreen else 0
        self.main_menu.game.display = pygame.display.set_mode((w,h), fullscreen, HWSURFACE)
        self.main_menu.game.win.fill((0,0,0))

class MainMenu:
    def __init__(self, game):
        self.game = game
        self.menu = MainScreenMenu(self)

    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        self.menu.ui_manager.update(mouse_position, mouse_pressed, mouse_rel, events)
        self.menu.update(mouse_position, mouse_pressed, mouse_rel, events)

    def main_menu(self, *args):
        self.game.save_config()
        self.menu = MainScreenMenu(self)

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
