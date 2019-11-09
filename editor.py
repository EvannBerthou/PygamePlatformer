import pygame
from pygame.locals import *

DESING_W, DESING_H = 1920,1080

pygame.font.init()

MODE_TEXT = pygame.font.SysFont("Arial Black", 46)

class Camera:
    def __init__(self, ws):
        self.x = 0
        self.y = 0
        self.zoom = 1

        self.mouse_moving = 0

        self.ratio = (DESING_W / ws[0], DESING_H / ws[1])

    def draw_rect(self, surface, color, rect, size=0):
        pos = ((self.x + rect[0]) * self.zoom, (self.y + rect[1]) * self.zoom)
        scl = (self.zoom * rect[2], self.zoom * rect[3])
        pygame.draw.rect(surface, color, (*pos, *scl), size)

    def event_zoom(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 4:
                self.zoom += 0.05
            if event.button == 5:
                self.zoom -= 0.05

                self.zoom = max(0.1, self.zoom)
                self.zoom = min(2, self.zoom)

            if event.button == 1:
                self.mouse_moving = 1
                pygame.mouse.get_rel()

        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.mouse_moving = 0

    def screen_to_world(self, pos):
        return (((pos[0] * self.ratio[0] / self.zoom) - self.x),
                ((pos[1] * self.ratio[1] / self.zoom) - self.y))

class MODE:
    Camera = 0
    Editor = 1

class Game:
    def __init__(self):
        self.w, self.h = 1152,648
        # self.w, self.h = 1920,1080
        self.win = pygame.display.set_mode((self.w,self.h))
        self.blitting_surface = pygame.Surface((DESING_W,DESING_H))
        self.running = True

        self.clock = pygame.time.Clock()

        self.mouse_moving = 0

        self.camera = Camera((self.w,self.h))

        self.mode_text = None
        self.mode = MODE.Camera
        self.update_mode()

        self.rect_start = None
        self.rect_started = False

        self.rects = []

    def run(self):
        while self.running:
            tick = self.clock.tick(60)

            mouse_position = pygame.mouse.get_pos()

            self.win.fill((0,0,0,))
            self.blitting_surface.fill((0,0,0))

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                if event.type == MOUSEBUTTONDOWN:
                    if self.mode == MODE.Camera:
                        self.camera.event_zoom(event)
                    if self.mode == MODE.Editor:
                        self.rect_started = True
                        self.rect_start = self.camera.screen_to_world(mouse_position)

                if event.type == MOUSEBUTTONUP:
                    if self.mode == MODE.Camera:
                        self.camera.event_zoom(event)
                    if self.mode == MODE.Editor:
                        if self.rect_started:
                            self.create_rect(self.camera.screen_to_world(mouse_position))
                            self.rect_started = False

                if event.type == KEYDOWN:
                    if event.key == K_TAB:
                        self.mode = (self.mode + 1) % 2
                        self.update_mode()


            if self.camera.mouse_moving:
                dx,dy = pygame.mouse.get_rel()
                self.camera.x += dx
                self.camera.y += dy

            #UPDATE

            #DRAW
            self.camera.draw_rect(self.blitting_surface, (250,250,250), (0,0, DESING_W, DESING_H), 2)

            for r in self.rects:
                self.camera.draw_rect(self.blitting_surface, (255,0,0), r)

            if self.rect_started:
                mp = self.camera.screen_to_world(mouse_position)
                r = self.get_rect_mouse_drag(mp)
                self.camera.draw_rect(self.blitting_surface, (0,255,0), r)

            blit = pygame.transform.scale(self.blitting_surface, (self.w, self.h))
            self.win.blit(blit, blit.get_rect())
            self.win.blit(self.mode_text,(0,0))
            pygame.display.update()

    def update_mode(self):
        if self.mode == MODE.Camera:
            self.mode_text = MODE_TEXT.render("Camera", 1, (255,255,255))
        if self.mode == MODE.Editor:
            self.mode_text = MODE_TEXT.render("Editor", 1, (255,255,255))

    def create_rect(self, mouse_end):
        self.rects.append(self.get_rect_mouse_drag(mouse_end))

    def get_rect_mouse_drag(self, end):
        size = ((end[0] - self.rect_start[0]), (end[1] - self.rect_start[1]))
        r = pygame.Rect(
                *self.rect_start,
                *size)
        return r

game = Game()
game.run()
