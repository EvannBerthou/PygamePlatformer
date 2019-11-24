import os
import pygame
from pygame.locals import *

import UI
from Wall import Wall
from Door import Door
from SpawnPoint import SpawnPoint
from PropertyPanel import PropertyPanel

from Camera import Camera


DESING_W, DESING_H = 1920,1080


pygame.font.init()

MODE_TEXT = pygame.font.SysFont("Arial Black", 46)

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

class MODE:
    Camera = 0
    Editor = 1

class Game:
    def change_object(self, button, obj):
        self.selected_object = obj
        self.selected_button.color = (150,150,150)
        button.color = (255,0,0)
        self.selected_button = button

    def __init__(self):
        self.w, self.h = 1152,648
        # self.w, self.h = 1920,1080
        self.win = pygame.display.set_mode((self.w,self.h))
        self.blitting_surface = pygame.Surface((DESING_W,DESING_H))
        self.running = True

        self.clock = pygame.time.Clock()

        self.mouse_moving = 0

        self.camera = Camera((self.w,self.h), (DESING_W, DESING_H))

        self.mode_text = None
        self.mode = MODE.Camera
        self.update_mode()

        self.rect_start = None
        self.rect_started = False

        self.rects = []
        self.selected_rect = -1

        self.UIManager = UI.UIManager()
        self.property_panel = None

        self.selected_object = Wall

        self.wall_button = UI.Button(2,100,100,30, "Wall", (255,0,0), self.change_object, Wall)
        self.door_button = UI.Button(2,140,100,30, "Door", (150,150,150), self.change_object, Door)
        self.spawn_button= UI.Button(2,180,100,30, "Spawn", (150,150,150), self.change_object, SpawnPoint)

        self.selected_button = self.wall_button

        self.UIManager.add(self.wall_button)
        self.UIManager.add(self.door_button)
        self.UIManager.add(self.spawn_button)

        self.spawn_points_count = 0

    def run(self):
        while self.running:
            tick = self.clock.tick(60)

            mouse_position = pygame.mouse.get_pos()
            mouse_pressed  = pygame.mouse.get_pressed()

            self.win.fill((0,0,0,))
            self.blitting_surface.fill((0,0,0))

            #TODO(#60): Handle key in different function
            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    self.running = False
                if event.type == MOUSEBUTTONDOWN:
                    if self.mode == MODE.Camera:
                        self.camera.event_zoom(event)
                    if self.mode == MODE.Editor:
                        if self.UIManager.update(mouse_position, event.button == 1, events) > 0:
                            continue
                        if self.property_panel == None:
                            self.selected_rect = self.inside_rect(mouse_position)
                        if self.selected_rect > -1:
                            pygame.mouse.get_rel()
                        else:
                            #If the selected object is a spawn point, don't drag and create the spawnpoint
                            if self.selected_object == SpawnPoint:
                                if self.spawn_points_count < 2:
                                    x,y = self.camera.screen_to_world(mouse_position)
                                    self.rects.append(SpawnPoint(x,y, 50, (255,255,255), 0))
                                    self.spawn_points_count += 1
                                else:
                                    print('Already 2 spawn points on the map')
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
                        if isinstance(self.rects[self.selected_rect], SpawnPoint):
                            self.spawn_points_count -= 1
                        self.rects.pop(self.selected_rect)
                        self.selected_rect = -1
                    if event.key == K_c and self.mode == MODE.Editor and self.selected_rect != -1:
                        if self.property_panel:
                            self.property_panel.destroy(self.UIManager)
                            self.property_panel = None
                        else:
                            self.property_panel = PropertyPanel(*mouse_position,
                                                                self.rects[self.selected_rect].get_properties(),
                                                                self.UIManager, self.rects[self.selected_rect])
                            if "ColorPicker" in self.property_panel.properties_obj:
                                self.property_panel.set_color(self.rects[self.selected_rect].color)
                    if event.key == K_F1:
                        self.change_object(self.wall_button, Wall)
                    if event.key == K_F2:
                        self.change_object(self.door_button, Door)
                    if event.key == K_s:
                        self.save_to_file()
                    if event.key == K_l:
                        self.load_map()

                if mouse_pressed[0] and self.selected_rect != -1 and self.property_panel == None:
                    r = self.rects[self.selected_rect]

                    if isinstance(r, SpawnPoint):
                        mp = self.camera.screen_to_world(mouse_position)
                        r.rect = pygame.Rect(mp[0] - r.lenght / 2, mp[1] - r.lenght / 2, r.lenght, r.lenght)
                        r.points = r.get_points()
                    else:
                        dx,dy = (pygame.mouse.get_rel())
                        r.rect = pygame.Rect(r.rect[0] + dx * (1 / self.camera.zoom) * self.camera.ratio[0],
                                             r.rect[1] + dy * (1 / self.camera.zoom) * self.camera.ratio[1],
                                             r.rect[2], r.rect[3])
                        if isinstance(r, Door):
                            r.lines = r.get_lines()

                if mouse_pressed[2] and self.selected_rect != -1 and self.property_panel == None:
                    r = self.rects[self.selected_rect]
                    corner = get_corner_point(r, self.camera.screen_to_world(mouse_position))
                    if corner != None:
                        dx,dy = tuple(l*r for l,r in zip(pygame.mouse.get_rel(), self.camera.ratio))

                        r.rect = self.resize_rect(r.rect, corner, dx,dy)
                        if isinstance(r, Door):
                            r.lines = r.get_lines()

            if self.camera.mouse_moving:
                dx,dy = pygame.mouse.get_rel()
                self.camera.x += dx * (1 / self.camera.zoom)
                self.camera.y += dy * (1 / self.camera.zoom)

            #UPDATE
            if self.UIManager.selected != -1:
                self.UIManager.elements[self.UIManager.selected].update(mouse_position, mouse_pressed, events)
                self.rect_started = 0
                if self.property_panel == None:
                    self.selected_rect = -1

            #DRAW
            self.camera.draw_rect(self.blitting_surface, (250,250,250), (0,0, DESING_W, DESING_H), 2)

            if self.selected_rect != -1:
                self.rects[self.selected_rect].outline(self.blitting_surface, self.camera)
                if self.property_panel:
                    if "ColorPicker" in self.property_panel.properties_obj:
                        color = self.property_panel.get_color()
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
                if self.property_panel:
                    self.property_panel.draw(self.win)

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
        r = self.selected_object(*self.rect_start, *size, color=(255,0,0))

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

    def resize_rect(self, rect, corner, dx,dy):
        AREA_LIMIT = 2000
        new_rect = None
        if corner == 0:
            new_rect = (rect[0] + dx * (1 / self.camera.zoom),
                        rect[1] + dy * (1 / self.camera.zoom),
                        rect[2] - dx * (1 / self.camera.zoom),
                        rect[3] - dy * (1 / self.camera.zoom))

        elif corner == 1:
            new_rect = (rect[0],
                        rect[1] + dy * (1 / self.camera.zoom),
                        rect[2] + dx * (1 / self.camera.zoom),
                        rect[3] - dy * (1 / self.camera.zoom))

        elif corner == 2:
            new_rect = (rect[0] + dx * (1 / self.camera.zoom),
                        rect[1],
                        rect[2] - dx * (1 / self.camera.zoom),
                        rect[3] + dy * (1 / self.camera.zoom))

        elif corner == 3:
            new_rect = (rect[0],
                        rect[1],
                        rect[2] + dx * (1 / self.camera.zoom),
                        rect[3] + dy * (1 / self.camera.zoom))
        area = new_rect[2] * new_rect[3]
        if area < AREA_LIMIT:
            return rect
        return pygame.Rect(new_rect)

    def save_to_file(self):
        with open('map', 'w') as f:
            f.write('name : FOO\n')
            f.write('author : BAR\n')
            f.write('map:\n')
            for obj in self.rects:
                string = obj.as_string()
                f.write(string)
            f.write('endmap\n')

    def obj_from_str(self, string):
        objs = {
            "Wall": Wall,
            "Door": Door,
            "Spawn": SpawnPoint
        }
        return objs[string]

    def create_obj(self, obj, args):
        if obj == Wall:
            pos = []
            color = []
            for v in args[:4]:
                pos.append(int(v))
            for v in args[4:]:
                color.append(int(v))

            wall = Wall(*pos, color)
            self.rects.append(wall)

        if obj == Door:
            pos = []
            for v in args[:4]:
                pos.append(int(v))

            door = Door(*pos, 0, int(args[4]))
            self.rects.append(door)

    def load_map(self, file_name = 'map'):
        print('Loading map')
        if not os.path.exists(file_name):
            print(f'No file named : {file_name}')
            return

        self.rects.clear()
        self.selected_rect = -1
        in_map = False
        with open('map', 'r') as f:
            for l in f:
                if l == "endmap\n":
                    in_map = False

                if in_map:
                    parts = l.strip().split(',')
                    obj = self.obj_from_str(parts[0])
                    self.create_obj(obj, parts[1:])

                if l == "map:\n":
                    in_map = True
        print('Map loaded')


game = Game()
game.run()
