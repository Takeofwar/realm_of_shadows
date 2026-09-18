"""
combat.py — Combat system for Realm of Shadows.

Implements turn-based combat between the player and enemies.
Uses decorators, control statements, and helper functions.
"""

import random

from utils.decorators import requires_alive, log_action
from utils.helpers import calculate_damage, roll_dice, critical_hit_check, hp_bar
from models.items import Spell


@log_action()
def start_combat(player, enemies):
    """Run a full turn-based combat encounter.

    The player fights a list of enemies in turns. Each turn, the player
    can attack, use a potion, cast a spell, or attempt to flee.

    Args:
        player: The Player object.
        enemies: List of Enemy objects to fight.

    Returns:
        True if the player wins, False if the player dies or flees.
    """
    
    alive_enemies = [e for e in enemies if e.is_alive()]

    if not alive_enemies:
        print("  There are no enemies to fight here.")
        return True

    print("\n<*>==========================================<*>")
    print("              <*> COMBAT BEGINS! <*>")
    print("<*>==========================================<*>")

    enemy_names = ", ".join(e.name for e in alive_enemies)
    print(f"  Enemies: {enemy_names}\n")

    round_number = 0

    
    while player.is_alive() and any(e.is_alive() for e in alive_enemies):
        round_number += 1
        print(f"\n-- Round {round_number} --")
        print(f"  You: {hp_bar(player.hp, player.max_hp)}  Mana: {player.mana}/{player.max_mana}")

        for enemy in alive_enemies:
            if enemy.is_alive():
                print(f"  {enemy}")

        
        result = player_turn(player, alive_enemies)

        if result == "fled":
            print("  You flee from battle!")
            return False
        elif result == "error":
            continue

       
        alive_enemies = [e for e in alive_enemies if e.is_alive()]

        if not alive_enemies:
            break

       
        for enemy in alive_enemies:
            if enemy.is_alive() and player.is_alive():
                enemy_turn(enemy, player)

   
    if player.is_alive():
        print("\n  ** VICTORY! You defeated all enemies!")
        return True
    else:
        print("\n  xx DEFEAT! You have been slain...")
        return False


def player_turn(player, enemies):
    """Handle the player's combat turn.

    Args:
        player: The Player object.
        enemies: List of alive Enemy objects.

    Returns:
        'ok' on success, 'fled' if player flees, 'error' on invalid input.
    """
    print("\n  Choose action: [attack] [use <item>] [cast <spell>] [flee]")

    try:
        action = input("  > ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return "fled"

    if not action:
        print("  Please enter an action.")
        return "error"

    
    if action == "attack":
        return perform_attack(player, enemies)

    
    elif action.startswith("use "):
        item_name = action[4:].strip()
        if not item_name:
            print("  Usage: use <item name>")
            return "error"
        msg = player.use_potion(item_name)
        print(f"  {msg}")
        return "ok"

   
    elif action.startswith("cast "):
        spell_name = action[5:].strip()
        return perform_cast(player, enemies, spell_name)

    
    elif action == "flee":
        if random.random() < 0.4:
            return "fled"
        else:
            print("  Failed to flee! The enemies block your escape.")
            return "ok"

    else:
        print("  Invalid combat action. Try: attack, use <item>, cast <spell>, or flee")
        return "error"


@requires_alive
def perform_attack(player, enemies):
    """Execute a physical attack against the first alive enemy.

    Decorated with @requires_alive to ensure the player is alive.

    Args:
        player: The Player object.
        enemies: List of Enemy objects.

    Returns:
        'ok' on success.
    """
    
    target = None
    for enemy in enemies:
        if enemy.is_alive():
            target = enemy
            break

    if target is None:
        print("  No enemies to attack!")
        return "ok"

   
    roll = roll_dice(20)
    is_critical = critical_hit_check(roll)

    total_attack = player.get_total_attack()

    if is_critical:

        damage = calculate_damage(total_attack * 2, target.defense)
        actual = target.take_damage(damage + target.defense)  # Bypass defense on crit
        print(f"  !! CRITICAL HIT! You strike {target.name} for {actual} damage!")
    elif roll >= 5:

        damage = calculate_damage(total_attack, target.defense)
        actual = target.take_damage(damage + target.defense)
        print(f"  >> You attack {target.name} for {actual} damage.")
    else:

        print(f"  -- Your attack misses {target.name}!")

    if not target.is_alive():
        print(f"  xx {target.name} has been defeated!")

    return "ok"


@requires_alive
def perform_cast(player, enemies, spell_name):
    """Cast a spell from inventory at the first alive enemy.

    Args:
        player: The Player object.
        enemies: List of Enemy objects.
        spell_name: Name of the spell to cast.

    Returns:
        'ok' on success, 'error' on failure.
    """
    item = player.find_item(spell_name)

    if item is None:
        print(f"  You don't have a spell called '{spell_name}'.")
        return "error"

    if not isinstance(item, Spell):
        print(f"  '{item.name}' is not a spell.")
        return "error"

    
    if not player.use_mana(item.mana_cost):
        print(f"  Not enough mana! Need {item.mana_cost}, have {player.mana}.")
        return "error"

    
    target = None
    for enemy in enemies:
        if enemy.is_alive():
            target = enemy
            break

    if target is None:
        print("  No enemies to cast on!")
        return "error"

    damage = calculate_damage(item.power, target.defense)
    actual = target.take_damage(damage + target.defense)
    print(f"  ** You cast {item.name} on {target.name} for {actual} damage! (Mana: {player.mana}/{player.max_mana})")

    if not target.is_alive():
        print(f"  xx {target.name} has been defeated!")

    return "ok"


def enemy_turn(enemy, player):
    """Handle a single enemy's attack turn.

    Args:
        enemy: The attacking Enemy object.
        player: The defending Player object.
    """
    roll = roll_dice(20)

    if roll >= 5:
        damage = calculate_damage(enemy.attack, player.defense)
        actual = player.take_damage(damage + player.defense)

        if critical_hit_check(roll):
            extra = calculate_damage(enemy.attack, player.defense)
            extra_actual = player.take_damage(extra + player.defense)
            actual += extra_actual
            print(f"  !! {enemy.name} lands a critical hit for {actual} total damage!")
        else:
            print(f"  >> {enemy.name} attacks you for {actual} damage.")
    else:
        print(f"  -- {enemy.name}'s attack misses!")

    if not player.is_alive():
        print(f"\n  xx You have been slain by {enemy.name}...")
