import pygame
from pygame.locals import *

from ..utils.utils import clamp
from ..utils.SpriteLoader import load_animation


class Player(pygame.sprite.Sprite):
    def __init__(self, left_key, right_key, jump_key, player_id, rect):
        super().__init__()
        self.rect = rect
        self.size = self.rect.w
        self.grounded = False
        self.mvt = [0, 0]
        self.vertical_speed = 0
        self.speed = self.size / 100
        self.gravity = 0.0035
        self.jump_force = self.size / 55

        self.left_key = left_key
        self.right_key = right_key
        self.jump_key = jump_key

        self.player_id = player_id
        self.image = pygame.Surface((self.size, self.size), SRCALPHA)

        self.prev_colliders = []

        self.animations = {
            "walking": load_animation('walker1.png', (64, 64), (self.size, self.size), 16, 33)
            # "idle": load_animation(f'player_{self.player_id}_idle.png', (self.size, self.size)),
            # "walking": load_animation(f'player_{self.player_id}_walking.png', (self.size, self.size), 9, 27),
            # "standing": load_animation(f'player_{self.player_id}_standing.png', (self.size, self.size))
        }

        # Looking direction :
        # 0 : left
        # 1 : right
        self.looking_direction = 1

        self.animation_lenght = 1000  # duration of the animation in ms
        self.animation_time = 0  # time since the start of the animation in ms
        self.update_animation(0)

    def collision_test(self, colliders):
        collisions = []
        for col in colliders:
            if self.rect.colliderect(col):
                collisions.append(col)
        return collisions

    def x_collisions(self, colliders):
        collisions = self.collision_test(colliders)
        for col in collisions:
            if col == self:
                continue
            if not col.has_collision(self.player_id):
                continue

            if self.mvt[0] > 0:
                self.rect.right = col.rect.left
            if self.mvt[0] < 0:
                self.rect.left = col.rect.right

    def y_collisions(self, colliders):
        collided_with = 0
        collisions = self.collision_test(colliders)
        set_grounded = False
        for col in collisions:
            if col == self:
                continue
            if not col.has_collision(self.player_id):
                continue
            collided_with += 1
            if self.mvt[1] > 0:
                self.rect.bottom = col.rect.top
                self.vertical_speed = 0
            if self.mvt[1] < 0:
                self.vertical_speed = 0
                self.rect.top = col.rect.bottom
                set_grounded = True

        self.grounded = collided_with != 0
        if set_grounded:
            self.grounded = False

    def move(self, colliders, dt):
        self.rect.x += self.mvt[0] * dt
        self.x_collisions(colliders)

        self.rect.y += self.mvt[1] * dt
        self.y_collisions(colliders)

        self.rect.x = clamp(self.rect.x, 0, 1920 - self.size)

    def update_animation(self, dt):
        self.image.fill((0, 0, 0, 0))
        self.animation_time = (self.animation_time +
                               dt) % self.animation_lenght
        animation_frame = self.animation_time * \
            len(self.animations['walking']) // self.animation_lenght
        frame_to_blit = self.animations['walking'][animation_frame]
        if self.looking_direction == 0:
            flipped_image = pygame.transform.flip(frame_to_blit, True, False)
            self.image.blit(flipped_image, (0, 0))
        if self.looking_direction == 1:
            self.image.blit(frame_to_blit, (0, 0))

    def c_update(self, colliders, keys, dt):
        self.mvt = [0, 0]
        self.mvt[1] = self.vertical_speed

        if not self.grounded:
            self.vertical_speed += self.gravity * dt

        if keys and keys[self.jump_key] and self.grounded:
            self.vertical_speed = -self.jump_force
            self.grounded = False

        self.update_animation(dt)
        if keys:
            self.mvt[0] = (keys[self.right_key] -
                           keys[self.left_key]) * self.speed
            if self.mvt[0] > 0:
                self.looking_direction = 1
            if self.mvt[0] < 0:
                self.looking_direction = 0
            self.move(colliders, dt)

        collisions = self.collision_test(colliders)
        # Detect when the player is no longuer in collision with an object
        for col in self.prev_colliders.copy():
            if col not in collisions:  # si le joueur n'a plus de collision avec un objet qu'il touchait avant
                col.on_collision_exit(self)
                self.prev_colliders.remove(col)

        # Detect when the player enters in collisions for the first time
        for col in collisions:
            if col not in self.prev_colliders:
                self.prev_colliders.append(col)
                col.on_collision(self)

    def has_collision(self, player_id):
        return True

    def on_collision(self, collider):
        return

    def on_collision_exit(self, collider):
        return

    def set_position(self, position):
        self.rect = pygame.Rect(*position, self.size, self.size)
