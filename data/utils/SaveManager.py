import os
from data.GameObjects import *

def save_to_file(rects, file_path = 'map'):

    spawn_points = []
    for obj in rects:
        if type(obj) == SpawnPoint:
            if spawn_points: #if there is already a spawn point in the list
                if spawn_points[0].player_id == obj.player_id: #if the spawn point in the list has the same player_id
                    return "Both spawn points have the same player_id"
            spawn_points.append(obj)
    if len(spawn_points) < 2:
        return "Missing {} spawn point(s)".format(2 - len(spawn_points))


    with open(file_path, 'w') as f:
        f.write('name : FOO\n')
        f.write('author : BAR\n')
        f.write('map:\n')
        for obj in rects:
            if hasattr(obj, 'as_string'):
                string = obj.as_string()
                f.write(string)
        f.write('endmap\n')
    return "map saved"

def obj_from_str(string):
    objs = {
        "Wall": Wall,
        "Door": Door,
        "Spawn": SpawnPoint,
        "Plate": Plate,
        "Goal":  EndGoal
    }
    return objs[string]

def create_obj(obj, args):
    if obj == Wall:
        pos = []
        color = []
        for v in args[:4]:
            pos.append(int(v))
        for v in args[4:]:
            color.append(int(v))

        return Wall(*pos, color)

    if obj == Door:
        pos = []
        for v in args[:4]:
            pos.append(int(v))

        return Door(*pos, 0, int(args[4]))
    if obj == SpawnPoint:
        pos = []
        for v in args[:2]:
            pos.append(int(v))
        return SpawnPoint(*pos, 50, (255,255,255), int(args[2]))

    if obj == Plate:
        pos = []
        for v in args[:4]:
            pos.append(int(v))
        return Plate(*pos, (255,255,255), int(args[4]))
    if obj == EndGoal:
        pos = []
        for v in args[:4]:
            pos.append(int(v))
        return EndGoal(*pos)

def load_map(file_name = 'map'):
    print('Loading map')
    if not os.path.exists(file_name):
        print(f'No file named : {file_name}')
        return

    rects = []
    in_map = False
    with open('map', 'r') as f:
        for l in f:
            if l == "endmap\n":
                in_map = False

            if in_map:
                parts = l.strip().split(',')
                obj = obj_from_str(parts[0])
                rects.append(create_obj(obj, parts[1:]))

            if l == "map:\n":
                in_map = True
    print('Map loaded')
    return rects
