import functools
import operator
from collections.abc import Callable
from typing import Any


def spell_reducer(spells: list[int], operation: str) -> int:
    """Combine all spell powers with the requested operation."""
    operations: dict[str, Callable[[int, int], int]] = {
        "add": operator.add,
        "multiply": operator.mul,
        "max": lambda first, second: first if first >= second else second,
        "min": lambda first, second: first if first <= second else second,
    }
    if operation not in operations:
        raise ValueError(f"Unknown operation '{operation}'")
    if len(spells) == 0:
        return 0
    return functools.reduce(operations[operation], spells)


def partial_enchanter(
        base_enchantment: Callable[[int, str, str], str]
) -> dict[str, Callable]:
    """Create element-specific enchantments with power fixed to 50."""
    return {
        element: functools.partial(base_enchantment, 50, element)
        for element in ("fire", "ice", "lightning")
    }


@functools.lru_cache(maxsize=None)
def memoized_fibonacci(n: int) -> int:
    """Return the nth Fibonacci number, caching every result."""
    if n < 0:
        raise ValueError("Fibonacci is not defined for negative numbers")
    if n < 2:
        return n
    return memoized_fibonacci(n - 1) + memoized_fibonacci(n - 2)


def spell_dispatcher() -> Callable[[Any], str]:
    """Build a spell caster whose behavior depends on the argument type."""
    @functools.singledispatch
    def cast(spell: Any) -> str:
        return "Unknown spell type"

    @cast.register
    def cast_damage(spell: int) -> str:
        return f"Damage spell: {spell} damage"

    @cast.register
    def cast_enchantment(spell: str) -> str:
        return f"Enchantment: {spell}"

    @cast.register
    def cast_multi(spell: list) -> str:
        return f"Multi-cast: {len(spell)} spells"

    return cast


def enchant(power: int, element: str, target: str) -> str:
    """Base enchantment used to demonstrate partial application."""
    return f"{target} enchanted with {element} ({power} power)"


def main() -> None:
    """Demonstrate the functools artifacts."""
    spells = [10, 20, 30, 40]
    print("Testing spell reducer...")
    print(f"Sum: {spell_reducer(spells, 'add')}")
    print(f"Product: {spell_reducer(spells, 'multiply')}")
    print(f"Max: {spell_reducer(spells, 'max')}")
    print(f"Min: {spell_reducer(spells, 'min')}")
    print(f"Empty: {spell_reducer([], 'add')}")
    try:
        spell_reducer(spells, "divide")
    except ValueError as error:
        print(f"Caught ValueError: {error}")
    print()

    print("Testing partial enchanter...")
    enchanters = partial_enchanter(enchant)
    for element, enchanter in enchanters.items():
        print(f"{element}: {enchanter('Sword')}")
    print()

    print("Testing memoized fibonacci...")
    for n in (0, 1, 10, 15):
        print(f"Fib({n}): {memoized_fibonacci(n)}")
    print(f"Cache info: {memoized_fibonacci.cache_info()}")
    print()

    print("Testing spell dispatcher...")
    cast = spell_dispatcher()
    print(cast(42))
    print(cast("fireball"))
    print(cast(["fireball", "heal", "shield"]))
    print(cast(3.14))


if __name__ == "__main__":
    main()
