from abc import ABC, abstractmethod

from ex0.creature import Creature
from ex1 import HealCapability, TransformCapability


class InvalidStrategyError(Exception):
    """Raised when a creature cannot follow the chosen strategy."""


class BattleStrategy(ABC):
    """How a creature behaves during one round of a tournament."""

    label = "generic"

    @abstractmethod
    def is_valid(self, creature: Creature) -> bool:
        """Tell whether the creature can follow this strategy."""

    @abstractmethod
    def act(self, creature: Creature) -> list[str]:
        """Make the creature act and return what happened."""

    def ensure_valid(self, creature: Creature) -> None:
        """Raise InvalidStrategyError for an unsuitable creature."""
        if not self.is_valid(creature):
            raise InvalidStrategyError(
                f"Invalid Creature '{creature.name}' for this "
                f"{self.label} strategy")


class NormalStrategy(BattleStrategy):
    """Any creature can simply attack."""

    label = "normal"

    def is_valid(self, creature: Creature) -> bool:
        return isinstance(creature, Creature)

    def act(self, creature: Creature) -> list[str]:
        self.ensure_valid(creature)
        return [creature.attack()]


class AggressiveStrategy(BattleStrategy):
    """Transform, attack while transformed, then revert."""

    label = "aggressive"

    def is_valid(self, creature: Creature) -> bool:
        return isinstance(creature, TransformCapability)

    def act(self, creature: Creature) -> list[str]:
        self.ensure_valid(creature)
        if not isinstance(creature, TransformCapability):
            raise InvalidStrategyError("Unreachable: creature was validated")
        return [creature.transform(), creature.attack(), creature.revert()]


class DefensiveStrategy(BattleStrategy):
    """Attack, then heal."""

    label = "defensive"

    def is_valid(self, creature: Creature) -> bool:
        return isinstance(creature, HealCapability)

    def act(self, creature: Creature) -> list[str]:
        self.ensure_valid(creature)
        if not isinstance(creature, HealCapability):
            raise InvalidStrategyError("Unreachable: creature was validated")
        return [creature.attack(), creature.heal()]
