"""
decorators.py — Custom decorators for Realm of Shadows.

Provides reusable decorators for common game logic such as
checking player status and logging game actions.
"""

import functools
from datetime import datetime

from utils.exceptions import PlayerDeadError


def requires_alive(func):
    """Decorator that ensures the player is alive before executing an action.

    The first argument of the decorated function must be a Player instance
    (or any object with an `is_alive()` method).

    Raises:
        PlayerDeadError: If the player's HP is 0 or below.
    """

    @functools.wraps(func)
    def wrapper(player, *args, **kwargs):
        if not player.is_alive():
            raise PlayerDeadError(func.__name__)
        return func(player, *args, **kwargs)

    return wrapper


def log_action(filepath="game.log"):
    """Decorator factory that logs function calls to a file.

    Uses a context manager (with statement) to write timestamped
    log entries for each decorated function call.

    Args:
        filepath: Path to the log file (default: 'game.log').
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] Action: {func.__name__}\n"
            with open(filepath, "a", encoding="utf-8") as log_file:
                log_file.write(log_entry)
            return result

        return wrapper

    return decorator
