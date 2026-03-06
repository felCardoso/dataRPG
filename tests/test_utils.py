from pytest import approx
from datarpg.core import Actor
from datarpg.utils import AttrifySerializer, ActorTemplate

# Using approx to handle floating point precision errors


def test_full_serialization_cycle():
    # 1. Create a complex Actor
    original = Actor("Mage")
    intel = original.add_attribute("int", 20)
    original.add_derived("mana", "int", multiplier=5.0)

    # Add modifiers of different types
    intel.add_modifier("hat", 2, kind="flat", tag="headgear")
    original.attributes["mana"].add_modifier("ring", 0.1, kind="percent", duration=10)

    # 2. Serialize to JSON
    data_json = AttrifySerializer.to_json(original)

    # 3. Reconstruct from data
    loaded = AttrifySerializer.from_json(data_json, is_path=False)

    # 4. Integrity checks
    assert loaded.name == "Mage"
    assert loaded.int.base_value == 20
    assert "hat" in loaded.int.modifiers

    # The stress test: does the derived web still work?
    # Expected: (20 + 2) * 5.0 * 1.1 = 121.0
    assert loaded.mana.value == approx(121.0)

    # If we change the intelligence of the loaded actor, does mana react?
    loaded.int.add_modifier("potion", 8)  # int goes to 30

    # Expected: (30 * 5) * 1.1 = 165.0
    assert loaded.mana.value == approx(165.0)


# tests/test_templates.py


def test_actor_template_creation():
    # Setup template
    tpl = ActorTemplate("Warrior")
    tpl.add_attribute_config("str", 10)
    tpl.add_derived_config("atk", "str", 2.0)

    # Create instance
    hero = tpl.create_actor("Arthur")

    assert hero.name == "Arthur"
    assert hero.str.value == 10
    assert hero.atk.value == 20

    # Check if derivation is active
    hero.str.add_modifier("sword", 5)
    assert hero.atk.value == 30
