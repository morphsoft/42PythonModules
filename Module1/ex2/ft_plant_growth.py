class Plant:
    def __init__(self, name: str, height: float, age: int = 0,
                 growth_rate: float = 1, max_height: float = 100) -> None:
        self.name = name
        self.height = height
        self.days_old = age
        self.growth_rate = growth_rate
        self.max_height = max_height

    def show(self) -> None:
        print((f"{self.name}: {self.height:.1f}cm, {self.days_old} days old"))

    def grow(self, cm: float | None = None) -> None:
        if cm is None:
            remaining = self.max_height - self.height
            self.height += round(remaining * (self.growth_rate - 1), 1)
            if self.height > self.max_height:
                self.height = self.max_height
        else:
            self.height += cm

    def age(self, days: int = 1) -> None:
        self.days_old += days

    def simulate_growth(self, days: int) -> None:
        self.show()
        for day in range(days):
            print(f"=== Day {day + 1} ===")
            self.grow()
            self.age()
            self.show()


if __name__ == "__main__":
    print("=== Garden Plant Growth ===")
    rose = Plant("Rose", 25, 30, growth_rate=1.1, max_height=35)
    start_height = rose.height
    rose.simulate_growth(7)
    print(f"Growth this week: {round(rose.height - start_height, 1)}cm")
