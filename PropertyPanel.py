import pygame
from ColorPicker import ColorPicker
from UI import Button

class PropertyPanel:
    def __init__(self, x,y, properties, UIManager, selected_obj):
        self.x, self.y = x,y
        self.w, self.h = 160,0 #TEMP
        self.properties_obj = {}

        self.padding = 5

        for p in properties:
            if p == "ColorPicker":
                cp = ColorPicker(self.x,self.y, UIManager)
                self.properties_obj[p] = cp
                self.h += cp.h + self.padding
            if p == "Player_Id":
                text = f"player : {selected_obj.player_id}"
                b = Button(self.x+5,self.y+95, 150,35,text, (170,170,170), selected_obj.switch_player_id, [])
                UIManager.add(b)
                self.properties_obj[p] = b
                self.h += b.rect.h + self.padding

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

