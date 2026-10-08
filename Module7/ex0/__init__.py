"""Creature factories. Concrete creatures are only reachable via factories."""

from .factory import AquaFactory, CreatureFactory, FlameFactory

__all__ = ["CreatureFactory", "FlameFactory", "AquaFactory"]
