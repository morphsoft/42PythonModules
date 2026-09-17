class Plant:
    def __init__(self, name, height, age):
        self.name = name
        self.height = height
        self.age = age

    def show(self):
        print((f"{self.name}: {self.height} cm, {self.age} days"))

if __name__ == "__main__":
    Plant("Rose", 25, 30).show()
    Plant("Sunflower", 80, 45).show()
    Plant("Cactus", 15, 120).show()
    print("== End of Program ==")