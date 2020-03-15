import json
import sys

class ReplayManager:
    def __init__(self, replay_path):
        with open (replay_path, 'r') as f:
            self.replay_data = json.loads(f.read())

        self.new_action = True
        self.action_id = -1
        self.get_next_action()

    def get_next_action(self):
        self.action_id += 1
        if self.action_id >= len(self.replay_data):
            print('replay ended')
            exit(0)
        self.next_action = self.replay_data[str(self.action_id)]

    def get_action(self, players):
        if self.new_action:
            next_action = self.next_action.copy()
            self.get_next_action()
            return next_action

        return None
