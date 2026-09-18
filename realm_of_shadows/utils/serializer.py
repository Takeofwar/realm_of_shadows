"""
serializer.py — Save and Load system for Realm of Shadows.

Handles game state serialization to/from JSON files using
context managers (with statement) and proper error handling.
"""

import json
import os
from datetime import datetime

from utils.exceptions import SaveLoadError


# Default saves directory
SAVES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "saves")


def ensure_saves_dir():
    """Create the saves directory if it doesn't exist."""
    if not os.path.exists(SAVES_DIR):
        os.makedirs(SAVES_DIR)


def save_game(player, dungeon, slot_name="autosave"):
    """Save the current game state to a JSON file.

    Uses a context manager (with open) and JSON serialization.

    Args:
        player: The Player object to save.
        dungeon: The Dungeon object to save.
        slot_name: Name for the save file (default: 'autosave').

    Returns:
        The filepath where the game was saved.

    Raises:
        SaveLoadError: If saving fails for any reason.
    """
    try:
        ensure_saves_dir()
        filepath = os.path.join(SAVES_DIR, f"{slot_name}.json")

        game_data = {
            "save_info": {
                "slot_name": slot_name,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "player_name": player.name,
                "player_level": player.level,
            },
            "player": player.to_dict(),
            "dungeon": dungeon.to_dict(),
        }

        
        with open(filepath, "w", encoding="utf-8") as save_file:
            json.dump(game_data, save_file, indent=2, ensure_ascii=False)

        return filepath

    except PermissionError:
        raise SaveLoadError("save", "permission denied — cannot write to saves directory")
    except OSError as e:
        raise SaveLoadError("save", str(e))


def load_game(slot_name="autosave"):
    """Load a game state from a JSON file.

    Uses a context manager (with open) and JSON deserialization.

    Args:
        slot_name: Name of the save file to load (default: 'autosave').

    Returns:
        A tuple of (player_data: dict, dungeon_data: dict).

    Raises:
        SaveLoadError: If the save file doesn't exist or is corrupted.
    """
    filepath = os.path.join(SAVES_DIR, f"{slot_name}.json")

    if not os.path.exists(filepath):
        raise SaveLoadError("load", f"save file '{slot_name}' not found")

    try:
        with open(filepath, "r", encoding="utf-8") as save_file:
            game_data = json.load(save_file)

        if "player" not in game_data or "dungeon" not in game_data:
            raise SaveLoadError("load", "save file is corrupted or incomplete")

        return game_data["player"], game_data["dungeon"]

    except json.JSONDecodeError:
        raise SaveLoadError("load", "save file contains invalid JSON data")
    except PermissionError:
        raise SaveLoadError("load", "permission denied — cannot read save file")
    except OSError as e:
        raise SaveLoadError("load", str(e))


def list_saves():
    """List all available save files.

    Uses a list comprehension to filter JSON files in the saves directory.

    Returns:
        A list of dictionaries with save information.
    """
    ensure_saves_dir()

    save_files = [
        f[:-5] for f in os.listdir(SAVES_DIR)
        if f.endswith(".json")
    ]

    saves_info = []
    for slot in save_files:
        try:
            filepath = os.path.join(SAVES_DIR, f"{slot}.json")
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                info = data.get("save_info", {})
                saves_info.append({
                    "slot": slot,
                    "player_name": info.get("player_name", "Unknown"),
                    "level": info.get("player_level", 0),
                    "timestamp": info.get("timestamp", "Unknown"),
                })
        except (json.JSONDecodeError, OSError):
            saves_info.append({
                "slot": slot,
                "player_name": "Corrupted",
                "level": 0,
                "timestamp": "Unknown",
            })

    return saves_info


def delete_save(slot_name):
    """Delete a save file.

    Args:
        slot_name: Name of the save file to delete.

    Raises:
        SaveLoadError: If the file doesn't exist or can't be deleted.
    """
    filepath = os.path.join(SAVES_DIR, f"{slot_name}.json")

    if not os.path.exists(filepath):
        raise SaveLoadError("delete", f"save file '{slot_name}' not found")

    try:
        os.remove(filepath)
    except OSError as e:
        raise SaveLoadError("delete", str(e))
