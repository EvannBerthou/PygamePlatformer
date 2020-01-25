import pygame

class DragRect(pygame.sprite.Sprite):
    def __init__(self, x,y,w,h, color):
        pos, scl = convert_rect(x,y,w,h)
        self.rect = pygame.Rect(*pos, *scl)
        self.color = color
        self.image = pygame.Surface(scl)

    def draw(self,camera,surface):
        camera.draw_rect(surface, self.color, self.rect)

def convert_rect(x,y,w,h):
    pos = [x,y]
    scl = [w,h]

    if w >= 0 and h <= 0:
        pos = [x,y + h]
        scl = [w, abs(h)]

    if w <= 0 and h <= 0:
        pos = [x + w, y + h]
        scl = [abs(w), abs(h)]

    if w <= 0 and h >= 0:
        pos = [x + w, y]
        scl = [abs(w), h]

    return pos, scl

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

def resize_rect(rect, corner, dx,dy, zoom):
    AREA_LIMIT = 2000
    new_rect = None
    if corner == 0:
        new_rect = (rect[0] + dx * (1 / zoom),
                    rect[1] + dy * (1 / zoom),
                    rect[2] - dx * (1 / zoom),
                    rect[3] - dy * (1 / zoom))

    elif corner == 1:
        new_rect = (rect[0],
                    rect[1] + dy * (1 / zoom),
                    rect[2] + dx * (1 / zoom),
                    rect[3] - dy * (1 / zoom))

    elif corner == 2:
        new_rect = (rect[0] + dx * (1 / zoom),
                    rect[1],
                    rect[2] - dx * (1 / zoom),
                    rect[3] + dy * (1 / zoom))

    elif corner == 3:
        new_rect = (rect[0],
                    rect[1],
                    rect[2] + dx * (1 / zoom),
                    rect[3] + dy * (1 / zoom))
    area = new_rect[2] * new_rect[3]
    if area < AREA_LIMIT:
        return rect
    return pygame.Rect(new_rect)

def inside_rect(rects, mouse_position, camera):
    for i,r in enumerate(rects.sprites()):
        if r.selectable == False: continue
        if pygame.Rect(r.org_rect).collidepoint(camera.screen_to_world(mouse_position)):
            return i
    return -1

def create_rect(rect_start, mouse_end, obj):
    size = ((mouse_end[0] - rect_start[0]), (mouse_end[1] - rect_start[1]))
    pos, scl = convert_rect(*rect_start, *size)
    r = obj(*pos, *scl, color=(255,0,0))

    if abs(r.rect[2]) < 16 or abs(r.rect[3]) < 16:
        print ("The rect is too smol")
        return None

    return r
