# 🐉 Realm of Shadows — Text-Based RPG

A text-based dungeon crawler RPG written in Python. Explore a dark dungeon, fight enemies in turn-based combat, collect items and spells, and defeat the Shadow Dragon to escape!

## 📋 Project Information

- **Author**: Bora Gungor
- **Language**: Python 3.8+
- **Dependencies**: None (uses only Python standard library)
- **Type**: Console / CLI application

## 🎮 How to Play

### Running the Game

```bash
cd realm_of_shadows
python main.py
```

No external packages or virtual environment needed — the game uses only Python's standard library.

### Game Commands

| Command | Description |
|---------|-------------|
| `look` | Examine your current surroundings |
| `go <direction>` | Move (north/south/east/west or n/s/e/w) |
| `attack` | Start combat with enemies in the room |
| `use <item>` | Use a potion from your inventory |
| `take <item>` | Pick up an item from the ground |
| `equip <weapon>` | Equip a weapon from inventory |
| `cast <spell>` | Cast a spell during combat |
| `inventory` | View your inventory (shortcut: `inv`) |
| `stats` | View character statistics |
| `map` | Show a map of visited rooms |
| `save` | Save your progress |
| `load` | Load a saved game |
| `help` | Show available commands |
| `quit` | Exit the game |

### Combat

During combat, you can:
- **attack** — Physical attack against the enemy
- **use <potion>** — Drink a healing potion
- **cast <spell>** — Cast a magic spell (costs mana)
- **flee** — 40% chance to escape the battle

### Tips
- Explore side rooms for better weapons and spells before facing tough enemies
- Save often — enemies can be dangerous!
- Manage your mana for spell casting in boss fights
- Equip stronger weapons as you find them

## 📁 Project Structure

```
realm_of_shadows/
├── main.py              # Game entry point and main loop
├── models/
│   ├── __init__.py
│   ├── character.py     # Player, Enemy classes (inheritance)
│   ├── items.py         # Item, Weapon, Potion, Spell classes
│   └── room.py          # Room, Dungeon classes
├── engine/
│   ├── __init__.py
│   ├── combat.py        # Turn-based combat system
│   ├── commands.py      # Command parser (regex)
│   └── events.py        # Random event generator
├── utils/
│   ├── __init__.py
│   ├── decorators.py    # Custom decorators (@requires_alive, @log_action)
│   ├── exceptions.py    # Custom exception classes
│   ├── helpers.py       # Helper functions and lambdas
│   └── serializer.py    # JSON save/load system
├── data/
│   └── enemies.json     # Enemy definitions
├── saves/               # Save files (auto-created)
└── README.md            # This file
```

## 🐍 Python Elements Used

| Element | Where Used |
|---------|-----------|
| **Classes & Inheritance** | `Character → Player/Enemy`, `Item → Weapon/Potion/Spell` |
| **Control Statements** | Combat loop (`while`), menu (`if/elif`), iterations (`for`) |
| **Operators** | Damage calculation, HP comparisons, gold checks |
| **Functions + Lambda** | Helper functions in `helpers.py`, lambda for sorting/damage |
| **Custom Decorators** | `@requires_alive`, `@log_action` in `decorators.py` |
| **Collections** | `list` (inventory), `dict` (room exits, stats), `set` (visited rooms) |
| **Comprehensions** | List/dict/set comprehensions in character, room, serializer |
| **Generator** | `event_generator()` in `events.py` using `yield` |
| **File Handling + `with`** | Save/load system, log writing, enemy data loading |
| **Serialization (JSON)** | Game state save/load via `json.dump`/`json.load` |
| **Regular Expressions** | Command parsing, name validation in `commands.py` |
| **Custom Exceptions** | `GameError`, `PlayerDeadError`, `InvalidCommandError`, etc. |
| **Modules** | 3 packages (`models`, `engine`, `utils`) with clean separation |
