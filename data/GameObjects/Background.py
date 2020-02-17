import pygame

class Background(pygame.sprite.Sprite):
    def __init__(self, window_size):
        super().__init__()
        background_img = pygame.image.load('Resources/background.png').convert()
        self.image = pygame.transform.scale(background_img, window_size)
        self.rect = self.image.get_rect()
        self.selectable = False
        self.resizable = False

    def on_collision(self, collider):
        return

    def has_collision(self, player_id):
        return False
