def ft_count_harvest_recursive(daysgone: int = 1,
                               deadline: int | None = None) -> None:
    if (deadline is None):
        deadline = int(input("Days until harvest: "))
    if (daysgone > deadline):
        print("Harvest time!")
        return
    print("Day", daysgone)
    ft_count_harvest_recursive(daysgone + 1, deadline)
