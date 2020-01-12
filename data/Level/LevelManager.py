import pygame
from pygame.locals import *
from data.GameObjects import *
from data.utils.SaveManager import load_map

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

    def __init__(self, window_size, map_path):
        self.player_1 = Player(K_q, K_d, K_SPACE, 0)
        self.player_2 = Player(K_LEFT, K_RIGHT, K_UP, 1)

        self.all_colliders = pygame.sprite.Group(
                Background(window_size), self.player_1, self.player_2)

        self.load_map(map_path)

        self.start_time = 0.0
        self.timer_font = pygame.font.SysFont(pygame.font.get_default_font(), 46)
        self.timer_playing = True

    def update(self, dt):
        if self.timer_playing:
            self.start_time += dt / 1000
        keyboard_input = pygame.key.get_pressed()

        self.all_colliders.update()

        #UPDATE
        self.player_1.c_update(self.all_colliders.sprites(), keyboard_input, dt)
        self.player_2.c_update(self.all_colliders.sprites(), keyboard_input, dt)

    def draw(self, surface):
        self.all_colliders.draw(surface)
        
    def draw_timer(self, surface):
        text = self.timer_font.render('{:06.2f}'.format(self.start_time), 1, (255,255,255))
        surface.blit(text, (0,0))
    
    def end_game(self):
        self.timer_playing = False