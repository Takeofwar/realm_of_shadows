"""
helpers.py — Helper functions and lambdas for Realm of Shadows.

Contains utility functions used across multiple modules,
including lambda expressions for concise operations.
"""

import random



# calculating effective damage
calculate_damage = lambda attack, defense: max(1, attack - defense)

# sorting items by their value (descending)
sort_by_value = lambda items: sorted(items, key=lambda item: item.value, reverse=True)

# sorting items by their power/damage (descending)
sort_by_power = lambda items: sorted(items, key=lambda item: item.power, reverse=True)

# formatting gold display
format_gold = lambda amount: f"{amount} gold coin{'s' if amount != 1 else ''}"



def roll_dice(sides=20):
    """Simulate rolling a dice with the given number of sides.

    Args:
        sides: Number of sides on the dice (default 20 for D20).

    Returns:
        A random integer between 1 and sides (inclusive).
    """
    return random.randint(1, sides)


def critical_hit_check(roll, threshold=18):
    """Check if a dice roll results in a critical hit.

    Args:
        roll: The dice roll result.
        threshold: Minimum roll for a critical hit (default 18).

    Returns:
        True if the roll is a critical hit, False otherwise.
    """
    return roll >= threshold


def calculate_xp_for_level(level):
    """Calculate XP needed to reach the next level.

    Uses a quadratic scaling formula so each level requires
    progressively more XP.

    Args:
        level: The current level of the player.

    Returns:
        XP required to reach the next level.
    """
    return 50 * (level ** 2) + 50


def generate_loot_gold(enemy_gold, player_level):
    """Generate a randomized gold reward based on enemy gold and player level.

    Args:
        enemy_gold: Base gold amount the enemy drops.
        player_level: Current player level (affects bonus).

    Returns:
        Total gold dropped.
    """
    bonus = random.randint(0, player_level * 2)
    return enemy_gold + bonus


def clear_screen_text():
    """Return a visual separator for the terminal to simulate clearing."""
    return "\n" + "=" * 50 + "\n"


def hp_bar(current_hp, max_hp, bar_length=20):
    """Generate a text-based HP bar.

    Args:
        current_hp: Current hit points.
        max_hp: Maximum hit points.
        bar_length: Length of the bar in characters.

    Returns:
        A formatted string like: [████████░░░░] 80/100 HP
    """
    if max_hp <= 0:
        return "[" + "." * bar_length + "] 0/0 HP"

    ratio = max(0, current_hp) / max_hp
    filled = int(bar_length * ratio)
    empty = bar_length - filled

    
    if ratio > 0.6:
        indicator = "#"
    elif ratio > 0.3:
        indicator = "="
    else:
        indicator = "-"

    bar = indicator * filled + "." * empty
    return f"[{bar}] {max(0, current_hp)}/{max_hp} HP"
