class Modifier:
    def __init__(self, name, amount, kind="flat", tag=None, duration=None):
        self.name = name
        self.amount = amount
        self.kind = kind  # "flat" (sum) / "percent" (multiply)
        self.tag = tag
        self.duration = duration  # Optional: time in seconds or turns


class Attribute:
    def __init__(self, name, base_value):
        self.name = name
        self.base_value = base_value
        self.modifiers = {}

    def add_modifier(self, id, value, kind="flat", tag=None):
        """
        Add a bonus or penalty modifier to the attribute.
        id: Unique identifier for the modifier (e.g., "sword_item_01", ...)
        tag: Modifier category for grouping (e.g., "potion", "item", ...)
        """
        modifier = Modifier(id, value, kind, tag)
        self.modifiers[id] = modifier

    def remove_modifier(self, mod_id):
        """Remove a modifier by its ID."""
        if mod_id in self.modifiers:
            del self.modifiers[mod_id]

    @property
    def value(self):
        # 1. Filter by tag and get the biggest
        active_mods = []
        tagged_groups = {}

        for mod in self.modifiers.values():
            if mod.tag:
                # Group by tag and stores only the one with the highest value.
                if (
                    mod.tag not in tagged_groups
                    or mod.amount > tagged_groups[mod.tag].amount
                ):
                    tagged_groups[mod.tag] = mod
            else:
                active_mods.append(mod)

        active_mods.extend(tagged_groups.values())

        # 2. Final calculation
        total = self.base_value

        # 2.1 Sum all flat modifiers
        flats = sum(m.amount for m in active_mods if m.kind == "flat")
        total += flats

        # 2.2 Apply all percent modifiers
        multipliers = sum(m.amount for m in active_mods if m.kind == "percent")
        total *= 1 + multipliers

        return total
