"""
exceptions.py — Custom exception classes for Realm of Shadows.

Defines a hierarchy of game-specific exceptions with meaningful
error messages to provide clear feedback to the player.
"""


class GameError(Exception):
    """Base exception for all game-related errors."""

    def __init__(self, message="An unexpected game error occurred."):
        self.message = message
        super().__init__(self.message)


class PlayerDeadError(GameError):
    """Raised when a dead player attempts an action that requires being alive."""

    def __init__(self, action="perform this action"):
        self.message = (
            f"Your character has fallen in battle and cannot {action}. "
            f"Start a new game or load a previous save."
        )
        super().__init__(self.message)


class InvalidCommandError(GameError):
    """Raised when the player enters a command that cannot be parsed."""

    def __init__(self, command=""):
        self.message = (
            f"Unknown command: '{command}'. Type 'help' to see available commands."
        )
        super().__init__(self.message)


class InsufficientGoldError(GameError):
    """Raised when the player does not have enough gold for a purchase."""

    def __init__(self, required, available):
        self.message = (
            f"Not enough gold! You need {required} gold but only have {available}."
        )
        super().__init__(self.message)


class SaveLoadError(GameError):
    """Raised when saving or loading a game fails."""

    def __init__(self, operation="save", reason="unknown error"):
        self.message = (
            f"Failed to {operation} the game: {reason}. "
            f"Please check your saves/ directory."
        )
        super().__init__(self.message)


class InvalidTargetError(GameError):
    """Raised when the player targets something that doesn't exist."""

    def __init__(self, target_name=""):
        self.message = f"There is no '{target_name}' here to interact with."
        super().__init__(self.message)
