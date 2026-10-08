from abc import ABC, abstractmethod

from .creature import Creature
from .creatures import Aquabub, Flameling, Pyrodon, Torragon


class CreatureFactory(ABC):
    """Abstract factory producing the creatures of one family."""

    @abstractmethod
    def create_base(self) -> Creature:
        """Create the base creature of the family."""

    @abstractmethod
    def create_evolved(self) -> Creature:
        """Create the evolved creature of the family."""


class FlameFactory(CreatureFactory):
    """Produces the Fire family."""

    def create_base(self) -> Creature:
        return Flameling()

    def create_evolved(self) -> Creature:
        return Pyrodon()


class AquaFactory(CreatureFactory):
    """Produces the Water family."""

    def create_base(self) -> Creature:
        return Aquabub()

    def create_evolved(self) -> Creature:
        return Torragon()
