import random

ACHIEVEMENTS = [
    "First Steps", "Speed Runner", "Boss Slayer", "Collector Supreme",
    "Master Explorer", "Treasure Hunter", "Untouchable", "Unstoppable",
    "Survivor", "Strategist", "Sharp Mind", "Crafting Genius",
    "World Savior", "Hidden Path Finder",
]

PLAYERS = ["Alice", "Bob", "Charlie", "Dylan"]


def gen_player_achievements() -> set[str]:
    """Build a random set of achievements for one player."""
    count = random.randint(4, 9)
    return set(random.sample(ACHIEVEMENTS, count))


def main() -> None:
    """Generate achievements for several players and compare them."""
    print("=== Achievement Tracker System ===")
    print()
    players: list[tuple[str, set[str]]] = []
    for name in PLAYERS:
        achievements = gen_player_achievements()
        players.append((name, achievements))
        print(f"Player {name}: {achievements}")
    print()

    all_achievements: set[str] = set()
    for _, achievements in players:
        all_achievements = all_achievements.union(achievements)
    print(f"All distinct achievements: {all_achievements}")
    print()

    common = set(all_achievements)
    for _, achievements in players:
        common = common.intersection(achievements)
    print(f"Common achievements: {common}")
    print()

    for name, achievements in players:
        unique = set(achievements)
        for other_name, other_achievements in players:
            if other_name != name:
                unique = unique.difference(other_achievements)
        print(f"Only {name} has: {unique}")
    print()

    full_set = set(ACHIEVEMENTS)
    for name, achievements in players:
        print(f"{name} is missing: {full_set.difference(achievements)}")


if __name__ == "__main__":
    main()
