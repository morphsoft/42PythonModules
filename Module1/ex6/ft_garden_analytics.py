class Plant:
    class Stats:
        def __init__(self) -> None:
            self._grow_calls = 0
            self._age_calls = 0
            self._show_calls = 0

        def record_grow(self) -> None:
            self._grow_calls += 1

        def record_age(self) -> None:
            self._age_calls += 1

        def record_show(self) -> None:
            self._show_calls += 1

        def display_stats(self) -> None:
            print(f"Stats: {self._grow_calls} grow, "
                  f"{self._age_calls} age, "
                  f"{self._show_calls} show")

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
        self._stats = Plant.Stats()

    @classmethod
    def anonymous(cls) -> "Plant":
        return cls(name="Unknown plant", height=0, age=0)

    @staticmethod
    def is_older_than_a_year(days_old: int) -> bool:
        return days_old > 365

    def show(self) -> None:
        self._stats.record_show()
        print((f"{self._name}: {self._height:.1f}cm, "
               f"{self._days_old} days old"))

    def grow(self, cm: float | None = None) -> None:
        self._stats.record_grow()
        if cm is None:
            remaining = self._max_height - self._height
            self._height += remaining * (self._growth_rate - 1)
            if self._height > self._max_height:
                self._height = self._max_height
        else:
            self._height += cm

    def age(self, days: int = 1) -> None:
        self._stats.record_age()
        self._days_old += days

    def simulate_growth(self, days: int) -> None:
        print(f"Simulating growth for {days} days.")
        for _ in range(days):
            self.grow()
            self.age()

    def show_created_log(self) -> None:
        print(f"Created: {self._name}: {self._height:.1f} cm, "
              f"{self._days_old} days")

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

    def get_name(self) -> str:
        return self._name

    def get_height(self) -> float:
        return self._height

    def get_age(self) -> int:
        return self._days_old

    def get_stats(self) -> "Plant.Stats":
        return self._stats


class Flower(Plant):
    def __init__(self, name: str = "Black Lotus", height: float = 1,
                 age: int = 0, growth_rate: float = 1.5,
                 max_height: float = 200, petal_color: str = "Black") -> None:
        super().__init__(name, height, age, growth_rate, max_height)
        self._petal_color = "Black"
        self._bloomed = False
        self.set_petal_color(petal_color)

    def set_petal_color(self, petal_color: str) -> None:
        self._petal_color = petal_color

    def bloom(self) -> None:
        self._bloomed = True

    def show(self) -> None:
        super().show()
        print(f"  Color: {self._petal_color}")
        if self._bloomed:
            print(f"  {self._name} is blooming beautifully!")
        else:
            print(f"  {self._name} has not bloomed yet")


class Seed(Flower):
    def __init__(self, name: str = "Black Lotus", height: float = 0,
                 age: int = 0, growth_rate: float = 1,
                 color: str = "black", seeds_per_bloom: int = 10) -> None:
        super().__init__(name, height, age, growth_rate, petal_color=color)
        self._seeds_per_bloom = seeds_per_bloom
        self._seeds = 0

    def bloom(self) -> None:
        super().bloom()
        self._seeds += self._seeds_per_bloom

    def show(self) -> None:
        super().show()
        print(f"  Seeds: {self._seeds}")


class Tree(Plant):
    class Status(Plant.Stats):
        def __init__(self) -> None:
            super().__init__()
            self._shade_calls = 0

        def record_shade(self) -> None:
            self._shade_calls += 1

        def display_stats(self) -> None:
            super().display_stats()
            print(f"  {self._shade_calls} shade")

    def __init__(self, name: str = "Oak", height: float = 600,
                 age: int = 360, growth_rate: float = 1.5,
                 max_height: float = 1200,
                 trunk_diameter: float = 150) -> None:
        super().__init__(name, height, age, growth_rate, max_height)
        self._tree_stats = Tree.Status()
        self._stats = self._tree_stats
        self._trunk_diameter = trunk_diameter
        self.set_trunk_diameter(trunk_diameter)

    def set_trunk_diameter(self, trunk_diameter: float) -> None:
        if (trunk_diameter < 0):
            print("Error: Trunk diameter cannot be negative. "
                  "Setting trunk diameter to 0.")
            trunk_diameter = 0
        self._trunk_diameter = trunk_diameter

    def produce_shade(self) -> None:
        self._tree_stats.record_shade()
        print(f"Tree {self._name} now produces a shade of "
              f"{self._height:.1f}cm long and "
              f"{self._trunk_diameter:.1f}cm wide.")

    def show(self) -> None:
        super().show()
        print(f"  Trunk diameter: {self._trunk_diameter:.1f}cm")


class Vegetable(Plant):
    def __init__(self, name: str = "Pumpkin", height: float = 20,
                 age: int = 40, growth_rate: float = 1.5,
                 max_height: float = 200, harvest_season: str = "Fall",
                 nutritional_value: int = 0) -> None:
        super().__init__(name, height, age, growth_rate, max_height)
        self._harvest_season = "Fall"
        self._nutritional_value = 0

        self.set_harvest_season(harvest_season)
        self.set_nutritional_value(nutritional_value)

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
            print("Error: Nutritional value cannot be negative. "
                  "Setting nutritional value to 0.")
            nutritional_value = 0
        self._nutritional_value = nutritional_value

    def show(self) -> None:
        super().show()
        print(f"  Harvest season: {self._harvest_season}")
        print(f"  Nutritional value: {self._nutritional_value}")


def display_statistics(plant: Plant) -> None:
    print(f"[statistics for {plant.get_name()}]")
    plant.get_stats().display_stats()


if __name__ == "__main__":
    print("=== Garden statistics ===")
    print("=== Check year-old")
    print(f"Is 30 days more than a year? -> "
          f"{Plant.is_older_than_a_year(30)}")
    print(f"Is 400 days more than a year? -> "
          f"{Plant.is_older_than_a_year(400)}")

    print("\n=== Flower")
    rose = Flower("Rose", 15, 10, petal_color="red")
    rose.show()
    display_statistics(rose)
    print("[asking the rose to grow and bloom]")
    rose.grow(8)
    rose.bloom()
    rose.show()
    display_statistics(rose)

    print("\n=== Tree")
    oak = Tree("Oak", 200, 365, trunk_diameter=5)
    oak.show()
    display_statistics(oak)
    print("[asking the oak to produce shade]")
    oak.produce_shade()
    display_statistics(oak)

    print("\n=== Seed")
    sunflower = Seed("Sunflower", 80, 45, color="yellow", seeds_per_bloom=42)
    sunflower.show()
    print("[make sunflower grow, age and bloom]")
    sunflower.grow(30)
    sunflower.age(20)
    sunflower.bloom()
    sunflower.show()
    display_statistics(sunflower)

    print("\n=== Anonymous")
    unknown = Plant.anonymous()
    unknown.show()
    display_statistics(unknown)
