import pytest
from attrify.core import Attribute, DerivedAttribute, Actor
from attrify.engines import TickEngine


def test_modifier_expiry():
    # Setup
    hero = Actor("Test Hero")
    strength = hero.add_attribute("str", 10)
    engine = TickEngine(hero)

    # Adiciona um buff que dura 3 "segundos"
    strength.add_modifier("temp_buff", 5, duration=3)
    assert strength.value == 15

    # Simula passar 1 segundo
    engine.update(1)
    assert strength.value == 15
    assert strength.modifiers["temp_buff"].duration == 2

    # Simula passar mais 2 segundos (total 3)
    engine.update(2)

    # O buff deve ter expirado e sido removido
    assert strength.value == 10
    assert "temp_buff" not in strength.modifiers


def test_mixed_permanent_and_temporary_modifiers():
    hero = Actor("Test Hero")
    agi = hero.add_attribute("agi", 10)
    engine = TickEngine(hero)

    # Um permanente e um temporário
    agi.add_modifier("boots", 2, duration=None)  # Permanente
    agi.add_modifier("speed_potion", 8, duration=5)  # Temporário

    assert agi.value == 20

    # Passa muito tempo
    engine.update(100)

    # Apenas as botas devem sobrar
    assert agi.value == 12


def test_base_value_initialization():
    """Gararante que o atributo começa com o valor correto."""
    attr = Attribute("Strength", 10)
    assert attr.base_value == 10
    assert attr.value == 10


def test_flat_modifier():
    """Testa bônus fixos (soma)."""
    attr = Attribute("Strength", 10)
    attr.add_modifier("sword", 5, kind="flat")
    # 10 + 5 = 15
    assert attr.value == 15


def test_percent_modifier():
    """Testa bônus percentuais (multiplicação)."""
    attr = Attribute("Strength", 10)
    attr.add_modifier("buff", 0.5, kind="percent")  # +50%
    # 10 * 1.5 = 15
    assert attr.value == 15.0


def test_mixed_modifiers_math():
    """
    Testa a fórmula real de RPG: (Base + Flats) * (1 + Percents)
    Este é o teste mais importante da biblioteca!
    """
    attr = Attribute("Strength", 10)
    attr.add_modifier("sword", 5, kind="flat")  # +5
    attr.add_modifier("potion", 0.2, kind="percent")  # +20%

    # (10 + 5) * 1.2 = 18
    assert attr.value == 18.0


def test_tag_anti_stacking():
    """Testa se o sistema de tags ignora modificadores mais fracos."""
    attr = Attribute("Defense", 10)
    attr.add_modifier("small_shield", 2, tag="shield")
    attr.add_modifier("great_shield", 10, tag="shield")

    # Deve ignorar o +2 e usar apenas o +10
    assert attr.value == 20


def test_modifier_removal():
    """Testa se a remoção por ID funciona e recalcula o valor."""
    attr = Attribute("Agility", 10)
    attr.add_modifier("item_boots", 5, tag="boots")
    assert attr.value == 15
    attr.remove_modifier("item_boots")
    assert attr.value == 10


def test_derived_attribute_chain_reaction():
    """Testa se o filho atualiza automaticamente quando o pai muda."""
    stamina = Attribute("Stamina", 10)
    # Health é 10x a Stamina
    health = DerivedAttribute("Health", stamina, multiplier=10.0)

    assert health.value == 100.0

    # Adiciona bônus no pai
    stamina.add_modifier("buff", 5)  # Stamina vai para 15

    # Health deve ir para 150 automaticamente
    assert health.value == 150.0


def test_derived_attribute_with_its_own_modifiers():
    """Garante que o filho pode ter seus próprios bônus além da herança."""
    mana_pool = Attribute("Intelligence", 10)
    mana = DerivedAttribute("Mana", mana_pool, multiplier=5.0)  # Base 50

    # Bônus direto na mana
    mana.add_modifier("ring", 20, kind="flat")

    # 50 (da inteligência) + 20 (do anel) = 70
    assert mana.value == 70.0
