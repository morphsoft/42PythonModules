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

class Flower(Plant):
    def __init__(self, name = "Black Lotus", height = 1, age = 0, growth_rate = 1.5, max_height = 200, petal_color = "Black"):
        super().__init__(name, height, age, growth_rate, max_height)
        self._petal_color = "Black"
        self.set_petal_color(petal_color)

    def set_petal_color(self, petal_color):
        self._petal_color = petal_color

    def bloom(self):
        print(f"{self._name} is blooming with {self._petal_color} petals.")

    def show(self):
        print((f"{self._name}: {self._height:.1f} cm, {self._days_old} days, Petal Color: {self._petal_color}"))

class Tree(Plant):
    def __init__(self, name = "Oak", height = 600, age = 360, growth_rate = 1.5, max_height = 1200, trunk_diameter = 150):
        super().__init__(name, height, age, growth_rate, max_height)
        self.trunk_diameter = 150
        self.set_trunk_diameter(trunk_diameter)

    def set_trunk_diameter(self, trunk_diameter):
        if (trunk_diameter < 0):
            print("Error: Trunk diameter cannot be negative. Setting trunk diameter to 0.")
            trunk_diameter = 0
        self._trunk_diameter = trunk_diameter

    def produce_shade(self):
        print(f"{self._name} is producing shade. The shade is {self._height} cm tall and {self._trunk_diameter} cm wide.")

    def show(self):
        print((f"{self._name}: {self._height:.1f} cm, {self._days_old} days, Trunk Diameter: {self._trunk_diameter} cm"))

class Vegetable(Plant):
    def __init__(self, name = "Pumpkin", height = 20, age = 40, growth_rate = 1.5, max_height = 200, harvest_season = "Fall", nutritional_value = 30):
        super().__init__(name, height, age, growth_rate, max_height)
        self._harvest_season = "Fall"
        self._nutritional_value = 30

        self.set_harvest_season(harvest_season)
        self.set_nutritional_value(nutritional_value)

    def set_harvest_season(self, harvest_season):
        self._harvest_season = harvest_season

    def set_nutritional_value(self, nutritional_value):
        if (nutritional_value < 0):
            print("Error: Nutritional value cannot be negative. Setting nutritional value to 0.")
            nutritional_value = 0
        self._nutritional_value = nutritional_value

    def show(self):
        print((f"{self._name}: {self._height:.1f} cm, {self._days_old} days, Harvest Season: {self._harvest_season}, Nutritional Value: {self._nutritional_value}"))

if __name__ == "__main__":
    print(f"== Garden Plant Types ==")
    flower = Flower()
    tree = Tree()
    vegetable = Vegetable()

    print(f"\n== Flower ==")
    flower.show()
    flower.bloom()
    print(f"\n== Tree ==")
    tree.show()
    tree.produce_shade()
    print(f"\n== Vegetable ==")
    vegetable.show()