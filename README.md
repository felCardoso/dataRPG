# DataRPG 🎮

**DataRPG** is a lightweight, flexible, and data-driven attribute management system for RPGs and game engines. It handles complex math, derived stats, temporary buffs, and data serialization with ease.

## Features

- **Dynamic Calculations**: Support for "Flat" and "Percent" modifiers.
- **Attribute Derivation**: Create dependencies (e.g., `Mana` depends on `Intelligence`).
- **Time-Aware**: Built-in engine to handle expiring buffs and debuffs.
- **Anti-Stacking**: Tag-based system to prevent similar bonuses from stacking.
- **Data-Driven**: Full support for JSON, YAML, and TOML.
- **Templates**: Define character "blueprints" and spawn instances instantly.

---

## Installation

Install the core package:

```bash
pip install datarpg
```

To enable YAML or TOML support, install the optional dependencies:

```Bash
pip install datarpg[yaml]
pip install datarpg[toml]

# Or install everything
pip install datarpg[all]
```

## Quick Start

#### 1. Basic Usage

```Python
from datarpg.core import Actor


# Create a character

hero = Actor("Artorias")

# Add a base attribute

hero.add_attribute("strength", 10)

# Add a derived attribute (Attack = Strength \* 2.0)

hero.add_derived("attack", parent_id="strength", multiplier=2.0)

print(hero.attack.value) # Output: 20.0
```

#### 2. Modifiers and Buffs

```Python

# Add a flat bonus (+5 Strength)

hero.strength.add_modifier("iron_sword", 5, kind="flat")

# Add a timed percentage buff (+10% Strength for 5 seconds)

hero.strength.add_modifier("potion", 0.1, kind="percent", duration=5)

# Automatic recalculation

print(hero.attack.value) # (10 + 5) _ 1.1 _ 2.0 = 33.0
```

#### 3. Using Templates and Serialization

Define your classes in YAML and spawn them:

```YAML
# warrior.yaml

name: "Warrior Class"
attributes:
str: { type: "base", value: 15 }
vit: { type: "base", value: 10 }
hp: { type: "derived", parent_id: "vit", multiplier: 10.0 }
```

```Python
from datarpg.utils import AttrifySerializer

# Load template

warrior_tpl = AttrifySerializer.load_template("warrior.yaml")

# Spawn a new instance

my_hero = warrior_tpl.create_actor("Geralt")
print(my_hero.hp.value) # Output: 100.0
```

## Advanced: The Tick Engine

To make temporary modifiers expire, integrate the TickEngine into your game loop:

```Python
from datarpg.engines import TickEngine

engine = TickEngine(my_hero)

# Inside your game loop (delta_time in seconds/frames)

engine.update(delta_time)
```

## Running Tests

Ensure everything is working correctly:

```Bash
pytest
```

## License

MIT
