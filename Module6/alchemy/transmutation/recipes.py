from alchemy.elements import create_air
from elements import create_fire

from ..potions import strength_potion


def lead_to_gold() -> str:
    """Describe the recipe turning lead into gold."""
    return (f"Recipe transmuting Lead to Gold: brew '{create_air()}' "
            f"and '{strength_potion()}' mixed with '{create_fire()}'")
