"""
events.py — Event generator for Realm of Shadows.

Uses a generator function to produce random dungeon events
when the player enters a new room.
"""

import random
import copy

from models.items import POTION_TEMPLATES, WEAPON_TEMPLATES, SPELL_TEMPLATES


def event_generator():
    """Generator that yields random dungeon events indefinitely.

    Each event is a dictionary with a 'type' key and associated data.
    Events include traps, treasure finds, merchant encounters,
    stat boosts, and ambushes.

    Yields:
        dict: An event dictionary with 'type' and 'data' keys.
    """
    event_types = ["trap", "treasure", "merchant", "rest", "nothing", "nothing"]

    while True:
        event_type = random.choice(event_types)

        if event_type == "trap":
            damage = random.randint(5, 20)
            yield {
                "type": "trap",
                "data": {
                    "damage": damage,
                    "message": (
                        f"[!] TRAP! You triggered a hidden trap and took {damage} damage!"
                    ),
                },
            }

        elif event_type == "treasure":
            gold = random.randint(5, 30)
            all_templates = list(
                item for item in POTION_TEMPLATES[:2] + WEAPON_TEMPLATES[:2]
            )
            loot = copy.deepcopy(random.choice(all_templates))
            yield {
                "type": "treasure",
                "data": {
                    "gold": gold,
                    "item": loot,
                    "message": (
                        f"[$$] TREASURE! You found a hidden chest containing "
                        f"{gold} gold and a {loot.name}!"
                    ),
                },
            }

        elif event_type == "merchant":
            
            shop_pool = POTION_TEMPLATES + WEAPON_TEMPLATES[:3] + SPELL_TEMPLATES[:2]
            shop_items = [copy.deepcopy(item) for item in random.sample(shop_pool, min(3, len(shop_pool)))]
            yield {
                "type": "merchant",
                "data": {
                    "items": shop_items,
                    "message": (
                        "[Merchant] A wandering merchant appears from the shadows!\n"
                        '  "Take a look at my wares, adventurer..."'
                    ),
                },
            }

        elif event_type == "rest":
            heal = random.randint(10, 30)
            yield {
                "type": "rest",
                "data": {
                    "heal": heal,
                    "message": (
                        f"[Rest] You find a quiet corner and rest for a moment. "
                        f"Recovered {heal} HP."
                    ),
                },
            }

        else:
            yield {
                "type": "nothing",
                "data": {
                    "message": random.choice([
                        "The room is eerily silent...",
                        "Shadows dance on the walls, but nothing happens.",
                        "A cold breeze passes through the corridor.",
                        "You hear distant echoes, but the way is clear.",
                        "Dust motes float in the dim torchlight.",
                    ]),
                },
            }


def handle_event(event, player):
    """Process an event and apply its effects to the player.

    Args:
        event: An event dictionary from the event_generator.
        player: The Player object to apply effects to.

    Returns:
        A list of message strings to display to the player.
    """
    messages = [event["data"]["message"]]
    event_type = event["type"]

    if event_type == "trap":
        damage = event["data"]["damage"]
        actual = player.take_damage(damage + player.defense) 
        messages.append(f"  You lost {actual} HP!")

    elif event_type == "treasure":
        gold = event["data"]["gold"]
        item = event["data"]["item"]
        player.gold += gold
        player.add_to_inventory(item)
        messages.append(f"  {item.name} added to inventory. Gold: {player.gold}")

    elif event_type == "rest":
        heal = event["data"]["heal"]
        actual = player.heal(heal)
        messages.append(f"  Restored {actual} HP!")

    elif event_type == "merchant":
        messages.append("  Type 'buy <number>' to purchase, or 'pass' to skip.")
        items = event["data"]["items"]
        for i, item in enumerate(items, 1):
            messages.append(f"    {i}. {item} — Price: {item.value}g")

    return messages
