from collections.abc import Callable

Spell = Callable[[str, int], str]


def ensure_callable(*candidates: object) -> None:
    """Raise a TypeError if any candidate cannot be called."""
    for candidate in candidates:
        if not callable(candidate):
            raise TypeError(f"{candidate!r} is not a callable spell")


def spell_combiner(spell1: Spell, spell2: Spell) -> Callable:
    """Build a spell that casts both spells and returns both results."""
    ensure_callable(spell1, spell2)

    def combined(target: str, power: int) -> tuple[str, str]:
        return (spell1(target, power), spell2(target, power))
    return combined


def power_amplifier(base_spell: Spell, multiplier: int) -> Spell:
    """Build a spell that multiplies the power before casting."""
    ensure_callable(base_spell)

    def amplified(target: str, power: int) -> str:
        return base_spell(target, power * multiplier)
    return amplified


def conditional_caster(condition: Callable[[str, int], bool],
                       spell: Spell) -> Spell:
    """Build a spell that only casts when the condition holds."""
    ensure_callable(condition, spell)

    def guarded(target: str, power: int) -> str:
        if condition(target, power):
            return spell(target, power)
        return "Spell fizzled"
    return guarded


def spell_sequence(spells: list[Spell]) -> Callable:
    """Build a spell that casts every spell in order."""
    ensure_callable(*spells)

    def sequence(target: str, power: int) -> list[str]:
        return [spell(target, power) for spell in spells]
    return sequence


def fireball(target: str, power: int) -> str:
    """A basic attack spell."""
    return f"Fireball hits {target} for {power} damage"


def heal(target: str, power: int) -> str:
    """A basic healing spell."""
    return f"Heal restores {target} for {power} HP"


def power_reading(target: str, power: int) -> str:
    """A spell that simply reports the power it received."""
    return f"{power}"


def main() -> None:
    """Demonstrate every spell modifier."""
    print("Testing spell combiner...")
    combined = spell_combiner(fireball, heal)
    print("Combined spell result:", ", ".join(combined("Dragon", 10)))
    print()

    print("Testing power amplifier...")
    amplified = power_amplifier(power_reading, 3)
    print(f"Original: {power_reading('Dragon', 10)}, "
          f"Amplified: {amplified('Dragon', 10)}")
    mega_fireball = power_amplifier(fireball, 3)
    print(mega_fireball("Dragon", 10))
    print()

    print("Testing conditional caster...")
    careful_fireball = conditional_caster(
        lambda target, power: power >= 20, fireball)
    print(f"Power 10: {careful_fireball('Goblin', 10)}")
    print(f"Power 25: {careful_fireball('Goblin', 25)}")
    print()

    print("Testing spell sequence...")
    combo = spell_sequence([fireball, heal, mega_fireball])
    for result in combo("Troll", 5):
        print(f"- {result}")
    print()

    print("Testing callable check...")
    print(f"Is fireball callable? {callable(fireball)}")
    print(f"Is 'fireball' callable? {callable('fireball')}")
    try:
        spell_combiner(fireball, "not a spell")  # type: ignore[arg-type]
    except TypeError as error:
        print(f"Caught TypeError: {error}")


if __name__ == "__main__":
    main()
