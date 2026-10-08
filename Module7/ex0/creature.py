from abc import ABC, abstractmethod


class Creature(ABC):
    """A card representing a creature with a name and a type."""

    def __init__(self, name: str, creature_type: str) -> None:
        self.name = name
        self.creature_type = creature_type

    @abstractmethod
    def attack(self) -> str:
        """Describe the creature's attack."""

    def describe(self) -> str:
        """Standard description shared by every creature."""
        return f"{self.name} is a {self.creature_type} type Creature"
