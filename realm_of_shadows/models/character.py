"""
character.py — Character classes for Realm of Shadows.

Defines the character hierarchy: Character (base), Player, and Enemy.
Player manages inventory, leveling, equipped weapon, and mana.
Enemy is created from JSON data and drops loot on defeat.
"""

from models.items import Item, Weapon, Potion, Spell
from utils.helpers import calculate_xp_for_level, hp_bar


class Character:
    """Base class for all characters (players and enemies).

    Attributes:
        name: Character's display name.
        hp: Current hit points.
        max_hp: Maximum hit points.
        attack: Base attack power.
        defense: Base defense value.
    """

    def __init__(self, name, hp, attack, defense):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.defense = defense

    def is_alive(self):
        """Check whether the character is still alive."""
        return self.hp > 0

    def take_damage(self, amount):
        """Apply damage to the character.

        Args:
            amount: Raw damage before defense is applied.

        Returns:
            Actual damage dealt (after defense, minimum 1).
        """
        actual = max(1, amount - self.defense)
        self.hp = max(0, self.hp - actual)
        return actual

    def heal(self, amount):
        """Heal the character by the given amount, capped at max_hp.

        Args:
            amount: HP to restore.

        Returns:
            Actual amount healed.
        """
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp

    def __str__(self):
        return f"{self.name} {hp_bar(self.hp, self.max_hp)}"


class Player(Character):
    """The player character with inventory, leveling, and equipment.

    Attributes:
        level: Current level (starts at 1).
        xp: Current experience points.
        gold: Currency for purchases.
        inventory: List of Item objects.
        equipped_weapon: Currently equipped Weapon (or None).
        mana: Current mana points.
        max_mana: Maximum mana points.
        visited_rooms: Set of room IDs the player has visited.
    """

    def __init__(self, name, hp=100, attack=10, defense=5):
        super().__init__(name, hp, attack, defense)
        self.level = 1
        self.xp = 0
        self.gold = 20
        self.inventory = []
        self.equipped_weapon = None
        self.mana = 30
        self.max_mana = 30
        self.visited_rooms = set()

    def get_total_attack(self):
        """Calculate total attack including equipped weapon bonus."""
        weapon_bonus = self.equipped_weapon.power if self.equipped_weapon else 0
        return self.attack + weapon_bonus

    def add_to_inventory(self, item):
        """Add an item to the player's inventory.

        Args:
            item: The Item object to add.
        """
        self.inventory.append(item)

    def remove_from_inventory(self, item_name):
        """Remove an item from inventory by name.

        Args:
            item_name: Name of the item to remove.

        Returns:
            The removed Item object, or None if not found.
        """
        for i, item in enumerate(self.inventory):
            if item.name.lower() == item_name.lower():
                return self.inventory.pop(i)
        return None

    def find_item(self, item_name):
        """Find an item in inventory by name (case-insensitive).

        Args:
            item_name: Name to search for.

        Returns:
            The matching Item, or None.
        """
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                return item
        return None

    def equip_weapon(self, weapon_name):
        """Equip a weapon from inventory.

        Args:
            weapon_name: Name of the weapon to equip.

        Returns:
            A status message string.
        """
        item = self.find_item(weapon_name)
        if item is None:
            return f"You don't have '{weapon_name}' in your inventory."
        if not isinstance(item, Weapon):
            return f"'{item.name}' is not a weapon and cannot be equipped."

        
        if self.equipped_weapon is not None:
            old_name = self.equipped_weapon.name
            self.add_to_inventory(self.equipped_weapon)
            msg_unequip = f"Unequipped {old_name}. "
        else:
            msg_unequip = ""

        self.equipped_weapon = item
        self.remove_from_inventory(weapon_name)
        return f"{msg_unequip}Equipped {item.name}! (ATK+{item.power})"

    def use_potion(self, potion_name):
        """Use a potion from inventory to restore HP.

        Args:
            potion_name: Name of the potion to use.

        Returns:
            A status message string.
        """
        item = self.find_item(potion_name)
        if item is None:
            return f"You don't have '{potion_name}' in your inventory."
        if not isinstance(item, Potion):
            return f"'{item.name}' is not a potion."

        healed = self.heal(item.heal_amount)
        self.remove_from_inventory(potion_name)
        return f"Used {item.name}! Restored {healed} HP. {hp_bar(self.hp, self.max_hp)}"

    def gain_xp(self, amount):
        """Add experience points and check for level up.

        Args:
            amount: XP to add.

        Returns:
            A list of status message strings (may include level-up info).
        """
        self.xp += amount
        messages = [f"Gained {amount} XP!"]

        
        while self.xp >= calculate_xp_for_level(self.level):
            self.xp -= calculate_xp_for_level(self.level)
            self.level += 1
            self.max_hp += 15
            self.hp = self.max_hp 
            self.attack += 3
            self.defense += 2
            self.max_mana += 5
            self.mana = self.max_mana
            messages.append(
                f"  ★ LEVEL UP! You are now Level {self.level}! "
                f"(HP: {self.max_hp}, ATK: {self.attack}, DEF: {self.defense})"
            )

        return messages

    def use_mana(self, cost):
        """Consume mana for casting a spell.

        Args:
            cost: Mana to consume.

        Returns:
            True if enough mana was available, False otherwise.
        """
        if self.mana >= cost:
            self.mana -= cost
            return True
        return False

    def show_stats(self):
        """Return a formatted string of the player's current stats."""
        
        stats_dict = {k: v for k, v in {
            "Level": self.level,
            "XP": f"{self.xp}/{calculate_xp_for_level(self.level)}",
            "HP": hp_bar(self.hp, self.max_hp),
            "Mana": f"{self.mana}/{self.max_mana}",
            "Attack": self.get_total_attack(),
            "Defense": self.defense,
            "Gold": self.gold,
            "Weapon": self.equipped_weapon.name if self.equipped_weapon else "None",
            "Items": len(self.inventory),
        }.items()}

        lines = [f"+=== {self.name}'s Stats ==="]
        for key, val in stats_dict.items():
            lines.append(f"  {key}: {val}")

        
        spells = [item for item in self.inventory if isinstance(item, Spell)]
        if spells:
            lines.append("")
            lines.append("  Spells:")
            for spell in spells:
                lines.append(f"    - {spell.name} (DMG: {spell.power}, Mana: {spell.mana_cost})")
        else:
            lines.append("")
            lines.append("  Spells: None")

        lines.append(f"+{'=' * (len(lines[0]) - 2)}+")
        return "\n".join(lines)

    def show_inventory(self):
        """Return a formatted inventory listing."""
        lines = ["+=== Inventory ==="]

        if self.equipped_weapon:
            lines.append(f"  Equipped: [W] {self.equipped_weapon.name} (ATK+{self.equipped_weapon.power})")
        else:
            lines.append("  Equipped: None")

        if not self.inventory:
            lines.append("")
            lines.append("  (Inventory is empty)")
        else:
            lines.append("")
            
            item_lines = [f"  {i+1}. {item}" for i, item in enumerate(self.inventory)]
            lines.extend(item_lines)

        lines.append(f"+{'=' * 18}+")
        return "\n".join(lines)

    def sell_item(self, item_name):
        """Sell an item from inventory for its gold value.

        Args:
            item_name: Name of the item to sell.

        Returns:
            A tuple of (success: bool, message: str).
        """
        item = self.find_item(item_name)
        if item is None:
            return False, f"You don't have '{item_name}' in your inventory."

        sell_price = max(1, item.value // 2)  
        self.remove_from_inventory(item_name)
        self.gold += sell_price
        return True, f"Sold {item.name} for {sell_price}g! Gold: {self.gold}g"

    def to_dict(self):
        """Serialize the player to a dictionary for JSON storage."""
        return {
            "name": self.name,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "attack": self.attack,
            "defense": self.defense,
            "level": self.level,
            "xp": self.xp,
            "gold": self.gold,
            "mana": self.mana,
            "max_mana": self.max_mana,
            "inventory": [item.to_dict() for item in self.inventory],
            "equipped_weapon": self.equipped_weapon.to_dict() if self.equipped_weapon else None,
            "visited_rooms": list(self.visited_rooms),  # Sets are not JSON-serializable
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize a Player from a dictionary."""
        player = cls(
            name=data["name"],
            hp=data.get("max_hp", 100),
            attack=data.get("attack", 10),
            defense=data.get("defense", 5),
        )
        player.hp = data.get("hp", player.max_hp)
        player.max_hp = data.get("max_hp", 100)
        player.level = data.get("level", 1)
        player.xp = data.get("xp", 0)
        player.gold = data.get("gold", 0)
        player.mana = data.get("mana", 30)
        player.max_mana = data.get("max_mana", 30)
        player.inventory = [Item.from_dict(i) for i in data.get("inventory", [])]
        player.visited_rooms = set(data.get("visited_rooms", []))

        weapon_data = data.get("equipped_weapon")
        if weapon_data:
            player.equipped_weapon = Item.from_dict(weapon_data)
        return player


class Enemy(Character):
    """An enemy character that the player fights.

    Attributes:
        xp_reward: XP gained by the player upon defeating this enemy.
        gold_reward: Gold dropped upon defeat.
        description: Flavor text describing the enemy.
    """

    def __init__(self, name, hp, attack, defense, xp_reward=0, gold_reward=0, description=""):
        super().__init__(name, hp, attack, defense)
        self.xp_reward = xp_reward
        self.gold_reward = gold_reward
        self.description = description

    def __str__(self):
        return f"{self.name} {hp_bar(self.hp, self.max_hp)} (ATK:{self.attack} DEF:{self.defense})"

    @classmethod
    def from_dict(cls, data):
        """Create an Enemy from a dictionary (e.g., loaded from JSON)."""
        return cls(
            name=data["name"],
            hp=data["hp"],
            attack=data["attack"],
            defense=data["defense"],
            xp_reward=data.get("xp", 0),
            gold_reward=data.get("gold", 0),
            description=data.get("description", ""),
        )

    def to_dict(self):
        """Serialize the enemy to a dictionary."""
        return {
            "name": self.name,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "attack": self.attack,
            "defense": self.defense,
            "xp": self.xp_reward,
            "gold": self.gold_reward,
            "description": self.description,
        }
