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
        pos = (self.x + rect[0], self.y + rect[1])
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

class MODE:
    Camera = 0
    Editor = 1

class Game:
    def __init__(self):
        self.w, self.h = 1152,648
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
                        self.rect_start = mouse_position

                if event.type == MOUSEBUTTONUP:
                    if self.mode == MODE.Camera:
                        self.camera.event_zoom(event)
                    if self.mode == MODE.Editor:
                        if self.rect_started:
                            self.create_rect(mouse_position)
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
                size = ((mouse_position[0] - self.rect_start[0]) * self.camera.ratio[0],
                        (mouse_position[1] - self.rect_start[1]) * self.camera.ratio[1])
                pos  = (self.rect_start[0] * self.camera.ratio[0], self.rect_start[1] * self.camera.ratio[1])
                r = pygame.Rect(
                        *pos,
                        *size)
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
        size = ((mouse_end[0] - self.rect_start[0]) * self.camera.ratio[0], (mouse_end[1] - self.rect_start[1]) * self.camera.ratio[1])
        pos  = (self.rect_start[0] * self.camera.ratio[0], self.rect_start[1] * self.camera.ratio[1])
        r = pygame.Rect(
                *pos,
                *size)
        self.rects.append(r)

game = Game()
game.run()
