import random
import uuid
from items import Item, Food, Weapon

class Player:
    def __init__(self, ip, starting_room):
        self.username = ip
        self.current_room = starting_room
        self.uuid = uuid.uuid4
        self.coin_purse = 0
        self.inventory = []

    def travel(self, direction, show_rooms = False):
        next_room = self.current_room.get_room_in_direction(direction)
        if next_room is not None:
            self.current_room = next_room
            return True
        else:
            print("You cannot move in that direction.")
            return False

    def add_to_inventory(self, item):
        return self.inventory.append(item)
