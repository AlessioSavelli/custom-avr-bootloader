import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

def save_selected_com(port):
    """Save the selected COM port to a configuration file."""
    config = {"selected_com": port}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def load_selected_com():
    """Load the saved COM port from the configuration file."""
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("selected_com", None)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
