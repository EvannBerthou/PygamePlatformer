import os
import json

from pygame.locals import *

def save_config(config):
    with open('config', 'w') as f:
        f.write(json.dumps(config))


def get_default_config():
    return {"fullscreen": 0, "resolution": "1152x648",
            "p1_left": K_q, "p1_right": K_d, "p1_jump": K_SPACE, 
            "p2_left": K_LEFT, "p2_right": K_RIGHT, "p2_jump": K_UP, 
            "ed_mode": K_TAB, "ed_clear": K_r, "ed_reload": K_l, 
            "ed_delete": K_DELETE, "ed_camera_reset": K_f,
            "ed_wall": K_F1, "ed_door": K_F2, "ed_spawn": K_F3, "ed_plate": K_F4, "ed_goal": K_F5,
            "fps_counter": False
    }

def load_config():
    if not os.path.exists('config'):
        with open('config', 'w') as f:
            f.write(json.dumps(get_default_config()))

    with open('config', 'r') as f:
        config_text = f.read()
        return json.loads(config_text)
