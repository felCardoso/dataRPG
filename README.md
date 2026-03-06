# Attrify ⚔️

**Attrify** is a lightweight and powerful Python library for managing attributes, bonuses, and penalties in games. Stop dealing with manual "Strength + 5" calculations or worrying if potion bonuses are stacking incorrectly.

With Attrify, you focus on your game mechanics, and we handle the math.

## ✨ Key Features

- Native RPG Mathematics: Automatic separation between fixed bonuses (flat) and multipliers (percent).

- Tag System (Anti-stacking): Prevent buffs of the same type from stacking (e.g., only the strongest potion takes effect).

- Unique Identification: Add and remove specific modifiers using unique IDs.

- Lightweight & Extensible: No heavy dependencies, easy to integrate with Pygame, Arcade, or even Godot (via Python).

## 🚀 Installation

_`Coming Soon!`_

<!-- ```Bash
pip install attrify
``` -->

## 🛠️ How to Use

#### 1. Creating an Attribute

```Python
from attrify import Attribute


# Define an attribute with a base value of 10
strength = Attribute("Strength", 10)
```

#### 2. Adding Modifiers

```Python

# Add a flat bonus of +5
strength.add_modifier(mod_id="iron_sword", value=5, kind="flat")

# Add a 20% multiplier (multiplicative)
strength.get_modifier(mod_id="warrior_rage", value=0.20, kind="percent")

print(strength.value) # (10 + 5) \* 1.2 = 18.0
```

#### 3. Using Tags to Prevent Stacking

```Python

# If the player drinks two similar potions, only the highest one applies
strength.add_modifier("agility_potion", 2, tag="potion")
strength.add_modifier("god_potion", 10, tag="potion")

print(strength.value) # The +2 bonus is ignored in favor of the +10
```

## 📐 The Formula

Attrify follows the standard used by most modern RPGs:

```
FinalValue​ = ( Base + ∑Flat ) × ( 1 + ∑% )
```

## 🧪 Running Tests

To ensure the math is always correct:

```Bash
pytest
```

## 🗺️ Roadmap

[ ] Support for Derived Attributes (e.g., Agility affecting Critical Chance).

[ ] Timed Modifiers (auto-expiry system).

[ ] JSON/Dictionary export for Save Game systems.

---

---

### 📄 License

Distributed under the MIT License. See LICENSE for more information.
