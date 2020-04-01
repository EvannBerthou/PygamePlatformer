import os,sys
import pygame
from pygame.locals import *
import UI

from data.utils import *
from data.editor import *
from data.GameObjects import *

from tkinter import filedialog
from tkinter import *

DESIGN_W, DESIGN_H = 1920,1080

class Editor:
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
        self.map_path = filename

    def generate_grid(self, x_size, y_size):
        self.grid_x, self.grid_y = x_size, y_size
        self.grid_sizes = (DESIGN_W // self.grid_x, DESIGN_H // self.grid_y)
        surface = pygame.Surface((DESIGN_W, DESIGN_H), SRCALPHA)
        for col in range(self.grid_x):
            for row in range(self.grid_y):
                pygame.draw.rect(surface, (255,255,255), (col * self.grid_sizes[0], row * self.grid_sizes[1],
                                                          self.grid_sizes[0], self.grid_sizes[1]), 3)
        return surface

    def update_grid(self):
        x_size = int(self.x_grid_slider.value)
        y_size = int(self.y_grid_slider.value)
        self.grid = self.generate_grid(x_size, y_size)

    def __init__(self, game):
        self.game = game
        self.custom_blitting = pygame.Surface((DESIGN_W, DESIGN_H))
        self.mouse_moving = 0
        self.camera = Camera((self.game.w, self.game.h), (DESIGN_W, DESIGN_H))

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

        self.grid = self.generate_grid(16,9)

        self.wall_button = UI.Button(2,200,200,60, "Wall", (255,0,0), self.change_object, Wall)
        self.door_button = UI.Button(2,280,200,60, "Door", (150,150,150), self.change_object, Door)
        self.spawn_button= UI.Button(2,360,200,60, "Spawn", (150,150,150), self.change_object, SpawnPoint)
        self.plate_button= UI.Button(2,440,200,60, "Plate", (150,150,150), self.change_object, Plate)
        self.goal_button = UI.Button(2,520,200,60, "Goal", (150,150,150), self.change_object, EndGoal)
        self.option_button = UI.Button(5, DESIGN_H - 110, 100,100, "O", (150,150,150), self.map_options, [], center_text=True)
        self.x_grid_text = UI.Text(740, DESIGN_H - 110, self.grid_x, 72, (255,255,255))
        self.y_grid_text = UI.Text(740, DESIGN_H - 50, self.grid_y, 72, (255,255,255))
        self.x_grid_slider = UI.Slider(130, DESIGN_H - 110, 600,40, 1,33, (150,150,150), (200,200,200), self.update_grid, self.x_grid_text, value_type='int')
        self.y_grid_slider = UI.Slider(130, DESIGN_H - 50, 600,40, 1,33, (150,150,150), (200,200,200), self.update_grid, self.y_grid_text, value_type='int')
        self.x_grid_slider.set_value(self.grid_x / 33)
        self.y_grid_slider.set_value(self.grid_y / 33)

        self.exit_button = UI.Button(DESIGN_W - 110, 5, 100,100, "X", (150,150,150), self.game.start_main_menu, '', center_text=True)

        self.selected_button = self.wall_button

        self.editor_ui.add(self.wall_button)
        self.editor_ui.add(self.door_button)
        self.editor_ui.add(self.spawn_button)
        self.editor_ui.add(self.plate_button)
        self.editor_ui.add(self.goal_button)
        self.editor_ui.add(self.option_button)
        self.editor_ui.add(self.x_grid_text)
        self.editor_ui.add(self.y_grid_text)
        self.editor_ui.add(self.x_grid_slider)
        self.editor_ui.add(self.y_grid_slider)
        self.editor_ui.add(self.exit_button)

        self.spawn_points_count = 0

        self.rects = pygame.sprite.Group(Background((DESIGN_W, DESIGN_H)))
        self.selected_rect = -1
        self.selected_arrow = ""
        self.vertical_arrow = None
        self.horizontal_arrow = None
        self.moving_offset = None
        self.fixed_point = None


        self.save_options_ui = UI.UIManager()

        self.back_button = UI.Button(DESIGN_W / 2 - 480,DESIGN_H - 150,200,60,
                                            "Back",(150,150,150),self.map_options,[],center_text=True)

        self.save_button = UI.Button(DESIGN_W / 2 + 250,DESIGN_H - 150,200,60,
                                            "Save",(150,150,150),self.save_to_file,[],center_text=True)

        self.open_button = UI.Button(DESIGN_W / 2,DESIGN_H - 150,200,60,
                                            "Open",(150,150,150),self.open_map,[],center_text=True)

        self.map_name_text = UI.Text(DESIGN_W / 2 - 500, DESIGN_H / 2 - 450, "Map name", 72, (255,255,255))
        self.map_name = UI.InputField(DESIGN_W / 2 - 500, DESIGN_H / 2 - 400, 800,60, None, None, 100)
        self.map_author_text = UI.Text(DESIGN_W / 2 - 500, DESIGN_H / 2 - 300, "Map author", 72, (255,255,255))
        self.map_author = UI.InputField(DESIGN_W / 2 - 500, DESIGN_H / 2 - 250, 800,60, None, None, 100)
        self.player_size_text = UI.Text(DESIGN_W / 2 - 500, DESIGN_H / 2 - 150, "Player size", 72, (255,255,255))
        self.player_size = UI.InputField(DESIGN_W / 2 - 440 + self.player_size_text.get_width(),
                                         DESIGN_H / 2 - 150, 100,60, None, None, 100,
                                         text_type = int, char_limit=2)
        self.player_size.set_text('64')

        self.save_options_ui.add(UI.Image(DESIGN_W / 2 - 510, DESIGN_H / 2 - 510,1000,1000, color = (200,200,200,240)))
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

        #self.map_path = map_path
        #if self.map_path:
            #self.map_data = self.load_map(map_path)
        self.dialogues = []        


    def update(self, mouse_position, mouse_pressed, mouse_rel, events):
        if mouse_pressed[0] and self.selected_rect != -1 and self.property_panel == None:
            move_rect(self, mouse_position)

        if self.resizing:
            on_resize_rect(self, mouse_position)

        for event in events:
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
        self.cliked_on_ui = self.ui_to_draw.update(mouse_position, mouse_pressed, 0, events)

        self.rects.update(cam = self.camera)

        self.rects.draw(self.custom_blitting)

        if self.selected_rect != -1:
            rect = self.rects.sprites()[self.selected_rect]
            rect.outline(self.custom_blitting, self.camera)
            self.draw_arrows(rect.rect)
            self.check_arrow(mouse_position)
            if self.property_panel:
                if "ColorPicker" in self.property_panel.properties_obj:
                    color = self.property_panel.get_color()
                    rect.color = color

        if self.selected_rect != -1 and isinstance(rect, Plate) and rect.linked_to_id != -1:
            self.camera.draw_line(self.custom_blitting, (0,0,255),
                                    (rect.org_rect.center[:2]),
                                    (self.rects.sprites()[rect.linked_to_id].org_rect.center[:2]), 10)
        if self.rect_started:
            mp = self.camera.screen_to_world(mouse_position)
            size = ((mp[0] - self.rect_start[0]), (mp[1] - self.rect_start[1]))
            DragRect(*self.rect_start, *size, (0,255,0)).draw(self.camera, self.custom_blitting)

        if self.property_panel:
            if self.property_panel.linking:
                self.camera.draw_line(self.custom_blitting, (0,255,0),
                                        (self.rects.sprites()[self.selected_rect].org_rect.center[:2]),
                                        self.camera.screen_to_world(mouse_position), 10)

        self.camera.draw_rect(self.custom_blitting, (255,255,255), (0,0, DESIGN_W, DESIGN_H), 3)
        self.custom_blitting.blit(self.camera.scale_to_zoom(self.grid), self.camera.get_offset(self.grid.get_rect()))
        if self.mode == MODE.Editor:
            self.ui_to_draw.draw(self.custom_blitting)
            if self.property_panel:
                self.property_panel.draw(self.custom_blitting)
        self.custom_blitting.blit(self.mode_text,(0,0))


    def draw(self, surface):
        blit = pygame.transform.scale(self.custom_blitting, surface.get_size())
        surface.blit(blit, (0,0))

    def load_map(self, map_path):
        self.rects.empty()
        self.rects.add(Background((DESIGN_W, DESIGN_H)))
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
        pygame.draw.rect(self.custom_blitting, (0,0,255), self.vertical_arrow)
        pygame.draw.rect(self.custom_blitting, (0,255,0), self.horizontal_arrow)