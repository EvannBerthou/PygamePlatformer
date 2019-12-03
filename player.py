import pygame
from pygame.locals import *

PLAYER_SIZE = 64

class Player:
    def __init__(self, left_key, right_key, jump_key, player_id):
        self.rect = pygame.Rect(400,375, PLAYER_SIZE, PLAYER_SIZE)
        self.grounded = True
        self.mvt = [0,0]
        self.speed = 0.5
        self.gravity = 0.5
        self.jump_force = 1

        self.left_key  = left_key
        self.right_key = right_key
        self.jump_key  = jump_key

        self.player_id = player_id
        self.color = (255,0,0) if self.player_id == 1 else (0,0,255)

    def draw(self, game):
        pygame.draw.rect(game.blitting_surface, self.color, self.rect)

    def move(self):
        self.rect.x += self.mvt[0]
        self.rect.y += self.mvt[1]

    def update(self, colliders, keys, dt):
        self.move()
        self.mvt[0] = (keys[self.right_key] - keys[self.left_key]) * dt * self.speed
        collisions = self.rect.collidelistall(colliders)
        dx = 0
        dy = 0
        if collisions:
            for i in collisions:
                col = colliders[i]
                #If the collider is traversable don't check collisions
                if not col.has_collision(self.player_id):
                    continue
                rect = col.rect
                #Collision en dessous du joueur
                if self.collision_bottom(rect):
                    dy -= (self.rect.bottom - rect.top) #Correction pour éviter que le joueur traverse le sol
                    self.grounded = True
                    self.mvt[1] = 0
                elif self.collision_top(rect) and rect.w > self.rect.w:
                    dy -= (self.rect.top - rect.bottom) #Correction pour éviter que le joueur traverse le sol
                    self.grounded = False
                    self.mvt[1] = 0
                elif self.collision_right(rect):
                    self.mvt[0] = 0
                    dx -= (self.rect.right - rect.left)
                elif self.collision_left(rect) and not self.collision_top(rect):
                    self.mvt[0] = 0
                    dx -= (self.rect.left - rect.right)
        else:
            self.grounded = False

        self.rect.x += dx
        self.rect.y += dy

        if not self.grounded:
            self.mvt[1] += float(dt / 10) * self.gravity

        if keys[self.jump_key] and self.grounded:
            self.mvt[1] -= self.jump_force * dt
            self.grounded = False

    def collision_bottom(self, col):
        bl = col.collidepoint(self.rect.bottomleft)
        bm = col.collidepoint(self.rect.midbottom)
        br = col.collidepoint(self.rect.bottomright)
        ml = col.collidepoint(self.rect.midleft)
        mr = col.collidepoint(self.rect.midright)
        return (bl or br or bm) and not ml and not mr

    def collision_top(self, col):
        tl = col.collidepoint(self.rect.topleft)
        tm = col.collidepoint(self.rect.midtop)
        tr = col.collidepoint(self.rect.topright)
        ml = col.collidepoint(self.rect.midleft)
        mr = col.collidepoint(self.rect.midright)
        return (tl or tr or tm) and not ml and not mr


    def collision_left(self, col):
        t = col.collidepoint(self.rect.topleft)
        m = col.collidepoint(self.rect.midleft)
        b = col.collidepoint(self.rect.bottomleft)
        return t or m or b

    def collision_right(self, col):
        t = col.collidepoint(self.rect.topright)
        m = col.collidepoint(self.rect.midright)
        b = col.collidepoint(self.rect.bottomright)
        return t or m or b

    def has_collision(self, player_id):
        return True

    def set_position(self, position):
        self.rect.center = position
