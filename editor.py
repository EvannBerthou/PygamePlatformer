import pygame
from pygame.locals import *

import UI
from Wall import Wall
from Door import Door

DESING_W, DESING_H = 1920,1080


pygame.font.init()

MODE_TEXT = pygame.font.SysFont("Arial Black", 46)

def invert_color(color):
    return (255 - color[0], 255 - color[1], 255 - color[2])

def get_corner_point(rect, point):
    pr = pygame.Rect(rect)
    sub_rects = [
            pygame.Rect(pr.x, pr.y, pr.w / 2, pr.h / 2),
            pygame.Rect(pr.x + pr.w / 2, pr.y, pr.w / 2, pr.h / 2),
            pygame.Rect(pr.x, pr.y + pr.h / 2, pr.w / 2, pr.h / 2),
            pygame.Rect(pr.x + pr.w / 2, pr.y + pr.h / 2, pr.w / 2, pr.h / 2)
            ]
    for i, sr in enumerate(sub_rects):
        if sr.collidepoint(point):
            return i

class DragRect:
    def __init__(self, x,y,w,h, color):
        self.rect = pygame.Rect(x,y,w,h)
        self.color = color

    def draw(self,camera,surface):
        camera.draw_rect(surface, self.color, self.rect)

class ColorPicker:
    def __init__(self, x,y, UIManager):
        self.x, self.y = x,y
        self.w, self.h = 160,95
        self.r = UI.Slider(self.x + 5, self.y + 5, self.w - 10, 25, 0,255, (150,150,150), (255,0,0))
        self.g = UI.Slider(self.x + 5, self.y + 35, self.w - 10, 25, 0,255, (150,150,150), (0,255,0))
        self.b = UI.Slider(self.x + 5, self.y + 65, self.w - 10, 25, 0,255, (150,150,150), (0,0,255))
        UIManager.add(self.r)
        UIManager.add(self.g)
        UIManager.add(self.b)

    def draw(self, surface):
        pygame.draw.rect(surface, (100,100,100), (self.x, self.y, self.w, self.h))
        self.r.draw(surface)
        self.g.draw(surface)
        self.b.draw(surface)

    def get_color(self):
        return (self.r.value,self.g.value,self.b.value)

    def set_color(self, color):
        self.r.set_value(color[0] / 255)
        self.g.set_value(color[1] / 255)
        self.b.set_value(color[2] / 255)

    def destroy(self, UIManager):
        UIManager.remove(self.r)
        UIManager.remove(self.g)
        UIManager.remove(self.b)


#TODO(#58): Move camera in another file
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

    #TODO(#59): Add draw_line function

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

        self.UIManager = UI.UIManager()
        self.color_picker = None

        self.selected_object = Door

    def run(self):
        while self.running:
            tick = self.clock.tick(60)

            mouse_position = pygame.mouse.get_pos()
            mouse_pressed  = pygame.mouse.get_pressed()

            self.win.fill((0,0,0,))
            self.blitting_surface.fill((0,0,0))

            #TODO: Handle key in different function
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                if event.type == MOUSEBUTTONDOWN:
                    if self.mode == MODE.Camera:
                        self.camera.event_zoom(event)
                    if self.mode == MODE.Editor:
                        self.UIManager.update(mouse_position, event.button == 1)
                        if self.color_picker == None:
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
                        self.UIManager.selected = -1
                        if self.rect_started:
                            self.create_rect(self.camera.screen_to_world(mouse_position))
                            self.rect_started = False

                if event.type == KEYDOWN:
                    if event.key == K_TAB:
                        self.mode = (self.mode + 1) % 2
                        self.update_mode()
                    if event.key == K_r:
                        self.rects.clear()
                    if event.key == K_DELETE and self.selected_rect != -1:
                        self.rects.pop(self.selected_rect)
                        self.selected_rect = -1
                    if event.key == K_c and self.mode == MODE.Editor and self.selected_rect != -1:
                        if self.color_picker:
                            self.color_picker.destroy(self.UIManager)
                            self.color_picker = None
                        else:
                            self.color_picker = ColorPicker(*mouse_position, self.UIManager)
                            self.color_picker.set_color(self.rects[self.selected_rect].color)
                    if event.key == K_F1:
                        self.selected_object = Wall
                    if event.key == K_F2:
                        self.selected_object = Door

                if mouse_pressed[0] and self.selected_rect != -1 and self.color_picker == None:
                    r = self.rects[self.selected_rect]
                    dx,dy = (pygame.mouse.get_rel())
                    r.rect = (r.rect[0] + dx * (1 / self.camera.zoom) * self.camera.ratio[0],
                              r.rect[1] + dy * (1 / self.camera.zoom) * self.camera.ratio[1],
                              r.rect[2], r.rect[3])

                if mouse_pressed[2] and self.selected_rect != -1 and self.color_picker == None:
                    r = self.rects[self.selected_rect]
                    corner = get_corner_point(r, self.camera.screen_to_world(mouse_position))
                    dx,dy = tuple(l*r for l,r in zip(pygame.mouse.get_rel(), self.camera.ratio))

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
            if self.UIManager.selected != -1:
                self.UIManager.elements[self.UIManager.selected].update(mouse_position, mouse_pressed)
                self.rect_started = 0

            #DRAW
            self.camera.draw_rect(self.blitting_surface, (250,250,250), (0,0, DESING_W, DESING_H), 2)

            if self.selected_rect != -1:
                r = self.rects[self.selected_rect].rect
                border = (r[0] - 5, r[1] - 5, r[2] + 10, r[3] + 10)
                color = invert_color(self.rects[self.selected_rect].color)
                #TODO: When the selected object has an inside border, it fills it
                self.camera.draw_rect(self.blitting_surface,color,border)
                if self.color_picker:
                    color = self.color_picker.get_color()
                    self.rects[self.selected_rect].color = color

            for r in self.rects:
                r.draw(self.blitting_surface, self.camera)

            if self.rect_started:
                mp = self.camera.screen_to_world(mouse_position)
                size = ((mp[0] - self.rect_start[0]), (mp[1] - self.rect_start[1]))
                DragRect(*self.rect_start, *size, (0,255,0)).draw(self.camera, self.blitting_surface)

            blit = pygame.transform.scale(self.blitting_surface, (self.w, self.h))
            self.win.blit(blit, blit.get_rect())

            if self.mode == MODE.Editor:
                self.UIManager.draw(self.win)
                if self.color_picker:
                    self.color_picker.draw(self.win)

            self.win.blit(self.mode_text,(0,0))
            pygame.display.update()

    def update_mode(self):
        self.selected_rect = -1
        if self.mode == MODE.Camera:
            self.mode_text = MODE_TEXT.render("Camera", 1, (255,255,255))
        if self.mode == MODE.Editor:
            self.mode_text = MODE_TEXT.render("Editor", 1, (255,255,255))

    def create_rect(self, mouse_end):
        size = ((mouse_end[0] - self.rect_start[0]), (mouse_end[1] - self.rect_start[1]))
        r = self.selected_object(*self.rect_start, *size, (255,0,0))

        if abs(r.rect[2]) < 16 or abs(r.rect[3]) < 16:
            print ("The rect is too smol")
            return

        rr = r.rect
        #bottom left
        if rr[2] > 0 and rr[3] < 0:
            rr = (rr[0], rr[1] + rr[3], rr[2], abs(rr[3]))
        #bottom right
        if rr[2] < 0 and rr[3] < 0:
            rr = (rr[0] + rr[2], rr[1] + rr[3], abs(rr[2]), abs(rr[3]))
        #top right
        if rr[2] < 0 and rr[3] > 0:
            rr = (rr[0] + rr[2], rr[1], abs(rr[2]), rr[3])

        r.rect = rr
        self.rects.append(r)

    def inside_rect(self, mouse_position):
        for i,r in enumerate(self.rects):
            if pygame.Rect(r.rect).collidepoint(self.camera.screen_to_world(mouse_position)):
                return i
        return -1

game = Game()
game.run()
