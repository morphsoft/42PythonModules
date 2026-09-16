def ft_water_reminder():
	days = int(input("Days since watering: "))
	if (days <= 2):
		print("The plants are fine!")
	else:
		print("Water the plants!")
