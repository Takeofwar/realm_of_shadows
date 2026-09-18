"""
main.py -- Entry point for Realm of Shadows.

A text-based dungeon crawler RPG written in Python.
Run this file to start the game.
"""

import io
import sys

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

import json
import os
import random

from models.character import Player, Enemy
from models.room import Dungeon, build_dungeon
from models.items import Item, Potion, Spell, Weapon
from engine.commands import parse_command, validate_name, resolve_direction, get_help_text
from engine.combat import start_combat
from engine.events import event_generator, handle_event
from utils.serializer import save_game, load_game, list_saves
from utils.exceptions import (
    GameError,
    InvalidCommandError,
    InsufficientGoldError,
    PlayerDeadError,
    SaveLoadError,
)
from utils.helpers import (
    format_gold,
    generate_loot_gold,
    hp_bar,
    sort_by_value,
)



DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ENEMIES_FILE = os.path.join(DATA_DIR, "enemies.json")

TITLE_ART = """
+===================================================+
|                                                   |
|   #####   ######   ####  ##     ##   ##  ##       |
|   ##  ##  ##      ##  ## ##     ### ###  ##       |
|   #####   #####   ###### ##     ## # ##  ##       |
|   ##  ##  ##      ##  ## ##     ##   ##           |
|   ##  ##  ######  ##  ## #####  ##   ##  ##       |
|                                                   |
|           <*> OF SHADOWS <*>                      |
|                                                   |
|        A Text-Based Dungeon Crawler RPG           |
|                                                   |
+===================================================+
"""



def load_enemy_data():
    """Load enemy definitions from JSON file.

    Uses context manager (with) and JSON deserialization.

    Returns:
        A list of enemy dictionaries.

    Raises:
        SystemExit: If the enemy data file cannot be loaded.
    """
    try:
        with open(ENEMIES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"ERROR: Enemy data file not found at {ENEMIES_FILE}")
        print("Make sure the 'data/enemies.json' file exists.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"ERROR: Enemy data file is corrupted.")
        sys.exit(1)


# Main Menu
def show_main_menu():
    """Display the main menu and return the player's choice."""
    print(TITLE_ART)
    print("  1. New Game")
    print("  2. Load Game")
    print("  3. Quit")
    print()

    while True:
        try:
            choice = input("  Select an option (1-3): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye, adventurer!")
            sys.exit(0)

        if choice in ("1", "2", "3"):
            return choice
        print("  Invalid option. Please enter 1, 2, or 3.")


def create_new_player():
    """Prompt the player to create a new character.

    Uses regex validation for the character name.

    Returns:
        A new Player object.
    """
    print("\n+======================================+")
    print("|       <*> CREATE YOUR CHARACTER <*>   |")
    print("+======================================+\n")

    while True:
        try:
            name = input("  Enter your character's name (2-20 letters): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Exiting...")
            sys.exit(0)

        if validate_name(name):
            break
        print("  Invalid name! Use only letters (A-Z), 2-20 characters.")

    player = Player(name)
    # starting equipment
    starting_sword = Weapon("Wooden Sword", "A simple training sword.", value=5, power=3)
    starting_potion = Potion("Small Potion", "A small vial of red liquid.", value=5, heal_amount=20)

    player.equipped_weapon = starting_sword
    player.add_to_inventory(starting_potion)
    player.add_to_inventory(Potion("Small Potion", "A small vial of red liquid.", value=5, heal_amount=20))

    print(f"\n  Welcome, {name}! Your adventure begins now...")
    print(f"  Starting equipment: [Weapon] {starting_sword.name}, [Potion] 2x Small Potions")
    print(f"  Gold: {format_gold(player.gold)}")
    return player


# Merchant System
def handle_merchant(player, shop_items):
    """Handle the merchant encounter with buy/sell/pass commands.

    Args:
        player: The Player object.
        shop_items: List of Item objects for sale.
    """
    while True:
        try:
            action = input("  > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            break

        if action == "pass":
            print('  "Come back anytime!" says the merchant.')
            break

        if action.startswith("buy "):
            try:
                item_num = int(action[4:].strip())
                if 1 <= item_num <= len(shop_items):
                    item = shop_items[item_num - 1]
                    if player.gold >= item.value:
                        player.gold -= item.value
                        player.add_to_inventory(item)
                        print(f"  Purchased {item.name}! Remaining gold: {format_gold(player.gold)}")
                        shop_items.pop(item_num - 1)
                        if not shop_items:
                            print('  "You bought everything! Safe travels."')
                            break
                        # remaining items
                        for i, it in enumerate(shop_items, 1):
                            print(f"    {i}. {it} — Price: {it.value}g")
                    else:
                        raise InsufficientGoldError(item.value, player.gold)
                else:
                    print(f"  Invalid item number. Choose 1-{len(shop_items)}.")
            except ValueError:
                print("  Usage: buy <number>")
            except InsufficientGoldError as e:
                print(f"  {e.message}")
        elif action.startswith("sell "):
            item_name = action[5:].strip()
            if not item_name:
                print("  Usage: sell <item name>")
                continue
            success, msg = player.sell_item(item_name)
            print(f"  {msg}")
        elif action == "inventory" or action == "inv":
            print(player.show_inventory())
        else:
            print("  Type 'buy <number>' to purchase, 'sell <item name>' to sell, 'inv' to view inventory, or 'pass' to skip.")


# Map Display
def show_map(player, dungeon):
    """Display a simple text map showing visited rooms.

    Uses set comprehension to determine which rooms to display.

    Args:
        player: The Player object (for visited_rooms set).
        dungeon: The Dungeon object.
    """
    visited_ids = {rid for rid in player.visited_rooms}

    print("\n+=== Dungeon Map ===")
    print("  (V = visited, ? = unvisited, * = current)\n")

    for room_id, room in dungeon.rooms.items():
        if room_id == dungeon.current_room_id:
            marker = "*"
        elif room_id in visited_ids:
            marker = "V"
        else:
            marker = "?"

        if room_id in visited_ids or room_id == dungeon.current_room_id:
            exits_str = ", ".join(room.exits.keys()) if room.exits else "none"
            print(f"  [{marker}] {room.name} -> exits: {exits_str}")
        else:
            print(f"  [?] ??? ")

    print(f"\n+{'=' * 18}+")


# Game Over
def game_over_screen(player, won=False):
    """Display the game over or victory screen.

    Args:
        player: The Player object.
        won: True if the player won, False if defeated.
    """
    if won:
        print("""
+===================================================+
|                                                   |
|          *** V I C T O R Y ! ***                  |
|                                                   |
|    You have conquered the Realm of Shadows!       |
|    The sunlight warms your face as you emerge     |
|    from the dungeon, victorious.                  |
|                                                   |
+===================================================+
        """)
        print(f"  Hero: {player.name}")
        print(f"  Level: {player.level}")
        print(f"  Gold collected: {format_gold(player.gold)}")
        print(f"  Rooms explored: {len(player.visited_rooms)}")
    else:
        print("""
+===================================================+
|                                                   |
|           xxx  G A M E   O V E R  xxx             |
|                                                   |
|      Your journey ends in the darkness...         |
|      The shadows claim another soul.              |
|                                                   |
+===================================================+
        """)
        print(f"  Hero: {player.name} (Level {player.level})")
        print(f"  Rooms explored: {len(player.visited_rooms)}")
        print("  Better luck next time, adventurer.\n")


# Combat Rewards
def give_combat_rewards(player, enemies):
    """Award XP and gold after a successful combat.

    Args:
        player: The Player object.
        enemies: List of defeated Enemy objects.
    """
    total_xp = sum(e.xp_reward for e in enemies)
    total_gold = sum(generate_loot_gold(e.gold_reward, player.level) for e in enemies)

    player.gold += total_gold
    xp_messages = player.gain_xp(total_xp)

    print(f"\n  [Loot] {format_gold(total_gold)}")
    for msg in xp_messages:
        print(f"  {msg}")


# Main Game Loop 
def game_loop(player, dungeon):
    """The main game loop — handles exploration and events.

    Args:
        player: The Player object.
        dungeon: The Dungeon object.
    """
   
    events = event_generator()

 
    current_room = dungeon.get_current_room()
    player.visited_rooms.add(dungeon.current_room_id)
    print(current_room.describe())
    print(f"\n  Type 'help' to see available commands.\n")

   
    merchant_items = None

    while True:
        current_room = dungeon.get_current_room()
        if current_room.is_exit:
            game_over_screen(player, won=True)
            break

        try:
            raw_input_str = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Saving and exiting...")
            try:
                save_game(player, dungeon)
                print("  Game auto-saved!")
            except SaveLoadError as e:
                print(f"  Warning: {e.message}")
            break

        if not raw_input_str:
            continue

       
        try:
            command, argument = parse_command(raw_input_str)
        except InvalidCommandError as e:
            print(f"  {e.message}")
            continue

        # Handle commands 
        try:
            if command == "look":
                print(current_room.describe())

            elif command == "go":
                if not argument:
                    print("  Usage: go <direction> (north/south/east/west)")
                    continue

                direction = resolve_direction(argument)
                if direction is None:
                    print(f"  Invalid direction: '{argument}'. Use north/south/east/west (or n/s/e/w).")
                    continue

                success, message = dungeon.move(direction)
                print(f"  {message}")

                if success:
                    player.visited_rooms.add(dungeon.current_room_id)
                    new_room = dungeon.get_current_room()

                   
                    if not new_room.has_enemies() and not new_room.is_exit:
                        event = next(events)
                        event_messages = handle_event(event, player)
                        for msg in event_messages:
                            print(f"  {msg}")

                        
                        if event["type"] == "merchant":
                            merchant_items = event["data"]["items"]
                            handle_merchant(player, merchant_items)
                            merchant_items = None

                        
                        if not player.is_alive():
                            game_over_screen(player, won=False)
                            break

            elif command == "attack":
                if not current_room.has_enemies():
                    print("  There are no enemies to fight here.")
                    continue

                enemies = current_room.get_alive_enemies()
                victory = start_combat(player, enemies)

                if victory:
                    give_combat_rewards(player, enemies)
                elif not player.is_alive():
                    game_over_screen(player, won=False)
                    break

            elif command == "use":
                if not argument:
                    print("  Usage: use <item name>")
                    continue
                msg = player.use_potion(argument)
                print(f"  {msg}")

            elif command == "take":
                if not argument:
                    print("  Usage: take <item name>")
                    continue

                
                found = None
                for item in current_room.items:
                    if item.name.lower() == argument.lower():
                        found = item
                        break

                if found:
                    current_room.items.remove(found)
                    player.add_to_inventory(found)
                    print(f"  Picked up: {found.name}")
                else:
                    print(f"  There is no '{argument}' here to pick up.")

            elif command == "equip":
                if not argument:
                    print("  Usage: equip <weapon name>")
                    continue
                msg = player.equip_weapon(argument)
                print(f"  {msg}")

            elif command == "cast":
                print("  Spells can only be cast during combat. Use 'attack' to start combat.")

            elif command == "inventory":
                print(player.show_inventory())

            elif command == "stats":
                print(player.show_stats())

            elif command == "map":
                show_map(player, dungeon)

            elif command == "save":
                slot = argument if argument else "autosave"
                filepath = save_game(player, dungeon, slot)
                print(f"  Game saved to slot '{slot}'!")

            elif command == "load":
                saves = list_saves()
                if not saves:
                    print("  No save files found.")
                    continue

                print("  Available saves:")
                for s in saves:
                    print(f"    - {s['slot']}: {s['player_name']} (Lv.{s['level']}) -- {s['timestamp']}")

                slot = argument if argument else "autosave"
                player_data, dungeon_data = load_game(slot)
                player = Player.from_dict(player_data)
                dungeon = Dungeon.from_dict(dungeon_data)
                print(f"  Game loaded from slot '{slot}'!")
                print(dungeon.get_current_room().describe())

            elif command == "help":
                print(get_help_text())

            elif command == "quit":
                print("  Save before quitting? (yes/no)")
                try:
                    answer = input("  > ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    answer = "no"

                if answer in ("yes", "y"):
                    try:
                        save_game(player, dungeon)
                        print("  Game saved!")
                    except SaveLoadError as e:
                        print(f"  Warning: {e.message}")
                print("  Farewell, adventurer! May the shadows guide you.")
                break

            elif command == "buy":
                
                print("  There is no merchant here. Explore the dungeon to find one!")

            elif command == "sell":
                if not argument:
                    print("  Usage: sell <item name> (only available at a merchant)")
                    continue
                print("  You can only sell items at a merchant. Explore the dungeon to find one!")

            elif command == "pass":
                print("  Nothing to pass on right now.")

        except PlayerDeadError as e:
            print(f"  {e.message}")
            game_over_screen(player, won=False)
            break
        except GameError as e:
            print(f"  Error: {e.message}")


# Entry Point
def main():
    """Main entry point for the game."""
   
    enemy_data = load_enemy_data()

    while True:
        choice = show_main_menu()

        if choice == "1":
            
            player = create_new_player()
            dungeon = build_dungeon(enemy_data)
            game_loop(player, dungeon)

        elif choice == "2":
            
            saves = list_saves()
            if not saves:
                print("\n  No save files found. Start a new game first!\n")
                continue

            print("\n  Available saves:")
            for s in saves:
                print(f"    - {s['slot']}: {s['player_name']} (Lv.{s['level']}) -- {s['timestamp']}")

            try:
                slot = input("\n  Enter save slot name (or press Enter for 'autosave'): ").strip()
            except (EOFError, KeyboardInterrupt):
                continue

            slot = slot if slot else "autosave"

            try:
                player_data, dungeon_data = load_game(slot)
                player = Player.from_dict(player_data)
                dungeon = Dungeon.from_dict(dungeon_data)
                print(f"\n  Welcome back, {player.name}! (Level {player.level})")
                game_loop(player, dungeon)
            except SaveLoadError as e:
                print(f"\n  {e.message}\n")

        elif choice == "3":
            print("\n  Farewell, adventurer! May the shadows guide you.\n")
            break


if __name__ == "__main__":
    main()
