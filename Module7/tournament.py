from ex0 import AquaFactory, CreatureFactory, FlameFactory
from ex1 import HealingCreatureFactory, TransformCreatureFactory
from ex2 import (AggressiveStrategy, BattleStrategy, DefensiveStrategy,
                 InvalidStrategyError, NormalStrategy)

Opponent = tuple[CreatureFactory, BattleStrategy]


def battle(opponents: list[Opponent]) -> None:
    """Make every opponent fight every other one, once."""
    print("*** Tournament ***")
    print(f"{len(opponents)} opponents involved")
    try:
        for index, (factory, strategy) in enumerate(opponents):
            for other_factory, other_strategy in opponents[index + 1:]:
                challenger = factory.create_base()
                opponent = other_factory.create_base()
                print()
                print("* Battle *")
                print(challenger.describe())
                print(" vs.")
                print(opponent.describe())
                print(" now fight!")
                for line in strategy.act(challenger):
                    print(line)
                for line in other_strategy.act(opponent):
                    print(line)
    except InvalidStrategyError as error:
        print(f"Battle error, aborting tournament: {error}")


def main() -> None:
    """Run three tournaments: a basic one, a failing one, a big one."""
    normal = NormalStrategy()
    aggressive = AggressiveStrategy()
    defensive = DefensiveStrategy()

    print("Tournament 0 (basic)")
    print(" [ (Flameling+Normal), (Healing+Defensive) ]")
    battle([(FlameFactory(), normal),
            (HealingCreatureFactory(), defensive)])
    print()

    print("Tournament 1 (error)")
    print(" [ (Flameling+Aggressive), (Healing+Defensive) ]")
    battle([(FlameFactory(), aggressive),
            (HealingCreatureFactory(), defensive)])
    print()

    print("Tournament 2 (multiple)")
    print(" [ (Aquabub+Normal), (Healing+Defensive), (Transform+Aggressive) ]")
    battle([(AquaFactory(), normal),
            (HealingCreatureFactory(), defensive),
            (TransformCreatureFactory(), aggressive)])


if __name__ == "__main__":
    main()
