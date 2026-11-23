def ft_count_harvest_iterative() -> None:
    deadline = int(input("Days until harvest: "))
    days = 0
    while (days < deadline):
        days += 1
        print("Day", days)
    print("Harvest time!")
