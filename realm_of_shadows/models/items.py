"""
items.py — Item classes for Realm of Shadows.

Defines the item hierarchy: Item (base), Weapon, Potion, and Spell.
Each item has serialization support (to_dict / from_dict) for save/load.
"""


class Item:
    """Base class for all items in the game.

    Attributes:
        name: Display name of the item.
        description: Short description shown to the player.
        value: Gold value (for buying/selling).
        item_type: Category string ('item', 'weapon', 'potion', 'spell').
    """

    def __init__(self, name, description="A mysterious item.", value=0):
        self.name = name
        self.description = description
        self.value = value
        self.item_type = "item"

    def __str__(self):
        return f"{self.name} — {self.description} (Value: {self.value}g)"

    def __repr__(self):
        return f"Item(name='{self.name}', value={self.value})"

    def to_dict(self):
        """Serialize the item to a dictionary for JSON storage."""
        return {
            "name": self.name,
            "description": self.description,
            "value": self.value,
            "item_type": self.item_type,
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize an item from a dictionary.

        Uses the 'item_type' field to determine which subclass to create.
        """
        item_type = data.get("item_type", "item")

        if item_type == "weapon":
            return Weapon(
                name=data["name"],
                description=data.get("description", ""),
                value=data.get("value", 0),
                power=data.get("power", 0),
            )
        elif item_type == "potion":
            return Potion(
                name=data["name"],
                description=data.get("description", ""),
                value=data.get("value", 0),
                heal_amount=data.get("heal_amount", 0),
            )
        elif item_type == "spell":
            return Spell(
                name=data["name"],
                description=data.get("description", ""),
                value=data.get("value", 0),
                power=data.get("power", 0),
                mana_cost=data.get("mana_cost", 0),
            )
        else:
            return cls(
                name=data["name"],
                description=data.get("description", ""),
                value=data.get("value", 0),
            )


class Weapon(Item):
    """A weapon that increases the player's attack power.

    Attributes:
        power: Additional attack damage dealt when equipped.
    """

    def __init__(self, name, description="A sturdy weapon.", value=0, power=5):
        super().__init__(name, description, value)
        self.power = power
        self.item_type = "weapon"

    def __str__(self):
        return f"[W] {self.name} -- {self.description} (ATK+{self.power}, Value: {self.value}g)"

    def to_dict(self):
        data = super().to_dict()
        data["power"] = self.power
        return data


class Potion(Item):
    """A consumable potion that restores HP.

    Attributes:
        heal_amount: Amount of HP restored when used.
    """

    def __init__(self, name, description="A healing potion.", value=0, heal_amount=20):
        super().__init__(name, description, value)
        self.heal_amount = heal_amount
        self.power = 0  
        self.item_type = "potion"

    def __str__(self):
        return f"[P] {self.name} -- {self.description} (Heals {self.heal_amount} HP, Value: {self.value}g)"

    def to_dict(self):
        data = super().to_dict()
        data["heal_amount"] = self.heal_amount
        return data


class Spell(Item):
    """A magical spell that deals damage and costs mana.

    Attributes:
        power: Damage dealt by the spell.
        mana_cost: Mana required to cast the spell.
    """

    def __init__(self, name, description="A magical spell.", value=0, power=15, mana_cost=10):
        super().__init__(name, description, value)
        self.power = power
        self.mana_cost = mana_cost
        self.item_type = "spell"

    def __str__(self):
        return (
            f"[S] {self.name} -- {self.description} "
            f"(DMG: {self.power}, Mana: {self.mana_cost}, Value: {self.value}g)"
        )

    def to_dict(self):
        data = super().to_dict()
        data["power"] = self.power
        data["mana_cost"] = self.mana_cost
        return data


# ── Predefined Item Templates

WEAPON_TEMPLATES = [
    Weapon("Rusty Sword", "A dull blade, but better than bare fists.", value=10, power=5),
    Weapon("Iron Axe", "A solid axe forged from iron.", value=25, power=10),
    Weapon("Steel Longsword", "A well-crafted longsword with a sharp edge.", value=50, power=16),
    Weapon("Shadow Blade", "A dark blade that seems to absorb light.", value=80, power=22),
    Weapon("Dragon Slayer", "A legendary sword said to fell dragons.", value=150, power=30),
]

POTION_TEMPLATES = [
    Potion("Small Potion", "A small vial of red liquid.", value=5, heal_amount=20),
    Potion("Medium Potion", "A flask of healing elixir.", value=15, heal_amount=45),
    Potion("Large Potion", "A large bottle of potent medicine.", value=30, heal_amount=80),
    Potion("Elixir of Life", "A shimmering golden elixir.", value=60, heal_amount=150),
]

SPELL_TEMPLATES = [
    Spell("Fire Bolt", "A bolt of searing flame.", value=20, power=12, mana_cost=8),
    Spell("Ice Shard", "A razor-sharp shard of ice.", value=30, power=18, mana_cost=12),
    Spell("Lightning Strike", "A devastating bolt of lightning.", value=50, power=28, mana_cost=20),
    Spell("Shadow Nova", "An explosion of dark energy.", value=75, power=40, mana_cost=30),
]
