"""
room.py — Room and Dungeon classes for Realm of Shadows.

Defines the dungeon layout as interconnected rooms. Each room can
contain enemies, items, and has exits to other rooms.
"""

import random
import copy

from models.items import (
    Item,
    Weapon,
    Potion,
    Spell,
    WEAPON_TEMPLATES,
    POTION_TEMPLATES,
    SPELL_TEMPLATES,
)
from models.character import Enemy


class Room:
    """A single room in the dungeon.

    Attributes:
        room_id: Unique identifier string for the room.
        name: Display name of the room.
        description: Narrative description shown when entering.
        exits: Dictionary mapping direction names to room IDs.
        enemies: List of Enemy objects currently in the room.
        items: List of Item objects on the ground.
        is_boss_room: Whether this room contains a boss enemy.
        is_exit: Whether this room is the dungeon exit (win condition).
    """

    def __init__(self, room_id, name, description, exits=None,
                 enemies=None, items=None, is_boss_room=False, is_exit=False):
        self.room_id = room_id
        self.name = name
        self.description = description
        self.exits = exits if exits is not None else {}  
        self.enemies = enemies if enemies is not None else []  
        self.items = items if items is not None else []
        self.is_boss_room = is_boss_room
        self.is_exit = is_exit

    def has_enemies(self):
        """Check if any living enemies remain in this room."""
        
        alive = [e for e in self.enemies if e.is_alive()]
        return len(alive) > 0

    def get_alive_enemies(self):
        """Return a list of alive enemies in this room."""
        return [e for e in self.enemies if e.is_alive()]

    def describe(self):
        """Return a full description of the room for the player."""
        lines = [
            f"\n{'-' * 45}",
            f"  [Location] {self.name}",
            f"{'-' * 45}",
            f"  {self.description}",
        ]

        
        if self.exits:
            exit_str = ", ".join(
                f"{direction.capitalize()}" for direction in self.exits
            )
            lines.append(f"\n  Exits: {exit_str}")

        
        alive_enemies = self.get_alive_enemies()
        if alive_enemies:
            lines.append(f"\n  [!] Enemies:")
            for enemy in alive_enemies:
                lines.append(f"    - {enemy.name} -- {enemy.description}")

        
        if self.items:
            lines.append(f"\n  [Items] On the ground:")
            for item in self.items:
                lines.append(f"    - {item}")

        lines.append(f"{'-' * 45}")
        return "\n".join(lines)

    def to_dict(self):
        """Serialize the room to a dictionary."""
        return {
            "room_id": self.room_id,
            "name": self.name,
            "description": self.description,
            "exits": self.exits,
            "enemies": [e.to_dict() for e in self.enemies],
            "items": [i.to_dict() for i in self.items],
            "is_boss_room": self.is_boss_room,
            "is_exit": self.is_exit,
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize a Room from a dictionary."""
        enemies = [Enemy.from_dict(e) for e in data.get("enemies", [])]
        items = [Item.from_dict(i) for i in data.get("items", [])]
        return cls(
            room_id=data["room_id"],
            name=data["name"],
            description=data["description"],
            exits=data.get("exits", {}),
            enemies=enemies,
            items=items,
            is_boss_room=data.get("is_boss_room", False),
            is_exit=data.get("is_exit", False),
        )


class Dungeon:
    """The dungeon map — a collection of interconnected rooms.

    Attributes:
        rooms: Dictionary mapping room_id to Room objects.
        current_room_id: The ID of the room the player is currently in.
    """

    def __init__(self):
        self.rooms = {}  
        self.current_room_id = "entrance"

    def add_room(self, room):
        """Add a room to the dungeon.

        Args:
            room: A Room object to add.
        """
        self.rooms[room.room_id] = room

    def get_current_room(self):
        """Get the Room object for the player's current location."""
        return self.rooms.get(self.current_room_id)

    def move(self, direction):
        """Attempt to move in a direction.

        Args:
            direction: A direction string (e.g., 'north', 'south').

        Returns:
            A tuple of (success: bool, message: str).
        """
        current = self.get_current_room()
        direction = direction.lower()

        if direction not in current.exits:
            available = ", ".join(current.exits.keys()) if current.exits else "none"
            return False, f"You can't go {direction}. Available exits: {available}."

        
        if current.has_enemies():
            return False, "Enemies block your path! Defeat them before moving on."

        self.current_room_id = current.exits[direction]
        new_room = self.get_current_room()
        return True, new_room.describe()

    def to_dict(self):
        """Serialize the entire dungeon to a dictionary."""
        return {
            "rooms": {rid: room.to_dict() for rid, room in self.rooms.items()},
            "current_room_id": self.current_room_id,
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize a Dungeon from a dictionary."""
        dungeon = cls()
        dungeon.current_room_id = data.get("current_room_id", "entrance")
        for rid, room_data in data.get("rooms", {}).items():
            dungeon.add_room(Room.from_dict(room_data))
        return dungeon


def build_dungeon(enemy_data):
    """Build the default dungeon layout with rooms, enemies, and items.

    Creates a multi-room dungeon with a variety of encounters and loot.
    The dungeon has a linear-branching structure leading to a boss room.

    Args:
        enemy_data: List of enemy dictionaries loaded from JSON.

    Returns:
        A fully constructed Dungeon object.
    """
    dungeon = Dungeon()

    
    def find_enemy(name):
        for e in enemy_data:
            if e["name"] == name:
                return Enemy.from_dict(copy.deepcopy(e))
        return None

    
    def random_loot():
        templates = POTION_TEMPLATES + WEAPON_TEMPLATES[:3] + SPELL_TEMPLATES[:2]
        chosen = random.choice(templates)
        return copy.deepcopy(chosen)

    
    rooms = [
        Room(
            room_id="entrance",
            name="Dungeon Entrance",
            description=(
                "You stand at the entrance of a dark, foreboding dungeon. "
                "Cold air seeps from the depths below. Torches flicker on the walls."
            ),
            exits={"north": "corridor_1"},
            items=[copy.deepcopy(POTION_TEMPLATES[0])],  # Small potion
        ),
        Room(
            room_id="corridor_1",
            name="Narrow Corridor",
            description=(
                "A narrow stone corridor stretches ahead. The walls are damp "
                "and covered in moss. You hear scratching sounds nearby."
            ),
            exits={"north": "hall", "south": "entrance", "east": "armory"},
            enemies=[find_enemy("Rat")],
        ),
        Room(
            room_id="armory",
            name="Abandoned Armory",
            description=(
                "Rusted weapons line the walls of this old armory. "
                "Most are useless, but something catches your eye..."
            ),
            exits={"west": "corridor_1"},
            items=[
                copy.deepcopy(WEAPON_TEMPLATES[1]),  # Iron Axe
                copy.deepcopy(POTION_TEMPLATES[0]),   # Small Potion
            ],
        ),
        Room(
            room_id="hall",
            name="Great Hall",
            description=(
                "A vast hall with crumbling pillars. Bones litter the floor. "
                "Multiple passages lead deeper into the dungeon."
            ),
            exits={"south": "corridor_1", "west": "library", "north": "corridor_2", "east": "treasury"},
            enemies=[find_enemy("Goblin")],
        ),
        Room(
            room_id="library",
            name="Ancient Library",
            description=(
                "Dusty bookshelves tower to the ceiling. Most books have "
                "crumbled to dust, but a faint magical glow emanates from one corner."
            ),
            exits={"east": "hall"},
            items=[
                copy.deepcopy(SPELL_TEMPLATES[0]),  # Fire Bolt
                copy.deepcopy(SPELL_TEMPLATES[1]),  # Ice Shard
            ],
        ),
        Room(
            room_id="treasury",
            name="Hidden Treasury",
            description=(
                "Gold coins and precious gems are scattered across a stone table. "
                "It seems too good to be true..."
            ),
            exits={"west": "hall"},
            enemies=[find_enemy("Skeleton")],
            items=[copy.deepcopy(POTION_TEMPLATES[1])],  # Medium Potion
        ),
        Room(
            room_id="corridor_2",
            name="Dark Passageway",
            description=(
                "The air grows colder as you descend deeper. Shadows seem to "
                "move on their own. A faint chanting echoes from ahead."
            ),
            exits={"south": "hall", "north": "crypt", "east": "altar"},
            enemies=[find_enemy("Dark Mage")],
        ),
        Room(
            room_id="altar",
            name="Sacrificial Altar",
            description=(
                "A blood-stained altar sits at the center of this circular room. "
                "Dark runes glow on the floor."
            ),
            exits={"west": "corridor_2"},
            enemies=[find_enemy("Wraith")],
            items=[
                copy.deepcopy(WEAPON_TEMPLATES[3]),  # Shadow Blade
                copy.deepcopy(POTION_TEMPLATES[2]),   # Large Potion
            ],
        ),
        Room(
            room_id="crypt",
            name="Underground Crypt",
            description=(
                "Ancient tombs line the walls. The path narrows ahead "
                "as you approach the heart of the dungeon."
            ),
            exits={"south": "corridor_2", "north": "boss_room"},
            enemies=[find_enemy("Troll")],
            items=[
                copy.deepcopy(SPELL_TEMPLATES[2]),    # Lightning Strike
                copy.deepcopy(POTION_TEMPLATES[2]),   # Large Potion
            ],
        ),
        Room(
            room_id="boss_room",
            name="Dragon's Lair",
            description=(
                "A massive cavern opens before you. The heat is overwhelming. "
                "In the center, a Shadow Dragon raises its head and fixes "
                "its burning eyes upon you. This is the final challenge."
            ),
            exits={"south": "crypt", "north": "exit_room"},
            enemies=[find_enemy("Shadow Dragon")],
            is_boss_room=True,
            items=[copy.deepcopy(POTION_TEMPLATES[3])],  # Elixir of Life
        ),
        Room(
            room_id="exit_room",
            name="Dungeon Exit",
            description=(
                "Sunlight floods through a gap in the rocks. You can see the sky! "
                "You have conquered the Realm of Shadows!"
            ),
            exits={},
            is_exit=True,
        ),
    ]

    for room in rooms:
        dungeon.add_room(room)

    return dungeon
