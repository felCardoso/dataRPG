import json
import logging
from .core import Actor

logger = logging.getLogger("datarpg")


class AttrifySerializer:
    """Serializer Class: Converts actors to/from JSON, YAML and TOML."""

    # --- JSON ---
    @staticmethod
    def to_json(actor, filepath=None):
        data = {
            "name": actor.name,
            "attributes": {aid: a.to_dict() for aid, a in actor.attributes.items()},
        }
        output = json.dumps(data, indent=4)
        if filepath:
            with open(filepath, "w") as f:
                f.write(output)
        return output

    @staticmethod
    def from_json(json_input, is_path=True):
        """Carrega um Actor de um arquivo .json ou string JSON."""
        if is_path:
            with open(json_input, "r") as f:
                data = json.load(f)
        else:
            data = json.loads(json_input)
        return Actor.from_dict(data)

    # --- YAML ---
    @staticmethod
    def to_yaml(actor, filepath=None):
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML is required for YAML support. Install with: pip install datarpg[yaml]"
            )

        data = {
            "name": actor.name,
            "attributes": {aid: a.to_dict() for aid, a in actor.attributes.items()},
        }
        output = yaml.dump(data, sort_keys=False)
        if filepath:
            with open(filepath, "w") as f:
                f.write(output)
        return output

    @staticmethod
    def from_yaml(yaml_input, is_path=True):
        """Carrega um Actor de um arquivo .yaml ou string YAML."""
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML is required. Install with: pip install datarpg[yaml]"
            )

        if is_path:
            with open(yaml_input, "r") as f:
                data = yaml.safe_load(f)
        else:
            data = yaml.safe_load(yaml_input)
        return Actor.from_dict(data)

    # --- TOML ---
    @staticmethod
    def to_toml(actor, filepath=None):
        try:
            import toml
        except ImportError:
            raise ImportError(
                "toml is required for TOML support. Install with: pip install datarpg[toml]"
            )

        data = {
            "name": actor.name,
            "attributes": {aid: a.to_dict() for aid, a in actor.attributes.items()},
        }
        if filepath:
            with open(filepath, "w") as f:
                toml.dump(data, f)
        return toml.dumps(data)

    @staticmethod
    def from_toml(filepath):
        """TOML geralmente é lido de arquivos de config."""
        try:
            import toml
        except ImportError:
            raise ImportError(
                "toml is required. Install with: pip install datarpg[toml]"
            )

        with open(filepath, "r") as f:
            data = toml.load(f)
        return Actor.from_dict(data)

    @staticmethod
    def load_template(filepath):
        """
        Loads an ActorTemplate from a file.
        Supports YAML, TOML, or JSON based on file extension.
        """
        import os

        ext = os.path.splitext(filepath)[1].lower()

        with open(filepath, "r") as f:
            if ext == ".yaml" or ext == ".yml":
                import yaml

                data = yaml.safe_load(f)
            elif ext == ".toml":
                import toml

                data = toml.load(f)
            else:
                import json

                data = json.load(f)

        return ActorTemplate.from_dict(data)


class ActorTemplate:
    """
    Represents a blueprint for creating Actors with predefined attributes.
    """

    def __init__(self, name, attributes=None):
        self.template_name = name
        # attributes will store: {"id": {"type": "base", "value": 10}, ...}
        self.attributes = attributes or {}

    def add_attribute_config(self, attr_id, base_value):
        """Add a base attribute definition to the template."""
        self.attributes[attr_id] = {"type": "base", "value": base_value}

    def add_derived_config(self, attr_id, parent_id, multiplier):
        """Add a derived attribute definition to the template."""
        self.attributes[attr_id] = {
            "type": "derived",
            "parent_id": parent_id,
            "multiplier": multiplier,
        }

    def create_actor(self, instance_name=None):
        """
        Instantiates a new Actor based on this template.
        """
        name = instance_name or f"New {self.template_name}"
        actor = Actor(name)

        # First pass: Base attributes
        for aid, config in self.attributes.items():
            if config["type"] == "base":
                actor.add_attribute(aid, config["value"])

        # Second pass: Derived attributes
        for aid, config in self.attributes.items():
            if config["type"] == "derived":
                actor.add_derived(aid, config["parent_id"], config["multiplier"])

        return actor

    @classmethod
    def from_dict(cls, data):
        """Create a template from a dictionary (e.g., loaded from YAML/JSON)."""
        return cls(data["name"], data["attributes"])


def format_mod_string(value, kind):
    """Modifier Formatter (e.g., 0.2 to '+20%' / 5 to '+5'."""
    if kind == "percent":
        return f"+{int(value * 100)}%" if value >= 0 else f"{int(value * 100)}%"
    return f"+{value}" if value >= 0 else str(value)


def bulk_add_modifiers(actor, mod_data):
    """
    Adds multiple modifiers to an actor's attributes.
    (e.g.: mod_data = {"str": 5, "agi": 2} )
    """
    for attr_id, value in mod_data.items():
        if attr_id in actor.attributes:
            actor.attributes[attr_id].add_modifier(f"bulk_{attr_id}", value)
