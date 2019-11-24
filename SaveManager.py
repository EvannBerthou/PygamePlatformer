import os
from Wall import Wall
from Door import Door
from SpawnPoint import SpawnPoint

def save_to_file(rects, file_path = 'map'):
    with open(file_path, 'w') as f:
        f.write('name : FOO\n')
        f.write('author : BAR\n')
        f.write('map:\n')
        for obj in rects:
            string = obj.as_string()
            f.write(string)
        f.write('endmap\n')

def obj_from_str(string):
    objs = {
        "Wall": Wall,
        "Door": Door,
        "Spawn": SpawnPoint
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
