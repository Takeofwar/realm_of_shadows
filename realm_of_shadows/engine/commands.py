"""
commands.py — Command parser for Realm of Shadows.

Uses regular expressions to parse and validate player input,
mapping text commands to game actions.
"""

import re

from utils.exceptions import InvalidCommandError



COMMAND_PATTERN = re.compile(
    r"^\s*(look|go|attack|use|take|equip|cast|inventory|inv|stats|"
    r"save|load|help|quit|exit|buy|sell|pass|map)\s*(.*?)\s*$",
    re.IGNORECASE,
)


NAME_PATTERN = re.compile(r"^[A-Za-z]{2,20}$")


DIRECTION_PATTERN = re.compile(r"^(north|south|east|west|n|s|e|w)$", re.IGNORECASE)


DIRECTION_MAP = {"n": "north", "s": "south", "e": "east", "w": "west"}


def parse_command(raw_input):
    """Parse raw player input into a (command, argument) tuple.

    Uses regex matching to extract the command verb and optional argument.

    Args:
        raw_input: The raw string typed by the player.

    Returns:
        A tuple of (command: str, argument: str).

    Raises:
        InvalidCommandError: If the input doesn't match any known command.
    """
    if not raw_input or not raw_input.strip():
        raise InvalidCommandError("")

    match = COMMAND_PATTERN.match(raw_input)
    if not match:
        raise InvalidCommandError(raw_input.strip())

    command = match.group(1).lower()
    argument = match.group(2).strip() if match.group(2) else ""

    
    if command == "inv":
        command = "inventory"
    if command in ("quit", "exit"):
        command = "quit"

    return command, argument


def validate_name(name):
    """Validate a player name using regex.

    Args:
        name: The name string to validate.

    Returns:
        True if the name is valid, False otherwise.
    """
    return bool(NAME_PATTERN.match(name))


def resolve_direction(direction_str):
    """Resolve a direction string, expanding abbreviations.

    Args:
        direction_str: Direction input (e.g., 'n', 'north').

    Returns:
        The full direction string (e.g., 'north'), or None if invalid.
    """
    direction_str = direction_str.lower().strip()

    if not DIRECTION_PATTERN.match(direction_str):
        return None

    
    return DIRECTION_MAP.get(direction_str, direction_str)


def get_help_text():
    """Return a formatted help text listing all available commands."""
    commands = {
        "look": "Examine your current surroundings",
        "go <direction>": "Move in a direction (north/south/east/west or n/s/e/w)",
        "attack": "Initiate combat with enemies in the room",
        "use <item>": "Use a potion from your inventory",
        "take <item>": "Pick up an item from the ground",
        "equip <weapon>": "Equip a weapon from your inventory",
        "cast <spell>": "Cast a spell during combat",
        "sell <item>": "Sell an item from your inventory (at merchant)",
        "inventory": "View your inventory (shortcut: inv)",
        "stats": "View your character's stats",
        "map": "Show a simple map of visited rooms",
        "save": "Save your current progress",
        "load": "Load a previously saved game",
        "help": "Show this help message",
        "quit": "Exit the game",
    }

    lines = [
        "+=============================================+",
        "|           AVAILABLE COMMANDS                |",
        "+=============================================+",
    ]

    for cmd, desc in commands.items():
        lines.append(f"|  {cmd:<18} -- {desc:<24}|")

    lines.append("+=============================================+")
    return "\n".join(lines)
