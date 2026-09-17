class Plant:
    class Stats:
        def __init__(self):
            self.grow_calls = 0
            self.age_calls = 0
            self._show_calls = 0

        def record_grow(self):
            self.grow_calls += 1

        def record_age(self):
            self.age_calls += 1

        def record_show(self):
            self._show_calls += 1

        def display_stats(self):
            print(f"Grow calls: {self.grow_calls}, Age calls: {self.age_calls}, Show calls: {self._show_calls}")

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
        self._stats = Plant.Stats()

    @classmethod
    def anonymous(cls):
        return cls(name="Anonymous")

    @staticmethod
    def is_older_than_a_year(days_old):
        return days_old > 365

    def show(self):
        self._stats.record_show()
        print((f"{self._name}: {self._height:.1f} cm, {self._days_old} days"))

    def grow(self, cm = None):
        self._stats.record_grow()
        if cm is None:
            remaining = self._max_height - self._height
            self._height += remaining * (self._growth_rate - 1)
            if self._height > self._max_height:
                self._height = self._max_height
        else:
            self._height += cm

    def age(self, days = 1):
        self._stats.record_age()
        self._days_old += days

    def simulate_growth(self, days):
        print(f"Simulating growth for {days} days.")
        for _ in range(days):
            self.grow()
            self.age()

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

    def get_name(self):
        return self._name

    def get_stats(self):
        return self._stats

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
        super().show()
        print((f"-> Petal Color: {self._petal_color}"))

class Seed(Flower):
    def __init__(self, name = "Black Lotus", height=0, age=0, growth_rate=1, color="black", seeds_per_bloom=10):
        super().__init__(name, height, age, growth_rate, petal_color=color)
        self._seeds_per_bloom = seeds_per_bloom
        self._seeds = 0

    def bloom(self):
        super().bloom()
        self._seeds += self._seeds_per_bloom
        print(f"  {self._seeds} seeds produced")

    def show(self):
        super().show()
        print(f"-> Seeds: {self._seeds}")


class Tree(Plant):
    class Status(Plant.Stats):
        def __init__(self):
            super().__init__()
            self._shade_calls = 0

        def record_shade(self):
            self._shade_calls += 1

        def display(self):
            super().display()
            print(f"Shade produced {self._shade_calls} times")

    def __init__(self, name = "Oak", height = 600, age = 360, growth_rate = 1.5, max_height = 1200, trunk_diameter = 150):
        super().__init__(name, height, age, growth_rate, max_height)
        self._trunk_diameter = trunk_diameter
        self.set_trunk_diameter(trunk_diameter)

    def set_trunk_diameter(self, trunk_diameter):
        if (trunk_diameter < 0):
            print("Error: Trunk diameter cannot be negative. Setting trunk diameter to 0.")
            trunk_diameter = 0
        self._trunk_diameter = trunk_diameter

    def produce_shade(self):
        print(f"{self._name} is producing shade. The shade is {self._height} cm tall and {self._trunk_diameter} cm wide.")

    def show(self):
        super().show()
        print((f"-> Trunk Diameter: {self._trunk_diameter} cm"))

class Vegetable(Plant):
    def __init__(self, name = "Pumpkin", height = 20, age = 40, growth_rate = 1.5, max_height = 200, harvest_season = "Fall", nutritional_value = 30):
        super().__init__(name, height, age, growth_rate, max_height)
        self._harvest_season = "Fall"
        self._nutritional_value = 30

        self.set_harvest_season(harvest_season)
        self.set_nutritional_value(nutritional_value)

    def grow(self, cm = None):
        super().grow(cm)
        self.set_nutritional_value(self._nutritional_value + 2)

    def age(self, days = 1):
        super().age(days)
        self.set_nutritional_value(self._nutritional_value + days)

    def set_harvest_season(self, harvest_season):
        self._harvest_season = harvest_season

    def set_nutritional_value(self, nutritional_value):
        if (nutritional_value < 0):
            print("Error: Nutritional value cannot be negative. Setting nutritional value to 0.")
            nutritional_value = 0
        self._nutritional_value = nutritional_value

    def show(self):
        super().show()
        print((f"-> Harvest Season: {self._harvest_season}, Nutritional Value: {self._nutritional_value}"))

def display_statistics(plant):
    print(f"Statistics for {plant.get_name()} ({type(plant).__name__}):")
    plant.get_stats().display_stats()

if __name__ == "__main__":
    print("== Garden Analytics ==")
    flower = Flower()
    tree = Tree()
    vegetable = Vegetable()
    seed = Seed()

    print("== Flower ==")
    print("Growing the flower...")
    flower.simulate_growth(5)
    flower.bloom()
    flower.show()
    display_statistics(flower)

    print("== Tree ==")
    print("Growing the tree...")
    tree.simulate_growth(10)
    tree.produce_shade()
    tree.show()
    display_statistics(tree)

    print("== Vegetable ==")
    print("Growing the vegetable...")
    vegetable.simulate_growth(7)
    vegetable.show()
    display_statistics(vegetable)

    print("== Seed ==")
    print("Growing the seed...")
    seed.simulate_growth(3)
    seed.show()
    display_statistics(seed)
    print("No seeds produced yet, making it bloom!")
    seed.bloom()
    seed.show()
    print("Displaying updated statistics for the seed...")
    display_statistics(seed)