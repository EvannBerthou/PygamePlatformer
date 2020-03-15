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
    def __init__(self, main_menu):
        super().__init__(main_menu)
        self.category_selector_ui = UI.UIManager()
        self.category_selector_ui.add(UI.Button(self.main_menu.game.DESING_W / 2 - 450,
                                                self.main_menu.game.DESING_H / 2 - 200,
                                                400,400,
                                                "Official", (150,150,150),
                                                self.open_categorie, "official"))

        self.category_selector_ui.add(UI.Button(self.main_menu.game.DESING_W / 2,
                                                self.main_menu.game.DESING_H / 2 - 200,
                                                400,400,
                                                "Community", (150,150,150),
                                                self.open_categorie, "community"))

        BUTTON_WIDTH = 800
        BUTTON_HEIGHT = 100
        self.scrollview = UI.ScrollView(
                                        0, 0,
                                        main_menu.game.DESING_W,main_menu.game.DESING_H, (75,0,130),
                                        BUTTON_WIDTH, BUTTON_HEIGHT,
                                        main_menu.game.DESING_W / 2 - BUTTON_WIDTH / 2, 25)
        self.LevelSelectorUI = UI.UIManager()
        self.LevelSelectorUI.add(self.scrollview)

        self.search_bar = UI.InputField(10,10,400,60, self.update_levels, 'search_icon.png')
        self.LevelSelectorUI.add(self.search_bar)
        self.ui_manager = self.category_selector_ui

    def open_categorie(self, btn, categorie):
        self.ui_manager = self.LevelSelectorUI

        folder = 'maps' if categorie == 'official' else 'custom_maps'
        self.infos, self.paths = self.load_level_list(folder)
        self.update_levels('')

    def load_level_list(self, folder):
        path = os.path.join('.', folder)
        if not os.path.exists(path) or not os.path.isdir(path):
            print(f'No folder named {folder}')
            exit(1)

        maps_names = os.listdir(path)
        maps_paths = [os.path.join(folder, map_name) for map_name in maps_names]
        maps_infos  = [self.extract_map_infos(file) for file in maps_paths]
        return maps_infos, maps_paths

    def extract_map_infos(self, file):
        infos = {}
        with open(file, 'r') as f:
            for line in f:
                if line.startswith('name'):
                    infos['name'] = line.split(':')[1].strip()
                if line.startswith('author'):
                    infos['author'] = line.split(':')[1].strip()
        return infos

    def draw(self, surface):
        self.ui_manager.draw(surface)

    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        for event in events:
            if event.type == KEYDOWN and self.ui_manager == self.LevelSelectorUI:
                self.search_bar.key_pressed(event)
                if event.key == K_ESCAPE:
                    if self.ui_manager == self.LevelSelectorUI: self.ui_manager = self.category_selector_ui
                    else: self.main_menu.main_menu()


    def update_levels(self, search):
        self.scrollview.clear()
        total = 0
        for i, infos in enumerate(self.infos):
            if search in infos['name']:
                self.scrollview.add(UI.LevelButton,
                                    [infos['name'], infos['author'], (150,150,150),
                                    self.main_menu.load_map, self.paths[i],
                                    True, 64])
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
