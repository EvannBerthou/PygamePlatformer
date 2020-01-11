import UI

class MainMenu:
    def __init__(self, game):
        self.game = game
        self.ui_manager = UI.UIManager()
        self.ui_manager.add(UI.Button(self.game.w / 2 - 75, self.game.h / 2 - 15, 150, 30,
                            "Load Map", (150,150,150),
                            self.game.load_map, 'maps/map'))

    def update(self, mouse_position, mouse_pressed, events):
        self.ui_manager.update(mouse_position, mouse_pressed, events)
        if self.ui_manager.selected != -1:
            self.ui_manager.elements[self.ui_manager.selected].update(mouse_position,mouse_pressed,events)

    def draw(self, surface):
        surface.fill((75,0,130))
