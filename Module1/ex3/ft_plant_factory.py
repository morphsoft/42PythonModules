class Plant:
    def __init__(self, name, height, age = 0, growth_rate = 1, max_height = 100):
        self.name = name
        self.height = height
        self.days_old = age
        self.growth_rate = growth_rate
        self.max_height = max_height

    def show(self):
        print((f"{self.name}: {self.height:.1f} cm, {self.days_old} days"))

    def grow(self, cm = None):
        if cm is None:
            remaining = self.max_height - self.height
            self.height += remaining * (self.growth_rate - 1)
            if self.height > self.max_height:
                self.height = self.max_height
        else:
            self.height += cm

    def age(self, days = 1):
        self.days_old += days

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
        print(f"Created: {self.name}: {self.height:.1f} cm, {self.days_old} days")

if __name__ == "__main__":
    print("== Plant Factory Output ==")
    rose = Plant("Rose", 5, growth_rate=1.1, max_height=30).show_created_log()
    cactus = Plant("Cactus", 10, growth_rate=1.05, max_height=50).show_created_log()
    violet = Plant("Violet", 3, growth_rate=1.2, max_height=20).show_created_log()
    orchid = Plant("Orchid", 4, growth_rate=1.15, max_height=25).show_created_log()
    black_lotus = Plant("Black Lotus", 2, growth_rate=1.3, max_height=15).show_created_log()
    
    print("== End of Program ==")