from items import Item, Food, Weapon

class Store:
    def __init__(self, stock=[Weapon('Short sword', 'It\'s sharp.', 10, 'Sword', 5), Food('Stale bread', 'It\'s stale.', 1, 'Bread', 2)]):
        self.stock = stock
        self.vault = 1000000
