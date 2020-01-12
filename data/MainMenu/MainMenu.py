import UI
import os

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
        self.scrollview = UI.ScrollView(0,0,1000,1000, (75,0,130))
        self.ui_manager.add(self.scrollview)
        names, paths = self.load_level_list()
        for i, name in enumerate(names):
            self.scrollview.add(UI.Button(self.main_menu.game.w / 2 - 75, 10 + 50 * i, 150, 35,
                                name, (150,150,150),
                                self.main_menu.load_map, paths[i]))

    def draw(self, surface):
        self.ui_manager.draw(surface)

class MainMenu:
    def __init__(self, game):
        self.game = game
        self.menu = MainScreenMenu(self)

    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        self.menu.ui_manager.update(mouse_position, mouse_pressed, mouse_rel, events)
        if self.menu.ui_manager.selected != -1:
            self.menu.ui_manager.elements[self.menu.ui_manager.selected].update(mouse_position,mouse_pressed,mouse_rel,events)

    def draw(self, surface):
        surface.fill((75,0,130))

    def draw_ui(self, surface):
        self.menu.draw(surface)

    def play(self, btn, args):
        self.menu = LevelSelectorMenu(self)

    def options(self, btn, args):
        print('Options')

    def exit(self, btn, args):
        exit(0)

    def load_map(self, btn, args):
        self.game.load_map(args)