import pygame
from pygame.locals import *
from data.GameObjects import *
from data.utils.SaveManager import load_map
import UI
import json
import os
from .ReplayManager import ReplayManager

pygame.font.init()

class LevelState:
    DIALOGUE = 0
    IN_GAME = 1

class LevelManager:
    def load_map(self, file_path):
        colliders_list = []
        p1_pos = (0,0)
        p2_pos = (0,0)
        map_data = load_map(file_path)
        colliders = map_data['rects']
        for col in colliders:
            if isinstance(col, Plate):
                if col.linked_to_id != -1:
                    linked_to = colliders[col.linked_to_id - 1]
                    col.linked_to = linked_to
            if isinstance(col, EndGoal):
                col.level_manager = self
            if isinstance(col, SpawnPoint):
                player = col.player_id
                if player == 0:
                    p1_pos = col.get_position()
                elif player == 1:
                    p2_pos = col.get_position()
                else:
                    raise ValueError("Spawn point's Player_id is not valid")
            else:
                colliders_list.append(col)
        return map_data, colliders_list, p1_pos, p2_pos

    def __init__(self, window_size, map_path, game, replay = None):

        self.background = Background(window_size)

        self.map_path = map_path
        map_data, colliders, p1_pos, p2_pos = self.load_map(map_path)
        size = (map_data['player_size'], map_data['player_size'])

        self.player_1 = Player(game.config['p1_left'], game.config['p1_right'], game.config['p1_jump'],
                               0, pygame.Rect(*p2_pos, *size))
        self.player_2 = Player(game.config['p2_left'], game.config['p2_right'], game.config['p2_jump'], 
                               1, pygame.Rect(*p2_pos, *size))

        self.all_colliders = pygame.sprite.Group()
        self.all_colliders.add([self.background, self.player_1, self.player_2])
        self.all_colliders.add(colliders)

        self.dialogues = map_data['dialogues']
        self.level_state = LevelState.DIALOGUE if len(self.dialogues) > 0 else LevelState.IN_GAME
        self.dialogues_index = -1

        self.start_time = 0.0
        self.timer_font = pygame.font.SysFont(pygame.font.get_default_font(), 46)
        self.level_completed = False

        self.ui_manager = UI.UIManager()
        self.dialogue_ui = UI.UIManager()
        self.end_screen = pygame.Surface(window_size, SRCALPHA)
        self.game = game

        self.players_positions = {}
        self.replay = replay
        if self.replay:
            self.replay_manager = ReplayManager('test.json')

        self.line_index = -1
        self.dialogues_background = UI.Image(0, game.DESING_H - 300, game.DESING_W, 300, color = (150,150,150))
        self.dialogues_text = UI.Text(5,game.DESING_H - 280, "", 70, (255,255,255))
        self.text_timer = 0
        self.next_timer = 0
        self.line = self.next_dialogue()

        self.dialogue_ui.add(self.dialogues_background)
        self.dialogue_ui.add(self.dialogues_text)

    def update(self, dt):
        if self.level_completed:
            return
        if self.level_state == LevelState.DIALOGUE:
            if not self.line:
                self.level_state = LevelState.IN_GAME
                return

            self.text_timer += dt
            if self.text_timer >= self.next_timer:
                self.next_timer += 64
                self.line_index += 1
                self.dialogues_text.set_text(self.line[:self.line_index])
                if self.line_index > len(self.line):
                    self.line = self.next_dialogue()
            return

        self.start_time += dt / 1000
        keyboard_input = pygame.key.get_pressed()

        self.all_colliders.update()

        #UPDATE
        if self.replay:
            positions = self.replay_manager.get_action([self.player_1, self.player_2])
            self.replay_position(self.player_1, positions[0])
            self.replay_position(self.player_2, positions[1])
            self.player_1.c_update(self.all_colliders.sprites(), None, dt)
            self.player_2.c_update(self.all_colliders.sprites(), None, dt)
            self.player_1.update_animation(dt)
            self.player_2.update_animation(dt)
        else:
            self.player_1.c_update(self.all_colliders.sprites(), keyboard_input, dt)
            self.player_2.c_update(self.all_colliders.sprites(), keyboard_input, dt)
            self.record_position()

    def record_position(self):
        self.players_positions[len(self.players_positions)] = [
                [self.player_1.rect.x, self.player_1.rect.y],
                [self.player_2.rect.x, self.player_2.rect.y]]

    def replay_position(self, player, positions):
        player.rect.x = positions[0]
        player.rect.y = positions[1]

    def draw(self, surface):
        self.all_colliders.draw(surface)

        if self.level_state == LevelState.DIALOGUE:
            self.dialogue_ui.draw(surface)
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

        #Texts
        font = pygame.font.SysFont(pygame.font.get_default_font(), 150)

        level_completed_text = font.render("Level Completed !", 1, (255,255,255))
        x_pos = self.end_screen.get_width() / 2 - level_completed_text.get_width() / 2
        self.end_screen.blit(level_completed_text, (x_pos, 50))

        timer_text = font.render('{:06.2f}'.format(self.start_time), 1, (255,255,255))
        x_pos = self.end_screen.get_width() / 2 - timer_text.get_width() / 2
        self.end_screen.blit(timer_text, (x_pos, 300))

        #Buttons
        button_y_pos = self.game.DESING_H / 2 + 50
        w_center = self.game.DESING_W / 2
        reload_button = UI.Button(w_center - 650, button_y_pos, 400,80,
                                  "Restart", (150,150,150), self.reload_level, [], center_text = True)

        save_replay_button = UI.Button(w_center - 200, button_y_pos, 400,80,
                                      "Save Replay", (150,150,150), self.save_replay, [], center_text = True)

        main_menu_button = UI.Button(w_center + 250, button_y_pos, 400,80,
                                    "Main Menu", (150,150,150), self.game.load_main_menu, [], center_text = True)

        self.ui_manager.add(reload_button)
        self.ui_manager.add(main_menu_button)
        self.ui_manager.add(save_replay_button)

        #saves recorded actions
        with open('test.json', 'w') as f:
            f.write(json.dumps(self.players_positions))

    def save_replay(self, btn, args):
        file_name = os.path.basename(self.map_path) + '.json'
        print(file_name)
        with open(file_name, 'w') as f:
            f.write(json.dumps(self.players_positions))

    def reload_level(self, btn, args):
        self.start_time = 0.0
        self.level_completed = False
        self.ui_manager.clear()
        self.all_colliders.empty()
        self.player_1.prev_colliders.clear()
        self.player_2.prev_colliders.clear()
        self.load_map(self.map_path)

    def next_dialogue(self):
        if self.level_state != LevelState.DIALOGUE:
            return
        if self.dialogues_index >= len(self.dialogues) - 1:
            return None
        self.line_index = -1
        self.dialogues_index += 1
        dialogue = self.dialogues[self.dialogues_index]
        player = dialogue[0]
        if player == "p1":
            self.dialogues_text.color = (0,0,255)
        if player == "p2":
            self.dialogues_text.color = (255,0,0)
        text = dialogue[1]
        return text
