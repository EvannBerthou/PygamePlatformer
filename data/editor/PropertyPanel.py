import pygame
from . import ColorPicker
from UI import Button

class PropertyPanel:
    def __init__(self, x,y, properties, UIManager, selected_obj):
        self.x, self.y = x,y
        self.w, self.h = 320,10
        self.properties_obj = {}

        self.padding = 10

        self.linking = False

        for p in properties:
            if p == "ColorPicker":
                cp = ColorPicker(self.x,self.y, UIManager)
                self.properties_obj[p] = cp
                self.h += cp.h + self.padding
            if p == "Player_Id":
                text = f"player : {selected_obj.player_id}"
                b = Button(self.x+10,self.y+self.h,
                            300,70,text, (170,170,170), selected_obj.switch_player_id, [], center_text=True)
                UIManager.add(b)
                self.properties_obj[p] = b
                self.h += b.rect.h + self.padding
            if p == "Linker":
                b = Button(self.x + 10, self.y + self.h,
                            300,70,"Link", (170,170,170), self.toggle_linker, [])
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

    def toggle_linker(self, btn, player_id):
        self.linking = not self.linking
