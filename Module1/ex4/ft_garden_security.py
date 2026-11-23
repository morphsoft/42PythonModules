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

        self.show(prefix="Plant created: ")

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


if __name__ == "__main__":
    print("=== Garden Security System ===")
    rose = Plant("Rose", 15, 10)
    print()
    rose.set_height(25)
    print(f"Height updated: {rose.get_height()}cm")
    rose.set_age(30)
    print(f"Age updated: {rose.get_age()} days")
    print()
    rose.set_height(-5)
    rose.set_age(-3)
    print()
    rose.show(prefix="Current state: ")
