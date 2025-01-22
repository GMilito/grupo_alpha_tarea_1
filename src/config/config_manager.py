import json
import os

class ConfigurationManager:
    CONFIG_FILE = "config.json"

    @staticmethod
    def load_config():
        """Carga la configuración desde el archivo config.json."""
        if not os.path.exists(ConfigurationManager.CONFIG_FILE):
            return {"sync_folder": ""}
        with open(ConfigurationManager.CONFIG_FILE, "r") as file:
            return json.load(file)

    @staticmethod
    def save_config(config):
        """Guarda la configuración en el archivo config.json."""
        with open(ConfigurationManager.CONFIG_FILE, "w") as file:
            json.dump(config, file, indent=4)
