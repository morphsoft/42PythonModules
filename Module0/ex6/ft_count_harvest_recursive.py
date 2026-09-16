def ft_count_harvest_recursive(daysgone = None, deadline = None):
	if (deadline == None):
		deadline = int(input("Days until harvest: "))
		daysgone = 0
	if (daysgone == None):
		return
	print("Day " + daysgone)
	if (daysgone == deadline):
		daysgone = None
	daysgone += 1
	ft_count_harvest_recursive(daysgone, deadline)
