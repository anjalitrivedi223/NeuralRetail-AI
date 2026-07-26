import os
import yaml

class ConfigLoader:
    def __init__(self, config_path="config/config.yaml"):
        self.config_path = config_path
        self.config_data = self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found at {self.config_path}")
        
        with open(self.config_path, "r") as file:
            try:
                return yaml.safe_load(file)
            except yaml.YAMLError as exc:
                raise RuntimeError(f"Error parsing YAML file: {exc}")

    def get(self, key_path, default=None):
        """
        Keys ko nested way me easily access karne ke liye (e.g., 'database.user')
        """
        keys = key_path.split(".")
        value = self.config_data
        try:
            for key in keys:
                value = value[key]
            return value
        except KeyError:
            return default

# Testing logic
if __name__ == "__main__":
    loader = ConfigLoader()
    print("🚀 Project Name:", loader.get("project.name"))
    print("📦 Database User:", loader.get("database.user"))