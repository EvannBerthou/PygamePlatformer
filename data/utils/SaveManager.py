import os

def save_to_file(rects, file_path, name, author, dialogues, player_size):
    from data.GameObjects.SpawnPoint import SpawnPoint
    spawn_points = []
    for obj in rects:
        if type(obj) == SpawnPoint:
            if spawn_points: #if there is already a spawn point in the list
                if spawn_points[0].player_id == obj.player_id: #if the spawn point in the list has the same player_id
                    return "Both spawn points have the same player_id"
            spawn_points.append(obj)
    if len(spawn_points) < 2:
        return "Missing {} spawn point(s)".format(2 - len(spawn_points))
    if player_size < 32:
        player_size = 32

    with open(file_path, 'w') as f:
        f.write(f'name:{name}\n')
        f.write(f'author:{author}\n')
        f.write(f'player_size:{player_size}\n')
        f.write('map:\n')
        for obj in rects:
            if hasattr(obj, 'as_string'):
                string = obj.as_string()
                f.write(string)
        f.write('endmap\n')
        f.write('dialogues:\n')
        for dialogue in dialogues:
            f.write(f'{dialogue[0]},{dialogue[1]}\n')
        f.write('enddialogues\n')
    return "map saved"

def obj_from_str(string):
    import data.GameObjects as go
    objs = {
        "Wall": go.Wall,
        "Door": go.Door,
        "Spawn": go.SpawnPoint,
        "Plate": go.Plate,
        "Goal":  go.EndGoal
    }
    return objs[string]

def create_obj(obj, args):
    import data.GameObjects as go
    if obj == go.Wall:
        pos = []
        color = []
        for v in args[:4]:
            pos.append(int(v))
        for v in args[4:]:
            color.append(int(v))

        return go.Wall(*pos, color)

    if obj == go.Door:
        pos = []
        for v in args[:4]:
            pos.append(int(v))

        return go.Door(*pos, 0, int(args[4]))
    if obj == go.SpawnPoint:
        pos = []
        for v in args[:2]:
            pos.append(int(v))
        return go.SpawnPoint(*pos, 50, (255,255,255), int(args[2]))

    if obj == go.Plate:
        pos = []
        for v in args[:4]:
            pos.append(int(v))
        return go.Plate(*pos, (255,255,255), int(args[4]))
    if obj == go.EndGoal:
        pos = []
        for v in args[:4]:
            pos.append(int(v))
        return go.EndGoal(*pos)

def load_map(file_name):
    print('Loading map')
    if not os.path.exists(file_name) or not os.path.isfile(file_name):
        print(f'No file named : {file_name}, creating one')
        return {'rects': [], 'name': '', 'author': '', 'dialogues': [], 'player_size': 64}

    rects = []
    dialogues = []
    in_map = False
    in_dialogue = False
    name = ""
    author = ""
    with open(file_name, 'r') as f:
        for l in f:
            if l == "endmap\n":
                in_map = False

            if l == "enddialogues\n":
                in_dialogue = False

            if l.startswith('name'):
                name = "".join(l.split(':')[1:]).strip('\n')

            if l.startswith('author'):
                author = "".join(l.split(':')[1:]).strip('\n')
            
            if l.startswith('player_size'):
                player_size = int("".join(l.split(':')[1:]).strip('\n'))
                if player_size < 32: player_size = 32

            if in_map:
                parts = l.strip().split(',')
                obj = obj_from_str(parts[0])
                rects.append(create_obj(obj, parts[1:]))

            if in_dialogue:
                parts = l.strip().split(',')
                player = parts[0]
                text = ",".join(parts[1:])
                dialogues.append([player, text])

            if l == "map:\n":
                in_map = True

            if l == "dialogues:\n":
                in_dialogue = True
    print('Map loaded')
    return {"rects": rects, "name": name,"author": author, "dialogues": dialogues, 'player_size': player_size}
