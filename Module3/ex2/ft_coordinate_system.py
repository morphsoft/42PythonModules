import math

Point = tuple[float, float, float]

PROMPT = "Enter new coordinates as floats in format 'x,y,z': "


def parse_coordinates(answer: str) -> Point | None:
    """Turn an 'x,y,z' string into a tuple, or None if it is invalid."""
    try:
        x_text, y_text, z_text = answer.split(",")
    except ValueError:
        print("Invalid syntax")
        return None
    values: list[float] = []
    for text in (x_text, y_text, z_text):
        text = text.strip()
        try:
            values.append(float(text))
        except ValueError as error:
            print(f"Error on parameter '{text}': {error}")
            return None
    return (values[0], values[1], values[2])


def get_player_pos() -> Point:
    """Ask for coordinates until a valid set is provided."""
    while True:
        position = parse_coordinates(input(PROMPT))
        if position is not None:
            return position


def distance(first: Point, second: Point) -> float:
    """Return the Euclidean distance between two 3D points."""
    return math.sqrt((second[0] - first[0]) ** 2
                     + (second[1] - first[1]) ** 2
                     + (second[2] - first[2]) ** 2)


def main() -> None:
    """Read two positions and compute distances between them."""
    print("=== Game Coordinate System ===")
    print()
    print("Get a first set of coordinates")
    first = get_player_pos()
    print(f"Got a first tuple: {first}")
    print(f"It includes: X={first[0]}, Y={first[1]}, Z={first[2]}")
    center: Point = (0.0, 0.0, 0.0)
    print(f"Distance to center: {round(distance(center, first), 4)}")
    print()
    print("Get a second set of coordinates")
    second = get_player_pos()
    print("Distance between the 2 sets of coordinates: "
          f"{round(distance(first, second), 4)}")


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print()
        print("No more input, exiting")
