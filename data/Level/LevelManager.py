import pygame
from pygame.locals import *
from data.GameObjects import *
from data.utils.SaveManager import load_map
import UI

pygame.font.init()

class LevelManager:
    def load_map(self, file_path):
        colliders = load_map(file_path)
        for col in colliders:
            if isinstance(col, Plate):
                print("plate id",col.linked_to_id)
                if col.linked_to_id != -1:
                    linked_to = colliders[col.linked_to_id]
                    col.linked_to = linked_to
            if isinstance(col, EndGoal):
                col.level_manager = self
            if isinstance(col, SpawnPoint):
                player = col.player_id
                if player == 0:
                    self.player_1.set_position(col.get_position())
                elif player == 1:
                    self.player_2.set_position(col.get_position())
                else:
                    raise ValueError("Spawn point's Player_id is not valid")
            else:
                self.all_colliders.add(col)

    def __init__(self, window_size, map_path, game):
        self.player_1 = Player(K_q, K_d, K_SPACE, 0)
        self.player_2 = Player(K_LEFT, K_RIGHT, K_UP, 1)

        self.all_colliders = pygame.sprite.Group(
                Background(window_size), self.player_1, self.player_2)

        self.map_path = map_path
        self.load_map(map_path)

        self.start_time = 0.0
        self.timer_font = pygame.font.SysFont(pygame.font.get_default_font(), 46)
        self.level_completed = False

        self.ui_manager = UI.UIManager()
        self.end_screen = pygame.Surface(window_size, SRCALPHA)
        self.game = game

    def update(self, dt):
        if self.level_completed:
            return

        self.start_time += dt / 1000
        keyboard_input = pygame.key.get_pressed()

        self.all_colliders.update()

        #UPDATE
        self.player_1.c_update(self.all_colliders.sprites(), keyboard_input, dt)
        self.player_2.c_update(self.all_colliders.sprites(), keyboard_input, dt)

    def draw(self, surface):
        self.all_colliders.draw(surface)
        if self.level_completed:
            surface.blit(self.end_screen, (0,0))

    def draw_ui(self, surface):
        if not self.level_completed:
            text = self.timer_font.render('{:06.2f}'.format(self.start_time), 1, (255,255,255))
            surface.blit(text, (0,0))

        if self.level_completed:
            self.ui_manager.draw(surface)

    def end_game(self):
        self.level_completed = True
        self.end_screen.fill((75,0,130,200))
        font = pygame.font.SysFont(pygame.font.get_default_font(), 150)
        level_completed_text = font.render("Level Completed !", 1, (255,255,255))
        x_pos = self.end_screen.get_width() / 2 - level_completed_text.get_width() / 2
        self.end_screen.blit(level_completed_text, (x_pos, 50))
        timer_text = font.render('{:06.2f}'.format(self.start_time), 1, (255,255,255))
        x_pos = self.end_screen.get_width() / 2 - timer_text.get_width() / 2
        self.end_screen.blit(timer_text, (x_pos, 300))

        button_y_pos = self.game.h / 2 + 50
        w_center = self.game.w / 2
        reload_button = UI.Button(w_center - 300, button_y_pos, 200,40,
                                    "Replay", (150,150,150), self.reload_level, [])

        main_menu_button = UI.Button(w_center + 50, button_y_pos, 200,40,
                                    "Main Menu", (150,150,150), self.game.load_main_menu, [])

        self.ui_manager.add(reload_button)
        self.ui_manager.add(main_menu_button)

    def reload_level(self, btn, args):
        self.load_map(self.map_path)
        self.start_time = 0.0
        self.level_completed = False
        self.ui_manager.clear()
