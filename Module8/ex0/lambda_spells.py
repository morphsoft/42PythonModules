def artifact_sorter(artifacts: list[dict]) -> list[dict]:
    """Sort artifacts by power, most powerful first."""
    return sorted(artifacts, key=lambda artifact: artifact["power"],
                  reverse=True)


def power_filter(mages: list[dict], min_power: int) -> list[dict]:
    """Keep only the mages whose power reaches min_power."""
    return list(filter(lambda mage: mage["power"] >= min_power, mages))


def spell_transformer(spells: list[str]) -> list[str]:
    """Decorate every spell name with '* ' and ' *'."""
    return list(map(lambda spell: f"* {spell} *", spells))


def mage_stats(mages: list[dict]) -> dict:
    """Return the max, min and average power of the mages."""
    if len(mages) == 0:
        return {"max_power": 0, "min_power": 0, "avg_power": 0.0}
    strongest = max(mages, key=lambda mage: mage["power"])
    weakest = min(mages, key=lambda mage: mage["power"])
    total = sum(map(lambda mage: mage["power"], mages))
    return {
        "max_power": strongest["power"],
        "min_power": weakest["power"],
        "avg_power": round(total / len(mages), 2),
    }


def main() -> None:
    """Demonstrate the lambda-based helpers."""
    artifacts = [
        {"name": "Crystal Orb", "power": 85, "type": "orb"},
        {"name": "Fire Staff", "power": 92, "type": "staff"},
        {"name": "Shadow Cloak", "power": 60, "type": "armor"},
    ]
    mages = [
        {"name": "Alex", "power": 75, "element": "fire"},
        {"name": "Jordan", "power": 92, "element": "ice"},
        {"name": "Riley", "power": 48, "element": "earth"},
    ]
    spells = ["fireball", "heal", "shield"]

    print("Testing artifact sorter...")
    sorted_artifacts = artifact_sorter(artifacts)
    first, second = sorted_artifacts[0], sorted_artifacts[1]
    print(f"{first['name']} ({first['power']} power) comes before "
          f"{second['name']} ({second['power']} power)")
    print()

    print("Testing power filter...")
    strong_mages = power_filter(mages, 70)
    print("Mages with power >= 70:",
          ", ".join(map(lambda mage: mage["name"], strong_mages)))
    print()

    print("Testing spell transformer...")
    print(" ".join(spell_transformer(spells)))
    print()

    print("Testing mage stats...")
    stats = mage_stats(mages)
    print(f"Max: {stats['max_power']}, Min: {stats['min_power']}, "
          f"Average: {stats['avg_power']}")


if __name__ == "__main__":
    main()
