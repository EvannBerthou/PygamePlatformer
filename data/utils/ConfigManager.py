import os
import json

def save_config(config):
    with open('config', 'w') as f:
        f.write(json.dumps(config))


def get_default_config():
    return {"fullscreen": 0, "resolution": "1152x648",
            "p1_left": 113, "p1_right": 100, "p1_jump": 32, #K_q, K_d, K_SPACE
            "p2_left": 1073741904, "p2_right": 1073741903, "p2_jump": 1073741906 #K_LEFT, K_RIGHT, K_UP
    }

def load_config():
    if not os.path.exists('config'):
        with open('config', 'w') as f:
            f.write(json.dumps(get_default_config()))

    with open('config', 'r') as f:
        config_text = f.read()
        return json.loads(config_text)
