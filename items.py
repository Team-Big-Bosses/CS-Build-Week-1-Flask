class Item:
    def __init__(self, name, description, price):
        self.name = name
        self.description = description
        self.price = price

    def __str__(self):
        display_string = f"{self.name}, "
        display_string += f"{self.description}"
        return display_string

class Food(Item):
    def __init__(self, name, description, price, food_type, healing_amount=0):
        super().__init__(name, description, price)
        self.food_type = food_type
        self.healing_amount = healing_amount

class Weapon(Item):
    def __init__(self, name, description, price, weapon_type, damage=0):
        super().__init__(name, description, price)
        self.weapon_type = weapon_type
        self.damage = damage
