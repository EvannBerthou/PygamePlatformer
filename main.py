import pygame, sys, os
from pygame.locals import *
from data.Level import LevelManager
from data.MainMenu import MainMenu
from data.utils.ConfigManager import load_config, save_config
from editor import Editor

def convert_to_ratio(pos, ratio):
    """
    Convert screen position to game position

    :param pos: on screen position
    :param ratio: ratio of the window
    :type pos: (int,int)
    :type ratio: (int,int)
    :rtype: (int,int)
    """
    return (pos[0] * ratio[0], pos[1] * ratio[1])

class GameState:
    MAIN_MENU = 0
    IN_GAME = 1
    EDITOR = 2

class Game:
    def __init__(self):
        self.config = load_config()
        resolution = self.config["resolution"].split('x')

        self.w, self.h =  int(resolution[0]), int(resolution[1])
        # self.w, self.h =  1920,1080
        self.DESING_W, self.DESING_H = 1920,1080
        self.win = pygame.display.set_mode((self.w,self.h), FULLSCREEN if self.config['fullscreen'] else 0)
        self.blitting_surface = pygame.Surface((self.DESING_W,self.DESING_H), HWSURFACE)
        self.running = True
        self.fullscreen = self.config['fullscreen']
        self.ratio = (self.DESING_W / self.w, self.DESING_H / self.h)

        self.clock = pygame.time.Clock()
        self.level_manager = None
        self.main_menu = MainMenu(self)

        self.game_state = GameState.MAIN_MENU
        self.draw_function = [self.draw_main_menu, self.draw_in_game, self.draw_editor]
        self.editor = None

        self.show_fps = self.config.get('fps_counter', False)
        self.fps_font = pygame.font.SysFont(pygame.font.get_default_font(), 56)

    def run(self):
        render_time = 0
        fps = 60
        update_rate = 60
        fixed_delta_time = round(1000.0 / update_rate)
        while self.running:
            tick = self.clock.tick(update_rate)
            self.blitting_surface.fill((0,0,0))

            mouse_position = convert_to_ratio(pygame.mouse.get_pos(), self.ratio)
            mouse_pressed  = pygame.mouse.get_pressed()
            mouse_rel = pygame.mouse.get_rel()

            events = pygame.event.get()
            for event in events:
                if event.type == QUIT:
                    self.running = False
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        if self.game_state == GameState.IN_GAME: self.load_main_menu()
                    if event.key == K_r:
                        if self.game_state == GameState.IN_GAME: self.level_manager.reload_level(0,0)

            if self.game_state == GameState.MAIN_MENU:
                self.main_menu.update(mouse_position, mouse_pressed, mouse_rel, events)

            if self.game_state == GameState.IN_GAME:
                self.level_manager.update(fixed_delta_time)
                self.level_manager.ui_manager.update(mouse_position, mouse_pressed, mouse_rel, events)

            if self.game_state == GameState.EDITOR:
                self.editor.update(mouse_position, mouse_pressed, mouse_rel, events)

            render_time -= fixed_delta_time
            if render_time <= 0:
                self.draw_function[self.game_state]()

                if self.show_fps:
                    fps_counter = int(self.clock.get_fps())
                    color = (0,255,0)
                    if fps_counter < 45: color = (255,165,0)
                    if fps_counter < 30: color = (255,0,0)
                    fps_text = self.fps_font.render(str(fps_counter), 1, color)
                    self.blitting_surface.blit(fps_text, (self.DESING_W - fps_text.get_width(),0))

                blit = pygame.transform.scale(self.blitting_surface, (self.w, self.h))
                self.win.blit(blit, blit.get_rect())
                pygame.display.update()
                render_time = round(1000 / fps)

    def draw_main_menu(self):
        self.main_menu.draw(self.blitting_surface)
        self.main_menu.draw_ui(self.blitting_surface)

    def draw_in_game(self):
        self.level_manager.draw(self.blitting_surface)
        self.level_manager.draw_ui(self.blitting_surface)

    def draw_editor(self):
        self.editor.draw(self.blitting_surface)

    def load_map(self, map_name):
        self.level_manager = LevelManager((self.DESING_W, self.DESING_H), map_name, self)
        self.game_state = GameState.IN_GAME

    def load_main_menu(self, btn = None, args = None):
        self.level_manager = None
        self.main_menu = MainMenu(self)
        self.game_state = GameState.MAIN_MENU

    def update_screen_size(self, new_size):
        self.w, self.h = new_size
        self.ratio = (self.DESING_W / self.w, self.DESING_H / self.h)

    def save_config(self):
        self.config['fullscreen'] = self.fullscreen
        self.config['resolution'] = f'{self.w}x{self.h}'
        self.config['fps_counter'] = self.show_fps
        save_config(self.config)

    def start_replay(self, map_name, replay_path):
        self.game_state = GameState.IN_GAME
        self.level_manager = LevelManager((self.DESING_W, self.DESING_H), map_name, self, replay = replay_path)
    
    def start_editor(self):
        self.game_state = GameState.EDITOR
        self.editor = Editor(self)
    
    def start_main_menu(self, *args):
        self.game_state = GameState.MAIN_MENU

if __name__ == '__main__':
    game = Game()
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        splitted = file_path.split('.')
        if splitted[1] == 'json':
            map_path = os.path.join('maps', splitted[0])
            game.start_replay(map_path, file_path)
    game.run()
