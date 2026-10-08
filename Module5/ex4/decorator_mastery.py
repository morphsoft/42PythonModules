import functools
import time
from collections.abc import Callable
from typing import Any


def spell_timer(func: Callable) -> Callable:
    """Print how long the decorated function takes to run."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        print(f"Casting {func.__name__}...")
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"Spell completed in {elapsed:.3f} seconds")
        return result
    return wrapper


def power_validator(min_power: int) -> Callable:
    """Build a decorator that rejects calls whose power is too low.

    The power is read from the 'power' keyword argument or, failing
    that, from the last positional argument.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if "power" in kwargs:
                power = kwargs["power"]
            elif len(args) > 0:
                power = args[-1]
            else:
                power = None
            if not isinstance(power, int) or power < min_power:
                return "Insufficient power for this spell"
            return func(*args, **kwargs)
        return wrapper
    return decorator


def retry_spell(max_attempts: int) -> Callable:
    """Build a decorator that retries a function when it raises."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt < max_attempts:
                        print("Spell failed, retrying... "
                              f"(attempt {attempt}/{max_attempts})")
            return f"Spell casting failed after {max_attempts} attempts"
        return wrapper
    return decorator


class MageGuild:
    """A guild that validates mage names and casts spells."""

    @staticmethod
    def validate_mage_name(name: str) -> bool:
        """A name needs 3+ characters made of letters and spaces only."""
        return len(name) >= 3 and name.replace(" ", "").isalpha()

    @power_validator(10)
    def cast_spell(self, spell_name: str, power: int) -> str:
        """Cast a spell, provided the power validator lets it through."""
        return f"Successfully cast {spell_name} with {power} power"


@spell_timer
def fireball() -> str:
    """A slow spell used to demonstrate the timer."""
    time.sleep(0.1)
    return "Fireball cast!"


@power_validator(20)
def lightning(target: str, power: int) -> str:
    """A standalone spell protected by the power validator."""
    return f"Lightning strikes {target} with {power} power"


@retry_spell(3)
def cursed_spell() -> str:
    """A spell that always fails."""
    raise RuntimeError("The spell backfired")


@retry_spell(3)
def war_cry() -> str:
    """A spell that always succeeds."""
    return "Waaaaaaagh spelled !"


def main() -> None:
    """Demonstrate every decorator and the MageGuild class."""
    print("Testing spell timer...")
    print(f"Result: {fireball()}")
    print(f"Preserved name: {fireball.__name__}")
    print()

    print("Testing power validator...")
    print(lightning("Orc", 25))
    print(lightning("Orc", 5))
    print()

    print("Testing retrying spell...")
    print(cursed_spell())
    print(war_cry())
    print()

    print("Testing MageGuild...")
    print(MageGuild.validate_mage_name("Gandalf the Grey"))
    print(MageGuild.validate_mage_name("X1"))
    guild = MageGuild()
    print(guild.cast_spell("Lightning", 15))
    print(guild.cast_spell("Lightning", 5))


if __name__ == "__main__":
    main()
