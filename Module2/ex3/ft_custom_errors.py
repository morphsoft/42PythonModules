class GardenError(Exception):
    """A basic error for garden problems."""

    def __init__(self, message: str = "Unknown garden error") -> None:
        super().__init__(message)


class PlantError(GardenError):
    """An error for problems with plants."""

    def __init__(self, message: str = "Unknown plant error") -> None:
        super().__init__(message)


class WaterError(GardenError):
    """An error for problems with watering."""

    def __init__(self, message: str = "Unknown water error") -> None:
        super().__init__(message)


def check_plant(plant_name: str, is_wilting: bool) -> None:
    """Raise a PlantError if the plant is wilting."""
    if is_wilting:
        raise PlantError(f"The {plant_name} plant is wilting!")


def check_water(tank_level: int, needed: int) -> None:
    """Raise a WaterError if the tank does not hold enough water."""
    if tank_level < needed:
        raise WaterError("Not enough water in the tank!")


def test_plant_error() -> None:
    """Show how to catch a PlantError specifically."""
    print("Testing PlantError...")
    try:
        check_plant("tomato", True)
    except PlantError as error:
        print(f"Caught PlantError: {error}")


def test_water_error() -> None:
    """Show how to catch a WaterError specifically."""
    print("Testing WaterError...")
    try:
        check_water(2, 10)
    except WaterError as error:
        print(f"Caught WaterError: {error}")


def test_all_garden_errors() -> None:
    """Show that catching GardenError catches every garden error."""
    print("Testing catching all garden errors...")
    try:
        check_plant("tomato", True)
    except GardenError as error:
        print(f"Caught GardenError: {error}")
    try:
        check_water(2, 10)
    except GardenError as error:
        print(f"Caught GardenError: {error}")


def test_custom_errors() -> None:
    """Run the full custom errors demonstration."""
    print("=== Custom Garden Errors Demo ===")
    print()
    test_plant_error()
    print()
    test_water_error()
    print()
    test_all_garden_errors()
    print()
    print("All custom error types work correctly!")


if __name__ == "__main__":
    test_custom_errors()