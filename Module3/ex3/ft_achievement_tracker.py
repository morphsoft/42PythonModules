import random

ACHIEVEMENTS = [
    "First Steps", "Speed Runner", "Boss Slayer", "Collector Supreme",
    "Master Explorer", "Treasure Hunter", "Untouchable", "Unstoppable",
    "Survivor", "Strategist", "Sharp Mind", "Crafting Genius",
    "World Savior", "Hidden Path Finder", "Night Owl", "Early Bird",
    "Dragon Tamer", "Gold Hoarder", "Perfectionist", "Pacifist",
    "Speed Demon", "Lucky Strike", "Combo Master", "Iron Will",
    "Lore Keeper", "Map Maker", "Beast Friend", "Shadow Walker",
    "Potion Brewer", "Sky Diver", "Deep Diver", "Puzzle Solver",
    "Guardian", "Champion", "Legend", "Veteran", "Rookie of the Year",
    "Marathon Runner", "Sharpshooter", "Completionist", "Treasure Seeker",
    "Monster Hunter", "Silent Step", "Fire Starter", "Ice Breaker",
    "Storm Rider", "Time Traveler", "Last Stand",
]

PLAYERS = ["Alice", "Bob", "Charlie", "Dylan"]


def gen_player_achievements() -> set[str]:
    """Build a random set of achievements for one player.

    Each player picks about half of the 48 achievements: this balances
    the chances of having common achievements (high pick rate) and
    achievements owned by a single player (low pick rate).
    """
    count = random.randint(22, 26)
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
