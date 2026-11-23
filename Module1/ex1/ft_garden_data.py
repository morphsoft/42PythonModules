class Plant:
    def __init__(self, name: str, height: int, age: int) -> None:
        self.name = name
        self.height = height
        self.age = age

    def show(self) -> None:
        print((f"{self.name}: {self.height}cm, {self.age} days old"))


if __name__ == "__main__":
    print("=== Garden Plant Registry ===")
    Plant("Rose", 25, 30).show()
    Plant("Sunflower", 80, 45).show()
    Plant("Cactus", 15, 120).show()
