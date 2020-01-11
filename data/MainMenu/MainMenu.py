import UI

class MainMenu:
    def __init__(self, game):
        self.game = game
        self.ui_manager = UI.UIManager()
        self.ui_manager.add(UI.Button(self.game.w / 2 - 75, self.game.h / 2 - 60, 150, 35,
                            "Load Map", (150,150,150),
                            self.play, 'maps/map'))
        self.ui_manager.add(UI.Button(self.game.w / 2 - 75, self.game.h / 2, 150, 35,
                            "Options", (150,150,150),
                            self.options, ''))
        self.ui_manager.add(UI.Button(self.game.w / 2 - 75, self.game.h / 2 + 60, 150, 35,
                            "Quit", (150,150,150),
                            self.exit, ''))

    def update(self, mouse_position, mouse_pressed, events):
        self.ui_manager.update(mouse_position, mouse_pressed, events)
        if self.ui_manager.selected != -1:
            self.ui_manager.elements[self.ui_manager.selected].update(mouse_position,mouse_pressed,events)

    def draw(self, surface):
        surface.fill((75,0,130))

    def play(self, btn, args):
        self.game.load_map(args)

    def options(self, btn, args):
        print('Options')

    def exit(self, btn, args):
        exit(0)
