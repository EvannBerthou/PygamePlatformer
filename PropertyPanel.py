import pygame
from ColorPicker import ColorPicker

class PropertyPanel:
    def get_obj_from_str(self, string):
        return {"ColorPicker": ColorPicker }[string]

    def __init__(self, x,y, properties, UIManager):
        self.x, self.y = x,y
        self.w, self.h = 160,95 #TEMP
        self.properties_obj = {}

        for p in properties:
            obj = self.get_obj_from_str(p)
            print(p, obj)
            self.properties_obj[p] = obj(self.x,self.y, UIManager)

    def draw(self, surface):
        pygame.draw.rect(surface, (100,100,100), (self.x, self.y, self.w, self.h))
        for key,obj in self.properties_obj.items():
            obj.draw(surface)

    def destroy(self, UIManager):
        for key,obj in self.properties_obj.items():
            obj.destroy(UIManager)

    def set_color(self, color):
        if "ColorPicker" in self.properties_obj:
            self.properties_obj["ColorPicker"].set_color(color)

    def get_color(self):
        if "ColorPicker" in self.properties_obj:
            return self.properties_obj["ColorPicker"].get_color()

