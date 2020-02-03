from items import Item, Food, Weapon

class Store:
    def __init__(self, vault = 50, stock=[Weapon('Short sword', 'It\'s sharp.', 10, 'Sword', 5), Food('Stale bread', 'It\'s stale.', 1, 'Bread', 2)]):
        self.stock = stock

    def buy(self):
        print(f"You have bought {self.stock[0].name}")

    def sell(self):
        print(f"You have sold {self.stock[0].name}")