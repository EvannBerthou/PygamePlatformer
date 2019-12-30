import pygame
import os

def load_sprite(name, size):
    path = os.path.join('Resources', name)
    if not os.path.exists(path):
        print(f'{path} file does not exists')
        return None

    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.scale(img, (int(size[0]), int(size[1])))
    return img