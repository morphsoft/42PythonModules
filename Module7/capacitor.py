from ex1 import HealingCreatureFactory, TransformCreatureFactory


def test_healing() -> None:
    """Describe, attack and heal with the healing family."""
    print("Testing Creature with healing capability")
    factory = HealingCreatureFactory()
    for label, creature in (("base", factory.create_base()),
                            ("evolved", factory.create_evolved())):
        print(f" {label}:")
        print(creature.describe())
        print(creature.attack())
        if hasattr(creature, "heal"):
            print(creature.heal())


def test_transform() -> None:
    """Describe, attack, transform, attack and revert."""
    print("Testing Creature with transform capability")
    factory = TransformCreatureFactory()
    for label, creature in (("base", factory.create_base()),
                            ("evolved", factory.create_evolved())):
        print(f" {label}:")
        print(creature.describe())
        print(creature.attack())
        if hasattr(creature, "transform") and hasattr(creature, "revert"):
            print(creature.transform())
            print(creature.attack())
            print(creature.revert())


def main() -> None:
    """Run both capability scenarios."""
    test_healing()
    print()
    test_transform()


if __name__ == "__main__":
    main()
