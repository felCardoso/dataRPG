import logging

logger = logging.getLogger("datarpg")
# Prevents "No handler found" warnings if the user doesn't confifg it
logger.addHandler(logging.NullHandler())


class Actor:
    def __init__(self, name="Generic Actor"):
        self.name = name
        self.attributes = {}

    def add_attribute(self, attr_id, base_value):
        """Adds a common attribute."""
        attr = Attribute(attr_id, base_value)
        self.attributes[attr_id] = attr
        return attr

    def add_derived(self, attr_id, parent_id, multiplier=0.1):
        """Creates a link between two attributes in the Actor."""
        if parent_id not in self.attributes:
            raise KeyError(f"Parent attribute '{parent_id}' not found in Actor.")

        parent = self.attributes[parent_id]
        derived = DerivedAttribute(attr_id, parent, multiplier)
        self.attributes[attr_id] = derived
        return derived

    def get(self, attr_id):
        """Shortcut to get final value: actor.get('str')"""
        return self.attributes[attr_id].value

    def __getattr__(self, item):
        """Accessing as a property: actor.strength"""
        if item in self.attributes:
            return self.attributes[item]
        raise AttributeError(f"Actor has no attribute '{item}'")

    @classmethod
    def from_dict(cls, data):
        """Reconstructs an Actor from a dictionary."""
        actor = cls(data.get("name", "Unknown Actor"))
        attr_configs = data.get("attributes", {})

        # 1. Create all base attributes
        for aid, config in attr_configs.items():
            if config.get("type") == "base":
                actor.add_attribute(aid, config["base_value"])

        # 2. Create derived attributes
        for aid, config in attr_configs.items():
            if config.get("type") == "derived":
                actor.add_derived(
                    aid, parent_id=config["parent_id"], multiplier=config["multiplier"]
                )

        # 3. Reapply modifiers
        for aid, config in attr_configs.items():
            target_attr = actor.attributes.get(aid)
            if not target_attr:
                continue

            for mid, m_data in config.get("modifiers", {}).items():
                target_attr.add_modifier(
                    mod_id=mid,
                    value=m_data["amount"],
                    kind=m_data["kind"],
                    tag=m_data.get("tag"),
                    duration=m_data.get("duration"),
                )

        return actor


class Modifier:
    def __init__(self, name, amount, kind="flat", tag=None, duration=None):
        self.name = name
        self.amount = amount
        self.kind = kind  # "flat" (sum) / "percent" (multiply)
        self.tag = tag
        self.duration = duration  # Optional: time in seconds (int / float)

    def is_expired(self):
        """Checks if the modifier is still valid."""
        if self.duration is None:
            return False
        return self.duration <= 0

    def to_dict(self):
        return {
            "name": self.name,
            "amount": self.amount,
            "kind": self.kind,
            "tag": self.tag,
            "duration": self.duration,
        }


class Attribute:
    def __init__(self, name, base_value):
        self.name = name
        self.base_value = base_value
        self.modifiers = {}
        self.listeners = []  # Optional: for event-driven updates

    def add_listener(self, attribute):
        """ "Add an attribute to be notified when this attribute changes."""
        self.listeners.append(attribute)

    def add_modifier(self, mod_id, value, kind="flat", tag=None, duration=None):
        """
        Add a bonus or penalty modifier to the attribute.
        mod_id: Unique identifier for the modifier (e.g., "sword_item_01", ...)
        tag: Modifier category for grouping (e.g., "potion", "item", ...)
        """
        modifier = Modifier(mod_id, value, kind, tag, duration)
        self.modifiers[mod_id] = modifier
        self._notify_listeners()
        logger.debug(
            f"Modifier '{mod_id}' added to '{self.name}': "
            f"value={value}, kind={kind}, tag={tag}, duration={duration}"
        )

    def _notify_listeners(self):
        for listener in self.listeners:
            listener.update_derived()

    def update_derived(self):
        """Recalculate derived attributes when a base attribute changes."""
        pass

    def remove_modifier(self, mod_id):
        """Remove a modifier by its id."""
        if mod_id in self.modifiers:
            del self.modifiers[mod_id]

    @property
    def value(self):
        # 1. Filter by tag and get the biggest (Anti-stacking)
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

        # return round(total, 4)  # Returns 2.3330 instead of 2.3333333333333335 Readability (nerd)
        return total  # Returns 2.3333333333333335 ULTRAPRECISION (chad)

    def to_dict(self):
        return {
            "type": "base",
            "name": self.name,
            "base_value": self.base_value,
            "modifiers": {mid: m.to_dict() for mid, m in self.modifiers.items()},
        }


class DerivedAttribute(Attribute):
    def __init__(self, name, parent_attribute, multiplier=0.1):
        # Base value will be calculated from the parent attribute, so we start with 0.
        super().__init__(name, base_value=0)
        self.parent = parent_attribute
        self.multiplier = multiplier

        # Register this derived attribute as a listener to the parent attribute
        self.parent.add_listener(self)

        # Calculate the initial value
        self.update_derived()

    def update_derived(self):
        """Recalculate the base value based on the parent attribute and multiplier."""
        self.base_value = self.parent.value * self.multiplier

    def to_dict(self):
        data = super().to_dict()
        data.update(
            {
                "type": "derived",
                "parent_id": self.parent.name,  # Parent's ID
                "multiplier": self.multiplier,
            }
        )
        return data
