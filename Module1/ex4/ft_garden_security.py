class Plant:
    def __init__(self, name = "Black Lotus", height = 1, age = 0, growth_rate = 1.5, max_height = 200):
        self._height = 0
        self._days_old = 0
        self._growth_rate = 1
        self._max_height = 1
        self._name = ""

        self.set_name(name)
        self.set_max_height(max_height)
        self.set_height(height)
        self.set_age(age)
        self.set_growth_rate(growth_rate)

    def show(self):
        print((f"{self._name}: {self._height:.1f} cm, {self._days_old} days"))

    def grow(self, cm = None):
        if cm is None:
            remaining = self._max_height - self._height
            self._height += remaining * (self._growth_rate - 1)
            if self._height > self._max_height:
                self._height = self._max_height
        else:
            self._height += cm

    def age(self, days = 1):
        self._days_old += days

    def simulate_growth(self, days):
        print(f"Simulating growth for {days} days.")
        print(f"=== Day 0 ===")
        self.show()
        for _ in range(days):
            print(f"=== Day {_ + 1} ===")
            self.grow()
            self.age()
            self.show()

    def show_created_log(self):
        print(f"Created: {self._name}: {self._height:.1f} cm, {self._days_old} days")

    def set_height(self, height):
        if (height < 0):
            print("Error: Height cannot be negative. Setting height to 0.")
            height = 0
        if height > self._max_height:
            self._height = self._max_height
        else:
            self._height = height

    def set_max_height(self, max_height):
        if (max_height < 0):
            print("Error: Max height cannot be negative. Setting max height to 0.")
            max_height = 0
        self._max_height = max_height
        if self._height > self._max_height:
            self._height = self._max_height

    def set_growth_rate(self, growth_rate):
        if (growth_rate < 0):
            print("Error: Growth rate cannot be negative. Setting growth rate to 0.")
            growth_rate = 0
        self._growth_rate = growth_rate

    def set_age(self, age):
        if (age < 0):
            print("Error: Age cannot be negative. Setting age to 0.")
            age = 0
        self._days_old = age

    def set_name(self, name):
        self._name = name

if __name__ == "__main__":
    print(f"== Garden Security System ==")
    Plant("Rose", -10, 0, 1.5, 200).show_created_log()
    Plant("Tulip", 5, 1, 1.2, 150).show_created_log()
    Plant("Gilded Lotus", 1, 3, 1.5, -200).show_created_log()
    Plant("Daisy", 3, 0, -1.1, 100).show_created_log()
    Plant().show_created_log()