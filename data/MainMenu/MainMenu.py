import UI
import os
import pygame
from data.utils.ConfigManager import load_config
from data.utils.SpriteLoader import load_sprite
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
        self.ui_manager.add(UI.Button(x_pos, y_center - 150, 300, 70,
                            "Load Map", (150,150,150),
                            self.main_menu.play, 'maps/map',
                            center_text = True, font_size = 64))
        self.ui_manager.add(UI.Button(x_pos, y_center - 50, 300, 70,
                            "Editor", (150,150,150),
                            self.main_menu.start_editor, '',
                            center_text = True, font_size = 64))
        self.ui_manager.add(UI.Button(x_pos, y_center + 50, 300, 70,
                            "Options", (150,150,150),
                            self.main_menu.options, '',
                            center_text = True, font_size = 64))
        self.ui_manager.add(UI.Button(x_pos, y_center + 150, 300, 70,
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
            quit(1)

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
                                    True, 46])
                total += 1
        self.scrollview.update_surface(0)

class OptionMenu(Menu):
    def set_keybind(self, btn, key):
        self.waiting_for_key = True
        self.keybind = key[0]
        self.btn = btn

    def key_to_char(self, key):
        specials = {
            K_SPACE: "Space",
            K_RIGHT: "Right",
            K_LEFT: "Left",
            K_DOWN: "Down",
            K_UP: "Up",
            K_TAB: "Tab",
            K_DELETE: "Delete",
            K_F1: "F1",
            K_F2: "F2",
            K_F3: "F3",
            K_F4: "F4",
            K_F5: "F5",
            K_F6: "F6",
            K_F7: "F7",
            K_F8: "F8",
            K_F9: "F9",
            K_F10: "F10",
            K_F11: "F11",
            K_F12: "F12",
        }
        if key in specials:
            return specials[key]
        if key < 0 or key > 0x10FFFF:
            print('Key out of chr range')
            return None

        return chr(key)

    def __init__(self, main_menu):
        super().__init__(main_menu)
        self.fullscreen_toggle = UI.Toggle(20,20,400,64, "Fullscreen", self.toggle_fullscreen)
        self.ui_manager.add(self.fullscreen_toggle)

        self.resolution_dropdown = UI.DropDown(20,100,400,60,
                                                ["1920x1080", "1366x768", "1280x720", "1152x664", "960x540","640x360"],
                                                (100,100,100), (75,75,75), self.change_resolution)

        self.ui_manager.add(self.resolution_dropdown)

        self.fps_counter_toggle = UI.Toggle(20, 180, 400,64, "FPS Counter", self.toggle_fps)
        self.ui_manager.add(self.fps_counter_toggle)


        self.ui_manager.add(UI.Button(main_menu.game.DESING_W - 250, main_menu.game.DESING_H - 100, 200,60,
                                        "Back", (200,200,200), main_menu.main_menu, [],
                                        center_text = True, font_size = 70))

        p1_text = UI.Text(720, 20, "Player 1", 56, (255,255,255))
        p2_text = UI.Text(930, 20, "Player 2", 56, (255,255,255))
        left_text = UI.Text(520, 95, "Left", 56, (255,255,255))
        right_text = UI.Text(520, 175, "Right", 56, (255,255,255))
        jump_text = UI.Text(520, 255, "Jump", 56, (255,255,255))
        self.ui_manager.add(p1_text)
        self.ui_manager.add(p2_text)
        self.ui_manager.add(left_text)
        self.ui_manager.add(right_text)
        self.ui_manager.add(jump_text)

        keybind_grid = UI.Grid(675,70,600,300,200,60,20,20)
        cfg = main_menu.game.config
        keybind_grid.add(UI.Button, [self.key_to_char(cfg['p1_left']), (200,200,200), self.set_keybind, ['p1_left'], True])
        keybind_grid.add(UI.Button, [self.key_to_char(cfg["p2_left"]), (200,200,200), self.set_keybind, ['p2_left'], True])
        keybind_grid.add(UI.Button, [self.key_to_char(cfg["p1_right"]), (200,200,200), self.set_keybind, ['p1_right'], True])
        keybind_grid.add(UI.Button, [self.key_to_char(cfg["p2_right"]), (200,200,200), self.set_keybind, ['p2_right'], True])
        keybind_grid.add(UI.Button, [self.key_to_char(cfg["p1_jump"]), (200,200,200), self.set_keybind, ['p1_jump'], True])
        keybind_grid.add(UI.Button, [self.key_to_char(cfg["p2_jump"]), (200,200,200), self.set_keybind, ['p2_jump'], True])
        self.ui_manager.add(keybind_grid)

        editor_grid = UI.Grid(1200,70,600,900,200,60,20,20)
        editor_grid.add(UI.Text, ["Mode", 56, (255,255,255)])
        editor_grid.add(UI.Button, [self.key_to_char(cfg['ed_mode']), (200,200,200), self.set_keybind, ['ed_mode'], True])
        editor_grid.add(UI.Text, ["Panel", 56, (255,255,255)])
        editor_grid.add(UI.Button, [self.key_to_char(cfg['ed_clear']), (200,200,200), self.set_keybind, ['ed_clear'], True])
        editor_grid.add(UI.Text, ["Reload", 56, (255,255,255)])
        editor_grid.add(UI.Button, [self.key_to_char(cfg['ed_reload']), (200,200,200), self.set_keybind, ['ed_reload'], True])
        editor_grid.add(UI.Text, ["Camera reset", 46, (255,255,255)])
        editor_grid.add(UI.Button, [self.key_to_char(cfg['ed_camera_reset']), (200,200,200), self.set_keybind, ['ed_camera_reset'], True])
        editor_grid.add(UI.Text, ["Delete", 46, (255,255,255)])
        editor_grid.add(UI.Button, [self.key_to_char(cfg['ed_delete']), (200,200,200), self.set_keybind, ['ed_delete'], True])
        editor_grid.add(UI.Text, ["Wall", 46, (255,255,255)])
        editor_grid.add(UI.Button, [self.key_to_char(cfg['ed_wall']), (200,200,200), self.set_keybind, ['ed_wall'], True])
        editor_grid.add(UI.Text, ["Door", 46, (255,255,255)])
        editor_grid.add(UI.Button, [self.key_to_char(cfg['ed_door']), (200,200,200), self.set_keybind, ['ed_door'], True])
        editor_grid.add(UI.Text, ["Spawn", 46, (255,255,255)])
        editor_grid.add(UI.Button, [self.key_to_char(cfg['ed_spawn']), (200,200,200), self.set_keybind, ['ed_spawn'], True])
        editor_grid.add(UI.Text, ["Plate", 46, (255,255,255)])
        editor_grid.add(UI.Button, [self.key_to_char(cfg['ed_plate']), (200,200,200), self.set_keybind, ['ed_plate'], True])
        editor_grid.add(UI.Text, ["Goal", 46, (255,255,255)])
        editor_grid.add(UI.Button, [self.key_to_char(cfg['ed_goal']), (200,200,200), self.set_keybind, ['ed_goal'], True])
        self.ui_manager.add(editor_grid)

        self.fullscreen_toggle.activated = main_menu.game.config['fullscreen'] == 1
        self.fps_counter_toggle.activated = main_menu.game.config['fps_counter']
        self.fps_counter_toggle.update_surface()
        self.fullscreen_toggle.update_surface()
        self.resolution_dropdown.set_choice(None, "{}x{}".format(main_menu.game.w, main_menu.game.h))

        self.waiting_for_key = False
        self.keybind = None
        self.btn = None

    def draw(self, surface):
        pygame.draw.rect(surface, (150,150,150),
                        (10,10, self.main_menu.game.DESING_W - 20, self.main_menu.game.DESING_H - 20))
        self.ui_manager.draw(surface)

    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        if self.waiting_for_key:
            for event in events:
                if event.type == KEYDOWN:
                    key = self.key_to_char(event.key)
                    self.main_menu.game.config[self.keybind] = event.key
                    self.waiting_for_key = False
                    self.btn.set_text(key)
 
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

    def toggle_fps(self, active):
        self.main_menu.game.show_fps = active

class MainMenu:
    def __init__(self, game):
        self.game = game
        self.menu = MainScreenMenu(self)
        self.background = load_sprite('background.png', (1920,1080))

    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        self.menu.ui_manager.update(mouse_position, mouse_pressed, mouse_rel, events)
        self.menu.update(mouse_position, mouse_pressed, mouse_rel, events)

    def main_menu(self, *args):
        self.game.save_config()
        self.menu = MainScreenMenu(self)

    def draw(self, surface):
        surface.blit(self.background, (0,0))

    def draw_ui(self, surface):
        self.menu.draw(surface)

    def play(self, btn, args):
        self.menu = LevelSelectorMenu(self)

    def options(self, btn, args):
        self.menu = OptionMenu(self)

    def exit(self, btn, args):
        quit(0)

    def load_map(self, btn, args):
        self.game.load_map(args)
    
    def start_editor(self, btn, args):
        self.game.start_editor()
