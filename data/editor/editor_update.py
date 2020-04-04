import pygame, copy
from pygame.locals import *

from data.editor import *

from data.GameObjects.Door import Door
from data.GameObjects.SpawnPoint import SpawnPoint

import random

pygame.font.init()
MODE_TEXT = pygame.font.SysFont(pygame.font.get_default_font(), 82)

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
    if editor.cliked_on_ui > -1:
        return
    if editor.ui_to_draw == editor.save_options_ui:
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
        if event.button == 3 and editor.selected_rect != -1 and editor.property_panel == None:
            start_resize(editor, mouse_position)
        if editor.property_panel and not editor.property_panel.linking:
            editor.property_panel.destroy(editor.ui_to_draw)
            editor.property_panel = None
            editor.property_panel_recently_closed = True
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
            if event.button == 1:
                editor.rect_started = True
                editor.rect_start = editor.camera.screen_to_world(mouse_position)


    if editor.property_panel != None:
        if editor.property_panel.linking:
            world_pos = editor.camera.screen_to_world(mouse_position)
            hover_objs = pygame.Rect(*world_pos, 1,1).collidelistall(editor.rects.sprites())
            if len(hover_objs) > 1: #There is always the background but we don't want it to be linked
                obj = hover_objs[1]
                if isinstance(editor.rects.sprites()[obj], Door):
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
    editor.property_panel_recently_closed = False
    editor.fixed_point = None
    editor.moving_offset = None
    editor.resizing = False

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
    config = editor.game.config
    if event.key == config['ed_mode']:
        editor.mode = (editor.mode + 1) % 2
        update_mode(editor)
    if event.key == config['ed_clear'] and event.mod & KMOD_LSHIFT:
        bg = copy.copy(editor.rects.sprites()[0])
        editor.rects.empty()
        editor.selected_rect = -1
        editor.rects.add(bg)
    if event.key == K_DELETE and editor.selected_rect != -1:
        if isinstance(editor.rects.sprites()[editor.selected_rect], SpawnPoint):
            editor.spawn_points_count -= 1
        editor.rects.remove(editor.rects.sprites()[editor.selected_rect])
        editor.selected_rect = -1
    if event.key == config['ed_panel'] and editor.mode == MODE.Editor and editor.selected_rect != -1:
        if editor.property_panel:
            editor.property_panel.destroy(editor.ui_to_draw)
            editor.property_panel = None
        else:
            editor.property_panel = PropertyPanel(*mouse_position,
                                                editor.rects.sprites()[editor.selected_rect].get_properties(),
                                                editor.ui_to_draw, editor.rects.sprites()[editor.selected_rect])
            if "ColorPicker" in editor.property_panel.properties_obj:
                editor.property_panel.set_color(editor.rects.sprites()[editor.selected_rect].color)
    if event.key == config['ed_wall']:
        editor.wall_button.callback(editor.wall_button, editor.wall_button.args)
    if event.key == config['ed_door']:
        editor.door_button.callback(editor.door_button, editor.door_button.args)
    if event.key == config['ed_spawn']:
        editor.spawn_button.callback(editor.spawn_button, editor.spawn_button.args)
    if event.key == config['ed_plate']:
        editor.plate_button.callback(editor.plate_button, editor.plate_button.args)
    if event.key == config['ed_goal']:
        editor.goal_button.callback(editor.goal_button, editor.goal_button.args)
    if event.key == K_s and event.mod & KMOD_LALT:
        editor.save_to_file(None, None)
    if event.key == config['ed_reload']:
        editor.selected_rect = -1
        editor.load_map(editor.map_path)
    if event.key == config['ed_camera_reset']:
        editor.camera.reset()

def update_mode(editor):
    editor.selected_rect = -1
    if editor.mode == MODE.Camera:
        editor.mode_text = MODE_TEXT.render("Camera", 1, (255,255,255))
    if editor.mode == MODE.Editor:
        editor.mode_text = MODE_TEXT.render("Editor", 1, (255,255,255))
    editor.rect_started = False
    editor.camera.mouse_moving = False


def move_rect(editor, mouse_position):
    r = editor.rects.sprites()[editor.selected_rect]
    mp = editor.camera.screen_to_world(mouse_position)
    if isinstance(r, SpawnPoint):
        if editor.property_panel_recently_closed:
            return
        r.move(mp)
        r.points = r.get_points()
    else:
        if editor.drag_start:
            constraint = ""
            if editor.selected_arrow: constraint = editor.selected_arrow
            if pygame.key.get_mods() & pygame.KMOD_LALT: constraint = 'snapping'
            r.move(mp, editor.drag_start, constraint, *(editor.grid_sizes))
        else:
            editor.selected_rect = -1

def start_resize(editor, mouse_position):
    r = editor.rects.sprites()[editor.selected_rect]
    if not r.resizable: return

    selected_arrow = editor.check_arrow(mouse_position)
    if selected_arrow != "":
        editor.selected_arrow = selected_arrow
        editor.resizing = True
        return

    if pygame.key.get_mods() & pygame.KMOD_LALT:
        editor.selected_arrow = 'snapping'
        editor.resizing = True

    mouse_position = editor.camera.screen_to_world(mouse_position)
    corner = get_corner_point(r.org_rect, mouse_position)

    if corner != None:
        editor.resizing = True
        rect_corners = [r.org_rect.topleft, r.org_rect.topright, r.org_rect.bottomleft, r.org_rect.bottomright]

        if editor.fixed_point == None:
            moving_corner = rect_corners[corner]
            editor.moving_offset = (mouse_position[0] - moving_corner[0], mouse_position[1] - moving_corner[1])

            opposed_corner_id = {0:3, 3:0, 1:2, 2:1}[corner]
            editor.fixed_point = rect_corners[opposed_corner_id]


def on_resize_rect(editor, mouse_position):
    """
    Resize the selected rect

    :param editor: the editor object
    :param mouse_position: mouse's position in screen coordinates
    :type editor: Editor
    :type mouse_position: (int,int)
    :rtype: None
    """
    if editor.selected_arrow == 'snapping':
        resize_to_grid(editor, mouse_position)
    if editor.selected_arrow != "":
        resize_arrow(editor, editor.selected_arrow)
        return

    r = editor.rects.sprites()[editor.selected_rect]
    mouse_position = editor.camera.screen_to_world(mouse_position)
    pos = (mouse_position[0] - editor.moving_offset[0], mouse_position[1] - editor.moving_offset[1])
    size = (editor.fixed_point[0] - mouse_position[0] + editor.moving_offset[0],
            editor.fixed_point[1] - mouse_position[1] + editor.moving_offset[1])

    new_rect = pygame.Rect(pos, size)
    new_rect.normalize()
    AREA_LIMIT = 2000
    if new_rect.w > 30 and new_rect.h > 30:
        r.org_rect = new_rect

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

def resize_to_grid(editor, mouse_position):
    r = editor.rects.sprites()[editor.selected_rect]
    mouse_position = editor.camera.screen_to_world(mouse_position)
    mouse_x_cell = mouse_position[0] // editor.grid_sizes[0] 
    mouse_y_cell = mouse_position[1] // editor.grid_sizes[1]
    fixed_x_cell = editor.fixed_point[0] // editor.grid_sizes[0]
    fixed_y_cell = editor.fixed_point[1] // editor.grid_sizes[1]

    delta_x = fixed_x_cell - mouse_x_cell
    delta_y = fixed_y_cell - mouse_y_cell

    mouse_x_cell += delta_x < 0
    delta_x -= delta_x < 0 

    mouse_y_cell += delta_y < 0
    delta_y -= delta_y < 0


    pos  = (mouse_x_cell * editor.grid_sizes[0], mouse_y_cell * editor.grid_sizes[1])
    size = (delta_x * editor.grid_sizes[0], delta_y * editor.grid_sizes[1])

    new_rect = pygame.Rect(pos, size)
    new_rect.normalize()
    if new_rect.w >= 30 and new_rect.h >= 30:
        r.org_rect = new_rect