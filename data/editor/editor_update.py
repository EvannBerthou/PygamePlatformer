import pygame, copy
from pygame.locals import *

from data.editor import *
from data.GameObjects import *


pygame.font.init()
MODE_TEXT = pygame.font.SysFont(pygame.font.get_default_font(), 46)

class MODE:
    Camera = 0
    Editor = 1

def mode_camera_mouse_down(editor, event, mouse_position):
    editor.camera.event_zoom(event, mouse_position)

def mode_camera_mouse_up(editor, event, mouse_position):
    editor.camera.event_zoom(event, mouse_position)

def mode_camera_key_down(editor):
    pass


def mode_editor_mouse_down(editor, event, events, mouse_position):
    """
    Handles the events when a mouse button is pressed in editor mode

    :param editor: the editor object
    :param event: current event state
    :param events: list of all events in the frame
    :param mouse_position: mouse's position in screen coordinates
    :type editor: Editor
    :type event: event
    :type events: [event]
    :type mouse_position: (int,int)
    :rtype: None
    """
    pygame.mouse.get_rel()
    if editor.ui_to_draw.update(mouse_position, event.button == 1, 0, events) > 0:
        return
    if editor.property_panel == None:
        if not (editor.selected_rect > -1 and editor.check_arrow(mouse_position)):
            editor.selected_rect = inside_rect(editor.rects, mouse_position, editor.camera)
    if editor.selected_rect > -1:
        if event.button == 1:
            mp = editor.camera.screen_to_world(mouse_position)
            rect = editor.rects.sprites()[editor.selected_rect]
            rect.before_drag = rect.org_rect.copy()
            editor.drag_start = editor.camera.screen_to_world(mouse_position)
            editor.draw_arrows(rect.rect)
            editor.selected_arrow = editor.check_arrow(mouse_position)
            pygame.mouse.get_rel()
        if editor.property_panel and not editor.property_panel.linking:
            editor.property_panel.destroy(editor.ui_to_draw)
            editor.property_panel = None
    else:
        #If the selected object is a spawn point, don't drag and create the spawnpoint
        if editor.selected_object == SpawnPoint:
            if editor.spawn_points_count < 2:
                x,y = editor.camera.screen_to_world(mouse_position)
                editor.rects.add(SpawnPoint(x,y, 50, (255,255,255), 0))
                editor.spawn_points_count += 1
            else:
                print('Already 2 spawn points on the map')
        else:
            editor.rect_started = True
            editor.rect_start = editor.camera.screen_to_world(mouse_position)


    if editor.property_panel != None:
        if editor.property_panel.linking:
            world_pos = editor.camera.screen_to_world(mouse_position)
            hover_objs = pygame.Rect(*world_pos, 1,1).collidelistall(editor.rects.sprites())
            if len(hover_objs) > 1: #There is always the background but we don't want it to be linked
                obj = hover_objs[1]
                editor.rects.sprites()[editor.selected_rect].linked_to_id = obj
                print("linked to", obj)
            else:
                print("no link")
            editor.property_panel.linking = False


def mode_editor_mouse_up(editor, mouse_position):
    """
    Handles the events when a mouse button is released in editor mode

    :param editor: the editor object
    :param mouse_position: mouse's position in screen coordinates
    :type editor: Editor
    :type mouse_position: (int,int)
    :rtype: None
    """
    # editor.ui_to_draw.selected = -1
    if editor.rect_started:
        rect = create_rect(editor.rect_start, editor.camera.screen_to_world(mouse_position), editor.selected_object)
        if rect != None:
            editor.rects.add(rect)
        editor.rect_started = False
    editor.drag_start = None
    editor.selected_arrow = ""
    pygame.mouse.get_rel()

def on_key_down(editor, event, mouse_position):
    """
    Handles the events when a key is pressed

    :param editor: the editor object
    :param event: current event
    :param mouse_position: mouse's position in screen coordinates
    :type editor: Editor
    :type event: event
    :type mouse_position: (int,int)
    :rtype: None
    """
    if event.key == K_TAB:
        editor.mode = (editor.mode + 1) % 2
        update_mode(editor)
    if event.key == K_r and event.mod & KMOD_LSHIFT:
        bg = copy.copy(editor.rects.sprites()[0])
        editor.rects.empty()
        editor.selected_rect = -1
        editor.rects.add(bg)
    if event.key == K_DELETE and editor.selected_rect != -1:
        if isinstance(editor.rects.sprites()[editor.selected_rect], SpawnPoint):
            editor.spawn_points_count -= 1
        editor.rects.remove(editor.rects.sprites()[editor.selected_rect])
        editor.selected_rect = -1
    if event.key == K_c and editor.mode == MODE.Editor and editor.selected_rect != -1:
        if editor.property_panel:
            editor.property_panel.destroy(editor.ui_to_draw)
            editor.property_panel = None
        else:
            editor.property_panel = PropertyPanel(*mouse_position,
                                                editor.rects.sprites()[editor.selected_rect].get_properties(),
                                                editor.ui_to_draw, editor.rects.sprites()[editor.selected_rect])
            if "ColorPicker" in editor.property_panel.properties_obj:
                editor.property_panel.set_color(editor.rects.sprites()[editor.selected_rect].color)
    if event.key == K_F1:
        editor.change_object(editor.wall_button, Wall)
    if event.key == K_F2:
        editor.change_object(editor.door_button, Door)
    if event.key == K_s and event.mod & KMOD_LALT:
        editor.save_to_file(None, None)
    if event.key == K_l:
        editor.selected_rect = -1
        editor.load_map(editor.map_path)

def update_mode(editor):
    editor.selected_rect = -1
    if editor.mode == MODE.Camera:
        editor.mode_text = MODE_TEXT.render("Camera", 1, (255,255,255))
    if editor.mode == MODE.Editor:
        editor.mode_text = MODE_TEXT.render("Editor", 1, (255,255,255))


def move_rect(editor, mouse_position):
    r = editor.rects.sprites()[editor.selected_rect]
    if not r:
        return
    mp = editor.camera.screen_to_world(mouse_position)
    if isinstance(r, SpawnPoint):
        r.move(mp)
        r.points = r.get_points()
    else:
        if editor.drag_start:
            r.move(mp, editor.drag_start, editor.selected_arrow)
        else:
            editor.selected_rect = -1

        if isinstance(r, Door):
            r.lines = r.get_lines()

def on_resize_rect(editor, mouse_position):
    """
    Resize the selected rect

    :param editor: the editor object
    :param mouse_position: mouse's position in screen coordinates
    :type editor: Editor
    :type mouse_position: (int,int)
    :rtype: None
    """
    arrow_selected = editor.check_arrow(mouse_position)
    if arrow_selected != "" or editor.selected_arrow != "":
        resize_arrow(editor, arrow_selected)
        return

    r = editor.rects.sprites()[editor.selected_rect]
    corner = get_corner_point(r, editor.camera.screen_to_world(mouse_position))
    if corner != None and r.resizable:
        dx,dy = tuple(l*r for l,r in zip(pygame.mouse.get_rel(), editor.camera.ratio))

        if isinstance(r, Plate):
            if corner == 0 or corner == 2:
                r.rect = (r.rect[0] + dx * (1 / editor.camera.zoom),
                            r.rect[1],
                            r.rect[2] - dx * (1 / editor.camera.zoom), r.rect[3])

            if corner == 1 or corner == 3:
                r.rect = (r.rect[0], r.rect[1],
                            r.rect[2] + dx * (1 / editor.camera.zoom), r.rect[3])
        else:
            r.org_rect = resize_rect(r.org_rect, corner, dx,dy, editor.camera.zoom)
            if isinstance(r, Door):
                r.lines = r.get_lines()

def resize_arrow(editor, arrow):
    """
    Resize the selected rect when an arrow is selected

    :param editor: the editor object
    :param arrow: the selected arrow
    :type editor: Editor
    :type arrow: string
    :rtype: None
    """
    rect = editor.rects.sprites()[editor.selected_rect]
    mouse_rel = pygame.mouse.get_rel()
    if editor.selected_arrow == "":
        editor.selected_arrow = arrow
    if editor.selected_arrow == "vertical":
        resize_rect_arrow(rect, mouse_rel[0], 0)
    if editor.selected_arrow == "horizontal":
        resize_rect_arrow(rect, 0, mouse_rel[1])

