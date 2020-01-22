import pygame, sys
from pygame.locals import *
from data.Level import LevelManager
from data.MainMenu import MainMenu

def convert_to_ratio(pos, ratio):
    return (pos[0] * ratio[0], pos[1] * ratio[1])

class GameState:
    MAIN_MENU = 0
    IN_GAME = 1

class Game:
    def __init__(self):
        self.w, self.h =  1152,648
        # self.w, self.h =  1920,1080
        self.DESING_W, self.DESING_H = 1920,1080
        self.win = pygame.display.set_mode((self.w,self.h))
        self.blitting_surface = pygame.Surface((self.DESING_W,self.DESING_H), HWSURFACE)
        self.running = True
        self.fullscreen = False
        self.ratio = (self.DESING_W / self.w, self.DESING_H / self.h)

        self.clock = pygame.time.Clock()
        self.level_manager = None
        self.main_menu = MainMenu(self)

        self.game_state = GameState.MAIN_MENU
        self.draw_function = [self.draw_main_menu, self.draw_in_game]

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

            if self.game_state == GameState.MAIN_MENU:
                self.main_menu.update(mouse_position, mouse_pressed, mouse_rel, events)

            if self.game_state == GameState.IN_GAME:
                self.level_manager.update(fixed_delta_time)
                self.level_manager.ui_manager.update(mouse_position, mouse_pressed, mouse_rel, events)

            render_time -= fixed_delta_time
            if render_time <= 0:
                self.draw_function[self.game_state]()
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

game = Game()
game.run()
