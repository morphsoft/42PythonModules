class Plant:
    def __init__(self, name: str = "Black Lotus", height: float = 1,
                 age: int = 0, growth_rate: float = 1.5,
                 max_height: float = 200) -> None:
        self._height: float = 0
        self._days_old = 0
        self._growth_rate: float = 1
        self._max_height: float = 1
        self._name = ""

        self.set_name(name)
        self.set_max_height(max_height)
        self.set_height(height)
        self.set_age(age)
        self.set_growth_rate(growth_rate)

    def show(self, prefix: str = "") -> None:
        height = f"{self._height:.1f}cm"
        age = f"{self._days_old} days old"
        print((f"{prefix}{self._name}: {height}, {age}"))

    def grow(self, cm: float | None = None) -> None:
        if cm is None:
            remaining = self._max_height - self._height
            self._height += remaining * (self._growth_rate - 1)
            if self._height > self._max_height:
                self._height = self._max_height
        else:
            self._height += cm

    def age(self, days: int = 1) -> None:
        self._days_old += days

    def simulate_growth(self, days: int) -> None:
        self.show()
        for day in range(days):
            print(f"=== Day {day + 1} ===")
            self.grow()
            self.age()
            self.show()

    def set_height(self, height: float) -> None:
        if (height < 0):
            print(f"{self._name}: Error, height can't be negative")
            print("Height update rejected")
            return
        if height > self._max_height:
            self._height = self._max_height
        else:
            self._height = height

    def set_max_height(self, max_height: float) -> None:
        if (max_height < 0):
            print(f"{self._name}: Error, max height can't be negative")
            print("Max height update rejected")
            return
        self._max_height = max_height
        if self._height > self._max_height:
            self._height = self._max_height

    def set_growth_rate(self, growth_rate: float) -> None:
        if (growth_rate < 0):
            print(f"{self._name}: Error, growth rate can't be negative")
            print("Growth rate update rejected")
            return
        self._growth_rate = growth_rate

    def set_age(self, age: int) -> None:
        if (age < 0):
            print(f"{self._name}: Error, age can't be negative")
            print("Age update rejected")
            return
        self._days_old = age

    def set_name(self, name: str) -> None:
        self._name = name

    def get_height(self) -> float:
        return self._height

    def get_age(self) -> int:
        return self._days_old


class Flower(Plant):
    def __init__(self, name: str = "Black Lotus", height: float = 1,
                 age: int = 0, growth_rate: float = 1.5,
                 max_height: float = 200, petal_color: str = "Black") -> None:
        self.set_petal_color(petal_color)
        self._bloomed = False
        super().__init__(name, height, age, growth_rate, max_height)

    def set_petal_color(self, petal_color: str) -> None:
        self._petal_color = petal_color

    def bloom(self) -> None:
        self._bloomed = True

    def show(self, prefix: str = "") -> None:
        super().show(prefix)
        print(f" Color: {self._petal_color}")
        if self._bloomed:
            print(f" {self._name} is blooming beautifully!")
        else:
            print(f" {self._name} has not bloomed yet")


class Tree(Plant):
    def __init__(self, name: str = "Oak", height: float = 600,
                 age: int = 360, growth_rate: float = 1.5,
                 max_height: float = 1200,
                 trunk_diameter: float = 150) -> None:
        self.set_trunk_diameter(trunk_diameter)
        super().__init__(name, height, age, growth_rate, max_height)

    def set_trunk_diameter(self, trunk_diameter: float) -> None:
        if (trunk_diameter < 0):
            print("""Error: Trunk diameter cannot be negative.
Setting trunk diameter to 0.""")
            trunk_diameter = 0
        self._trunk_diameter = trunk_diameter

    def produce_shade(self) -> None:
        print(f"Tree {self._name} now produces a shade of "
              f"{self._height:.1f}cm long and "
              f"{self._trunk_diameter:.1f}cm wide.")

    def show(self, prefix: str = "") -> None:
        super().show(prefix)
        print(f" Trunk diameter: {self._trunk_diameter:.1f}cm")


class Vegetable(Plant):
    def __init__(self, name: str = "Pumpkin", height: float = 20,
                 age: int = 40, growth_rate: float = 1.5,
                 max_height: float = 200, harvest_season: str = "Fall",
                 nutritional_value: int = 0) -> None:
        self.set_harvest_season(harvest_season)
        self.set_nutritional_value(nutritional_value)
        super().__init__(name, height, age, growth_rate, max_height)

    def grow(self, cm: float | None = None) -> None:
        super().grow(cm)
        self.set_nutritional_value(self._nutritional_value + 2)

    def age(self, days: int = 1) -> None:
        super().age(days)
        self.set_nutritional_value(self._nutritional_value + days)

    def set_harvest_season(self, harvest_season: str) -> None:
        self._harvest_season = harvest_season

    def set_nutritional_value(self, nutritional_value: int) -> None:
        if (nutritional_value < 0):
            print("""Error: Nutritional value cannot be negative.
Setting nutritional value to 0.""")
            nutritional_value = 0
        self._nutritional_value = nutritional_value

    def show(self, prefix: str = "") -> None:
        super().show(prefix)
        print(f" Harvest season: {self._harvest_season}")
        print(f" Nutritional value: {self._nutritional_value}")


if __name__ == "__main__":
    print("=== Garden Plant Types ===")
    print("=== Flower")
    rose = Flower("Rose", 15, 10, petal_color="red")
    rose.show()
    print("[asking the rose to bloom]")
    rose.bloom()
    rose.show()

    print("\n=== Tree")
    oak = Tree("Oak", 200, 365, trunk_diameter=5)
    oak.show()
    print("[asking the oak to produce shade]")
    oak.produce_shade()

    print("\n=== Vegetable")
    tomato = Vegetable("Tomato", 5, 10, harvest_season="April")
    tomato.show()
    print("[make tomato grow and age for 20 days]")
    for _ in range(20):
        tomato.grow(2.1)
        tomato.age()
    tomato.show()
