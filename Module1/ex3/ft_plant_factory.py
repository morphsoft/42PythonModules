class Plant:
    def __init__(self, name: str, height: float, age: int = 0,
                 growth_rate: float = 1, max_height: float = 100) -> None:
        self.name = name
        self.height = height
        self.days_old = age
        self.growth_rate = growth_rate
        self.max_height = max_height
        self.show(prefix="Created: ")

    def show(self, prefix: str = "") -> None:
        height = f"{self.height:.1f}cm"
        age = f"{self.days_old} days old"
        print((f"{prefix}{self.name}: {height}, {age}"))

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
    print("=== Plant Factory Output ===")
    rose = Plant("Rose", 5, 5, growth_rate=1.1, max_height=30)
    cactus = Plant("Cactus", 10, 15, growth_rate=1.05, max_height=50)
    violet = Plant("Violet", 3, 20, growth_rate=1.2, max_height=20)
    orchid = Plant("Orchid", 4, 574, growth_rate=1.15, max_height=25)
    black_lotus = Plant("Black Lotus", 2, 1002, growth_rate=1.3, max_height=15)
