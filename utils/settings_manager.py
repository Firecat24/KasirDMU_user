import os
import json

DEFAULT_SETTINGS = {
    "pembulatan": 500
}

class SettingsManager:
    def __init__(self, settings_path):
        self._path = settings_path
        self.settings = {}
        self.created_new = False
        self.load()

    def load(self):
        if os.path.exists(self._path):
            with open(self._path, "r") as f:
                data = json.load(f)
                self.settings = {**DEFAULT_SETTINGS, **data}
        else:
            self.settings = DEFAULT_SETTINGS.copy()
            self.created_new = True

    def save(self):
        os.makedirs(os.path.dirname(self._path), exist_ok=True)
        with open(self._path, "w") as f:
            json.dump(self.settings, f, indent=4)

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save()