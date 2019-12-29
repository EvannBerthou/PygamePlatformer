import pygame
from pygame.locals import *
from data.GameObjects import *
from data.utils.SaveManager import load_map

class Background(pygame.sprite.Sprite):
    def __init__(self, window_size):
        super().__init__()
        background_img = pygame.image.load('Resources/background.png').convert()
        self.image = pygame.transform.scale(background_img, window_size)
        self.rect = self.image.get_rect()

    def on_collision(self, collider):
        return

    def has_collision(self, player_id):
        return False

class LevelManager:
    def load_map(self, file_path = 'map'):
        colliders = load_map(file_path)
        for col in colliders:
            if isinstance(col, Plate):
                print("plate id",col.linked_to_id)
                if col.linked_to_id != -1:
                    linked_to = colliders[col.linked_to_id]
                    col.linked_to = linked_to
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

    def __init__(self, window_size):
        self.player_1 = Player(K_q, K_d, K_SPACE, 0)
        self.player_2 = Player(K_LEFT, K_RIGHT, K_UP, 1)

        self.all_colliders = pygame.sprite.Group(
                Background(window_size), self.player_1, self.player_2)
        
        self.load_map()
    
    def update(self, tick):
        keyboard_input = pygame.key.get_pressed()

        self.all_colliders.update()

        #UPDATE
        self.player_1.c_update(self.all_colliders.sprites(), keyboard_input, tick)
        self.player_2.c_update(self.all_colliders.sprites(), keyboard_input, tick)

    def draw(self, surface):
        self.all_colliders.draw(surface)