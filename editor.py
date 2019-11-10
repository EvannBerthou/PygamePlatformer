import pygame
from pygame.locals import *

DESING_W, DESING_H = 1920,1080

pygame.font.init()

MODE_TEXT = pygame.font.SysFont("Arial Black", 46)

class Rect:
    def __init__(self, x,y,w,h, color):
        self.rect = (x,y,w,h)
        self.color = color

    def draw(self, camera, surface):
        camera.draw_rect(surface, self.color, self.rect)

    '''
    0:  top     right
    1:  top     left
    2:  bottom  right
    3:  bottom  left
    '''
    def get_corner_point(self, point):
        pr = pygame.Rect(self.rect)
        sub_rects = [
                pygame.Rect(pr.x, pr.y, pr.w / 2, pr.h / 2),
                pygame.Rect(pr.x + pr.w / 2, pr.y, pr.w / 2, pr.h / 2),
                pygame.Rect(pr.x, pr.y + pr.h / 2, pr.w / 2, pr.h / 2),
                pygame.Rect(pr.x + pr.w / 2, pr.y + pr.h / 2, pr.w / 2, pr.h / 2)
                ]
        for i, sr in enumerate(sub_rects):
            if sr.collidepoint(point):
                return i

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

                self.zoom = max(0.5, self.zoom)
                self.zoom = min(1.5, self.zoom)

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
        self.selected_rect = -1

    def run(self):
        while self.running:
            tick = self.clock.tick(60)

            mouse_position = pygame.mouse.get_pos()
            mouse_pressed  = pygame.mouse.get_pressed()

            self.win.fill((0,0,0,))
            self.blitting_surface.fill((0,0,0))

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                if event.type == MOUSEBUTTONDOWN:
                    if self.mode == MODE.Camera:
                        self.camera.event_zoom(event)
                    if self.mode == MODE.Editor:
                        self.selected_rect = self.inside_rect(mouse_position)
                        if self.selected_rect > -1:
                            pygame.mouse.get_rel()
                        else:
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
                    if event.key == K_r:
                        self.rects.clear()

                if mouse_pressed[0] and self.selected_rect != -1:
                    r = self.rects[self.selected_rect]
                    dx,dy = self.camera.screen_to_world(pygame.mouse.get_rel())
                    r.rect = (r.rect[0] + dx * (1 / self.camera.zoom),
                              r.rect[1] + dy * (1 / self.camera.zoom),
                              r.rect[2], r.rect[3])

                if mouse_pressed[2] and self.selected_rect != -1:
                    r = self.rects[self.selected_rect]
                    corner = r.get_corner_point(self.camera.screen_to_world(mouse_position))
                    dx,dy = self.camera.screen_to_world(pygame.mouse.get_rel())

                    #TODO: Extract this code in its own function and think of a refactor
                    if corner == 0:
                        r.rect = (r.rect[0] + dx * (1 / self.camera.zoom),
                                  r.rect[1] + dy * (1 / self.camera.zoom),
                                  r.rect[2] - dx * (1 / self.camera.zoom),
                                  r.rect[3] - dy * (1 / self.camera.zoom))

                    elif corner == 1:
                        r.rect = (r.rect[0],
                                  r.rect[1] + dy * (1 / self.camera.zoom),
                                  r.rect[2] + dx * (1 / self.camera.zoom),
                                  r.rect[3] - dy * (1 / self.camera.zoom))

                    elif corner == 2:
                        r.rect = (r.rect[0] + dx * (1 / self.camera.zoom),
                                  r.rect[1],
                                  r.rect[2] - dx * (1 / self.camera.zoom),
                                  r.rect[3] + dy * (1 / self.camera.zoom))

                    elif corner == 3:
                        r.rect = (r.rect[0],
                                  r.rect[1],
                                  r.rect[2] + dx * (1 / self.camera.zoom),
                                  r.rect[3] + dy * (1 / self.camera.zoom))

            if self.camera.mouse_moving:
                dx,dy = pygame.mouse.get_rel()
                self.camera.x += dx * (1 / self.camera.zoom)
                self.camera.y += dy * (1 / self.camera.zoom)

            #UPDATE

            #DRAW
            self.camera.draw_rect(self.blitting_surface, (250,250,250), (0,0, DESING_W, DESING_H), 2)

            if self.selected_rect != -1:
                r = self.rects[self.selected_rect].rect
                border = (r[0] - 5, r[1] - 5, r[2] + 10, r[3] + 10)
                self.camera.draw_rect(self.blitting_surface, (0,0,255), border)

            for r in self.rects:
                r.draw(self.camera, self.blitting_surface)

            if self.rect_started:
                mp = self.camera.screen_to_world(mouse_position)
                self.get_rect_mouse_drag(mp,(0,255,0)).draw(self.camera, self.blitting_surface)

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
        self.rects.append(self.get_rect_mouse_drag(mouse_end, (255,0,0)))

    def get_rect_mouse_drag(self, end, color):
        size = ((end[0] - self.rect_start[0]), (end[1] - self.rect_start[1]))
        r = Rect(*self.rect_start,*size, color)
        return r

    def inside_rect(self, mouse_position):
        for i,r in enumerate(self.rects):
            if pygame.Rect(r.rect).collidepoint(self.camera.screen_to_world(mouse_position)):
                return i
        return -1

game = Game()
game.run()
