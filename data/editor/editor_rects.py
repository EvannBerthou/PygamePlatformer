import pygame


class DragRect(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color):
        #pos, scl = convert_rect(x,y,w,h)
        self.rect = pygame.Rect(x, y, w, h)
        self.rect.normalize()
        self.color = color
        self.image = pygame.Surface(self.rect.size)

    def draw(self, camera, surface):
        camera.draw_rect(surface, self.color, self.rect)


def get_corner_point(rect, point):
    """
    Returns the index of the rect's corner in which a point is.
    Top left     : 0
    Top right    : 1
    Bottom left  : 2
    Bottom right : 3

    :param rect: rect to check
    :param point: position of the point
    :type rect: pygame.Rect
    :type point: (int,int)
    :rtype: int
    """
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


def inside_rect(rects, mouse_position, camera):
    """
    Check if a point is inside any rect in a rect list

    :param rects: The list of rects to check
    :param mouse_position: position of the mouse in screen coordinates
    :param camera: the camera used
    :type rects: [pygame.Rect]
    :type mouse_positon: (int, int)
    :type camera: Camera
    :return: the index from the list of the first rect which contains the point
    """
    for i, r in enumerate(rects.sprites()):
        if not r.selectable:
            continue
        if pygame.Rect(r.org_rect).collidepoint(
                camera.screen_to_world(mouse_position)):
            return i
    return -1


def create_rect(rect_start, mouse_end, obj):
    """
    Create a new object going from a start positon to an end position

    :param rect_start: the start position of the rect
    :param mouse_end: the end position of the rect
    :param obj: the type of object to create
    :type rect_start: (int,int)
    :type mouse_end: (int,int)
    :type obj: class
    :rtype: obj typed object
    """
    size = ((mouse_end[0] - rect_start[0]), (mouse_end[1] - rect_start[1]))
    rect = pygame.Rect(*rect_start, *size)
    rect.normalize()
    r = obj(*rect, color=(255, 0, 0))

    if abs(r.rect[2]) < 16 or abs(r.rect[3]) < 16:
        print("The rect is too smol")
        return None

    return r


def resize_rect_arrow(rect, x, y):
    """
    Create a new rect resized with an offset by keeping the same center

    :param rect: rect to resize
    :param x: x offset
    :param y: y offset
    :type rect: pygame.Rect
    :type x: int
    :type y: int
    :rtype: pygame.Rect
    """
    if not rect.resizable:
        return
    new_x = rect.org_rect.x - x
    new_w = rect.org_rect.w + x * 2
    new_y = rect.org_rect.y - y
    new_h = rect.org_rect.h + y * 2
    if new_w < 30 or new_h < 30:
        return
    rect.org_rect = pygame.Rect(new_x, new_y, new_w, new_h)
