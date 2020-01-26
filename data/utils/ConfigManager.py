import os
import json

def save_config(config):
    with open('config', 'w') as f:
        f.write(json.dumps(config))


def get_default_config():
    return {"fullscreen": 0, "resolution": "1152x648"}

def load_config():
    if not os.path.exists('config'):
        with open('config', 'w') as f:
            f.write(json.dumps(get_default_config()))

    with open('config', 'r') as f:
        config_text = f.read()
        return json.loads(config_text)
