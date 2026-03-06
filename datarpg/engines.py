# import time
import logging

logger = logging.getLogger("datarpg")


class TickEngine:
    """Manages time passing for expiring buffs."""

    def __init__(self, actor):
        self.actor = actor

    def update(self, delta_time):
        """Logic to decrease the modifiers duration."""
        for attr in self.actor.attributes.values():
            to_remove = []
            for mod_id, mod in attr.modifiers.items():
                if mod.duration is not None:
                    mod.duration -= delta_time
                    if mod.is_expired():
                        to_remove.append(mod_id)
                        logger.info(
                            f"Modifier '{mod_id}' expired for attribute '{attr.name}'"
                        )

            # Remove expired modifiers
            for mod_id in to_remove:
                attr.remove_modifier(mod_id)
