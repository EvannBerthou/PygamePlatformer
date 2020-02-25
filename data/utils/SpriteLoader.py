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

def load_animation(file_name, size, number_of_sprite = 0, sprite_offset = 0):
    folder = os.path.join('Resources', 'Animations')
    path = os.path.join(folder, file_name)
    if not os.path.exists(path):
        print(f'{path} file does not exists')
        return None

    spritesheet = pygame.image.load(path).convert_alpha()
    sprites = []
    n_x = spritesheet.get_width() // size[0]
    n_y = spritesheet.get_height() // size[1]
    total_iteration = 0
    for y in range(n_y):
        for x in range(n_x):
            total_iteration += 1
            if number_of_sprite != 0 and total_iteration >= number_of_sprite + sprite_offset:
                return sprites
            if total_iteration < sprite_offset: continue
            sprite = pygame.Surface(size, pygame.SRCALPHA)
            subsurface = spritesheet.subsurface((size[0] * x, size[1] * y, *size)).convert_alpha()
            sprite.blit(subsurface, (0,0))
            sprites.append(sprite)
    return sprites
