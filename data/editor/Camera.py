import pygame
from pygame.locals import *

class Camera:
    def __init__(self, ws, ds):
        self.x = 0
        self.y = 0
        self.zoom = 1

        self.mouse_moving = 0

        self.ratio = (ds[0] / ws[0], ds[1] / ws[1])
        self.last_offset = (0,0)

    def get_zoomed(self, size):
        return (int(size[0] * self.zoom), int(size[1] * self.zoom))

    def get_offset(self, rect):
        """
        Returns the positon of the rect relative to the camera

        param rect: The rect to convert
        type rect: pygame.Rect
        rtype: (int,int,int,int)
        """
        offset = (int((self.x + rect.x) * self.zoom),
                  int((self.y + rect.y) * self.zoom),
                  int(self.zoom * rect.w),
                  int(self.zoom * rect.h))
        return offset

    def draw_rect(self, surface, color, rect, size=0):
        pos = ((self.x + rect[0]) * self.zoom, (self.y + rect[1]) * self.zoom)
        scl = (self.zoom * rect[2], self.zoom * rect[3])
        pygame.draw.rect(surface, color, (*pos, *scl), size)

    def draw_line(self, surface, color, pt1, pt2, width = 1):
        pos_1 = ((self.x + pt1[0]) * self.zoom, (self.y + pt1[1]) * self.zoom)
        pos_2 = ((self.x + pt2[0]) * self.zoom, (self.y + pt2[1]) * self.zoom)
        pygame.draw.line(surface, color, pos_1, pos_2, width)

    def draw_polygon(self, surface, color, points, width = 0):
        pts = []
        for pt in points:
            pts.append(((self.x + pt[0]) * self.zoom, (self.y + pt[1]) * self.zoom))
        pygame.draw.polygon(surface, color, pts, width)


    def event_zoom(self, event, mouse_position):
        if event.type == MOUSEBUTTONDOWN:
            prev_pos = self.screen_to_world(mouse_position)
            if event.button == 4:
                self.zoom += 0.05
            if event.button == 5:
                self.zoom -= 0.05

            self.zoom = max(0.5, self.zoom)
            self.zoom = min(1.5, self.zoom)

            new_pos = self.screen_to_world(mouse_position)

            self.x += new_pos[0] - prev_pos[0]
            self.y += new_pos[1] - prev_pos[1]

            if event.button == 1:
                self.mouse_moving = 1
                pygame.mouse.get_rel()

        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.mouse_moving = 0

    def screen_to_world(self, pos):
        """
        Convert screen position to game position

        :param pos: on screen position
        :type pos: (int,int)
        :rtype: (int,int)
        """
        return (int(((pos[0] * self.ratio[0] / self.zoom) - self.x)),
                int(((pos[1] * self.ratio[1] / self.zoom) - self.y)))
