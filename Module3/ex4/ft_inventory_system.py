import sys


def parse_inventory(arguments: list[str]) -> dict[str, int]:
    """Build the inventory from '<item_name>:<quantity>' parameters."""
    inventory: dict[str, int] = {}
    for argument in arguments:
        try:
            name, quantity_text = argument.split(":")
        except ValueError:
            print(f"Error - invalid parameter '{argument}'")
            continue
        if name == "":
            print(f"Error - invalid parameter '{argument}'")
            continue
        if name in inventory:
            print(f"Redundant item '{name}' - discarding")
            continue
        try:
            inventory[name] = int(quantity_text)
        except ValueError as error:
            print(f"Quantity error for '{name}': {error}")
    return inventory


def find_extremes(inventory: dict[str, int]) -> tuple[str, str]:
    """Return the most and least abundant items (first one wins ties)."""
    most = ""
    least = ""
    for name in inventory.keys():
        if most == "" or inventory[name] > inventory[most]:
            most = name
        if least == "" or inventory[name] < inventory[least]:
            least = name
    return (most, least)


def main() -> None:
    """Analyze the inventory given as command-line parameters."""
    print("=== Inventory System Analysis ===")
    inventory = parse_inventory(sys.argv[1:])
    if len(inventory) == 0:
        print("Empty inventory. Usage: "
              "python3 ft_inventory_system.py <item>:<quantity> ...")
        return
    print(f"Got inventory: {inventory}")
    print(f"Item list: {list(inventory.keys())}")
    total = sum(inventory.values())
    print(f"Total quantity of the {len(inventory)} items: {total}")
    for name in inventory.keys():
        percentage = round(inventory[name] / total * 100, 1)
        print(f"Item {name} represents {percentage}%")
    most, least = find_extremes(inventory)
    print(f"Item most abundant: {most} with quantity {inventory[most]}")
    print(f"Item least abundant: {least} with quantity {inventory[least]}")
    inventory.update({"magic_item": 1})
    print(f"Updated inventory: {inventory}")


if __name__ == "__main__":
    main()
