import os,sys
import pygame
from pygame.locals import *
import UI

from data.utils import *
from data.editor import *

from tkinter import filedialog
from tkinter import *

DESING_W, DESING_H = 1920,1080

class Game:
    def change_object(self, button, obj):
        self.selected_object = obj
        self.selected_button.color = (150,150,150)
        button.color = (255,0,0)
        self.selected_button = button

    def map_options(self, btn, args):
        #toggle between save_options_ui and editor_ui
        self.selected_rect = -1
        if self.property_panel:
            self.property_panel.destroy(self.ui_to_draw)
            self.property_panel = None
        self.ui_to_draw = self.save_options_ui if self.ui_to_draw == self.editor_ui else self.editor_ui

    def save_to_file(self, btn, args):
        name = self.map_name.text.strip(' ')
        author = self.map_author.text.strip(' ')
        player_size = 32 if self.player_size.text == "" else int(self.player_size.text)
        if name and author:
            self.map_path = os.path.join('custom_maps', name)
            print(save_to_file(self.rects.sprites(), self.map_path, name, author, self.dialogues, player_size))
        else:
            print('You need to provide a map name and an author name in order to save')

    def open_map(self, btn, args):
        root = Tk().withdraw()
        filename = filedialog.askopenfilename(initialdir = '.', title = 'Select map to open')
        self.load_map(filename)

    def generate_grid(self, x_size, y_size):
        surface = pygame.Surface((DESING_W, DESING_H), SRCALPHA)
        n_x, n_y = DESING_W // x_size, DESING_H // y_size
        for col in range(n_x):
            for row in range(n_y):
                pygame.draw.rect(surface, (255,255,255), (col * x_size, row * y_size, x_size, y_size), 3)
        return surface

    def __init__(self, map_path):
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
        self.drag_start = None
        self.resizing = False

        self.editor_ui = UI.UIManager()
        self.property_panel = None
        self.property_panel_recently_closed = False

        self.selected_object = Wall

        self.wall_button = UI.Button(2,100,100,30, "Wall", (255,0,0), self.change_object, Wall)
        self.door_button = UI.Button(2,140,100,30, "Door", (150,150,150), self.change_object, Door)
        self.spawn_button= UI.Button(2,180,100,30, "Spawn", (150,150,150), self.change_object, SpawnPoint)
        self.plate_button= UI.Button(2,220,100,30, "Plate", (150,150,150), self.change_object, Plate)
        self.goal_button = UI.Button(2,260,100,30, "Goal", (150,150,150), self.change_object, EndGoal)
        self.option_button = UI.Button(5, self.h - 55, 50,50, "O", (150,150,150), self.map_options, [], center_text=True)

        self.selected_button = self.wall_button

        self.editor_ui.add(self.wall_button)
        self.editor_ui.add(self.door_button)
        self.editor_ui.add(self.spawn_button)
        self.editor_ui.add(self.plate_button)
        self.editor_ui.add(self.goal_button)
        self.editor_ui.add(self.option_button)

        self.spawn_points_count = 0

        self.rects = pygame.sprite.Group(Background((DESING_W, DESING_H)))
        self.selected_rect = -1
        self.selected_arrow = ""
        self.vertical_arrow = None
        self.horizontal_arrow = None
        self.moving_offset = None
        self.fixed_point = None


        self.save_options_ui = UI.UIManager()

        self.back_button = UI.Button(self.w / 2 - 225,self.h - 125,100,30,
                                            "Back",(150,150,150),self.map_options,[],center_text=True)

        self.save_button = UI.Button(self.w / 2 + 125,self.h - 125,100,30,
                                            "Save",(150,150,150),self.save_to_file,[],center_text=True)

        self.open_button = UI.Button(self.w / 2,self.h - 125,100,30,
                                            "Open",(150,150,150),self.open_map,[],center_text=True)

        self.map_name_text = UI.Text(self.w / 2 - 225, self.h / 2 - 225, "Map name", 36, (255,255,255))
        self.map_name = UI.InputField(self.w / 2 - 225, self.h / 2 - 200, 400,30, None, None, 50)
        self.map_author_text = UI.Text(self.w / 2 - 225, self.h / 2 - 150, "Map author", 36, (255,255,255))
        self.map_author = UI.InputField(self.w / 2 - 225, self.h / 2 - 125, 400,30, None, None, 50)
        self.player_size_text = UI.Text(self.w / 2 - 225, self.h / 2 - 75, "Player size", 36, (255,255,255))
        self.player_size = UI.InputField(self.w / 2 - 220 + self.player_size_text.get_width(),
                                         self.h / 2 - 75, 50,30, None, None, 50,
                                         text_type = int, char_limit=2)
        self.player_size.set_text('64')

        self.save_options_ui.add(UI.Image(self.w / 2 - 250, self.h / 2 - 250,500,500, color = (200,200,200,200)))
        self.save_options_ui.add(self.back_button)
        self.save_options_ui.add(self.save_button)
        self.save_options_ui.add(self.map_name_text)
        self.save_options_ui.add(self.map_name)
        self.save_options_ui.add(self.map_author_text)
        self.save_options_ui.add(self.map_author)
        self.save_options_ui.add(self.player_size_text)
        self.save_options_ui.add(self.player_size)
        self.save_options_ui.add(self.open_button)

        self.ui_to_draw = self.editor_ui

        self.map_path = map_path
        if self.map_path:
            self.map_data = self.load_map(map_path)
        self.dialogues = []        

        self.grid = self.generate_grid(DESING_W // 16, DESING_H // 9)

    def run(self):
        while self.running:
            tick = self.clock.tick()

            mouse_position = pygame.mouse.get_pos()
            mouse_pressed  = pygame.mouse.get_pressed()

            self.win.fill((0,0,0,))
            self.blitting_surface.fill((0,0,0))

            if mouse_pressed[0] and self.selected_rect != -1 and self.property_panel == None:
                move_rect(self, mouse_position)

            if self.resizing:
                on_resize_rect(self, mouse_position)

            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    self.running = False
                if event.type == MOUSEBUTTONDOWN:
                    if self.mode == MODE.Camera: mode_camera_mouse_down(self, event, mouse_position)
                    if self.mode == MODE.Editor: mode_editor_mouse_down(self, event, events, mouse_position)

                if event.type == MOUSEBUTTONUP:
                    if self.mode == MODE.Camera: mode_camera_mouse_up(self, event, mouse_position)
                    if self.mode == MODE.Editor: mode_editor_mouse_up(self, mouse_position)

                if event.type == KEYDOWN:
                    on_key_down(self, event, mouse_position)


            if self.camera.mouse_moving:
                dx,dy = pygame.mouse.get_rel()
                self.camera.x += dx * (1 / self.camera.zoom)
                self.camera.y += dy * (1 / self.camera.zoom)

            #UPDATE
            self.ui_to_draw.update(mouse_position, mouse_pressed, 0, events)

            self.rects.update(cam = self.camera)

            self.rects.draw(self.blitting_surface)

            if self.selected_rect != -1:
                rect = self.rects.sprites()[self.selected_rect]
                rect.outline(self.blitting_surface, self.camera)
                self.draw_arrows(rect.rect)
                self.check_arrow(mouse_position)
                if self.property_panel:
                    if "ColorPicker" in self.property_panel.properties_obj:
                        color = self.property_panel.get_color()
                        rect.color = color

            if self.selected_rect != -1 and isinstance(rect, Plate) and rect.linked_to_id != -1:
                self.camera.draw_line(self.blitting_surface, (0,0,255),
                                        (rect.org_rect.center[:2]),
                                        (self.rects.sprites()[rect.linked_to_id].org_rect.center[:2]), 10)
            if self.rect_started:
                mp = self.camera.screen_to_world(mouse_position)
                size = ((mp[0] - self.rect_start[0]), (mp[1] - self.rect_start[1]))
                DragRect(*self.rect_start, *size, (0,255,0)).draw(self.camera, self.blitting_surface)

            if self.property_panel:
                if self.property_panel.linking:
                    self.camera.draw_line(self.blitting_surface, (0,255,0),
                                            (self.rects.sprites()[self.selected_rect].org_rect.center[:2]),
                                            self.camera.screen_to_world(mouse_position), 10)

            self.camera.draw_rect(self.blitting_surface, (255,255,255), (0,0, DESING_W, DESING_H), 3)
            self.blitting_surface.blit(self.camera.scale_to_zoom(self.grid), self.camera.get_offset(self.grid.get_rect()))
            blit = pygame.transform.scale(self.blitting_surface, (self.w, self.h))
            self.win.blit(blit, blit.get_rect())

            if self.mode == MODE.Editor:
                self.ui_to_draw.draw(self.win)
                if self.property_panel:
                    self.property_panel.draw(self.win)

            self.win.blit(self.mode_text,(0,0))
            pygame.display.update()

    def load_map(self, map_path):
        self.rects.empty()
        self.rects.add(Background((DESING_W, DESING_H)))
        map_data = load_map(map_path)
        self.spawn_points_count = 2 if map_data['rects'] else 0
        self.rects.add(map_data['rects'])
        self.map_name.set_text(map_data['name'])
        self.map_author.set_text(map_data['author'])
        self.player_size.set_text(map_data['player_size'])
        self.dialogues = map_data['dialogues']
        self.ui_to_draw = self.editor_ui


    def check_arrow(self, mouse_position):
        screen_to_world = self.camera.screen_to_world(mouse_position)
        mouse_rect = pygame.Rect(*screen_to_world, 1,1)
        mp = self.camera.get_offset(mouse_rect)[:2] #Only keep x and y
        if self.vertical_arrow.collidepoint(mp):
            return "vertical"
        if self.horizontal_arrow.collidepoint(mp):
            return "horizontal"
        return ""

    def draw_arrows(self, rect):
        self.vertical_arrow = pygame.Rect(rect.center[0] + 40, rect.center[1], 140,40)
        self.horizontal_arrow = pygame.Rect(rect.center[0], rect.center[1], 40,140)
        pygame.draw.rect(self.blitting_surface, (0,0,255), self.vertical_arrow)
        pygame.draw.rect(self.blitting_surface, (0,255,0), self.horizontal_arrow)


if __name__ == '__main__':
    path = None if len(sys.argv) < 2 else sys.argv[1]
    game = Game(path)
    game.run()
