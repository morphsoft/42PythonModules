from abc import ABC, abstractmethod


class HealCapability(ABC):
    """Ability to heal, independent from any Creature."""

    @abstractmethod
    def heal(self) -> str:
        """Describe the healing action."""


class TransformCapability(ABC):
    """Ability to switch into a transformed state and back."""

    _transformed: bool = False

    @property
    def transformed(self) -> bool:
        """Whether the transformation is currently active."""
        return self._transformed

    @abstractmethod
    def transform(self) -> str:
        """Enter the transformed state and describe it."""

    @abstractmethod
    def revert(self) -> str:
        """Leave the transformed state and describe it."""
