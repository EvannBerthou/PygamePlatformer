import os
import pygame
from pygame.locals import *
import UI

from data.utils import *
from data.editor import *

DESING_W, DESING_H = 1920,1080

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
        update_mode(self)

        self.rect_start = None
        self.rect_started = False

        self.UIManager = UI.UIManager()
        self.property_panel = None

        self.selected_object = Wall

        self.wall_button = UI.Button(2,100,100,30, "Wall", (255,0,0), self.change_object, Wall)
        self.door_button = UI.Button(2,140,100,30, "Door", (150,150,150), self.change_object, Door)
        self.spawn_button= UI.Button(2,180,100,30, "Spawn", (150,150,150), self.change_object, SpawnPoint)
        self.plate_button= UI.Button(2,220,100,30, "Plate", (150,150,150), self.change_object, Plate)

        self.selected_button = self.wall_button

        self.UIManager.add(self.wall_button)
        self.UIManager.add(self.door_button)
        self.UIManager.add(self.spawn_button)
        self.UIManager.add(self.plate_button)

        self.spawn_points_count = 0

        self.rects = pygame.sprite.Group(Background((DESING_W, DESING_H)))
        self.selected_rect = -1

    def run(self):
        while self.running:
            tick = self.clock.tick()

            mouse_position = pygame.mouse.get_pos()
            mouse_pressed  = pygame.mouse.get_pressed()

            self.win.fill((0,0,0,))
            self.blitting_surface.fill((0,0,0))

            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    self.running = False
                if event.type == MOUSEBUTTONDOWN:
                    if self.mode == MODE.Camera: mode_camera_mouse_down(self, event)
                    if self.mode == MODE.Editor: mode_editor_mouse_down(self, event, events, mouse_position)

                if event.type == MOUSEBUTTONUP:
                    if self.mode == MODE.Camera: mode_camera_mouse_up(self, event)
                    if self.mode == MODE.Editor: mode_editor_mouse_up(self, mouse_position)

                if event.type == KEYDOWN:
                    on_key_down(self, event, mouse_position)

                if mouse_pressed[0] and self.selected_rect != -1 and self.property_panel == None:
                    move_rect(self, mouse_position)

                if mouse_pressed[2] and self.selected_rect != -1 and self.property_panel == None:
                    on_resize_rect(self, mouse_position)

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

            self.rects.update(cam = self.camera)

            self.rects.draw(self.blitting_surface)

            if self.selected_rect != -1:
                rect = self.rects.sprites()[self.selected_rect]
                rect.outline(self.blitting_surface, self.camera)
                if self.property_panel:
                    if "ColorPicker" in self.property_panel.properties_obj:
                        color = self.property_panel.get_color()
                        rect.color = color

            if self.selected_rect != -1 and isinstance(rect, Plate) and rect.linked_to_id != -1:
                self.camera.draw_line(self.blitting_surface, (0,0,255),
                                        (rect.rect.center[:2]),
                                        (self.rects.sprites()[rect.linked_to_id].rect.center[:2]), 10)
            if self.rect_started:
                mp = self.camera.screen_to_world(mouse_position)
                size = ((mp[0] - self.rect_start[0]), (mp[1] - self.rect_start[1]))
                DragRect(*self.rect_start, *size, (0,255,0)).draw(self.camera, self.blitting_surface)

            if self.property_panel:
                if self.property_panel.linking:
                    self.camera.draw_line(self.blitting_surface, (0,255,0),
                                            (self.rects.sprites()[self.selected_rect].rect.center[:2]),
                                            self.camera.screen_to_world(mouse_position), 10)

            self.camera.draw_rect(self.blitting_surface, (255,255,255), (0,0, DESING_W, DESING_H), 3)
            blit = pygame.transform.scale(self.blitting_surface, (self.w, self.h))
            self.win.blit(blit, blit.get_rect())

            if self.mode == MODE.Editor:
                self.UIManager.draw(self.win)
                if self.property_panel:
                    self.property_panel.draw(self.win)

            self.win.blit(self.mode_text,(0,0))
            pygame.display.update()

    def load_map(self, file_name = 'map'):
        self.rects.empty()
        self.rects.add(Background((DESING_W, DESING_H)))
        self.rects.add(load_map())
    
    def save_to_file(self):
        return save_to_file(self.rects.sprites())

game = Game()
game.run()
