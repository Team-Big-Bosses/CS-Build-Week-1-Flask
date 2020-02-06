from room import Room
from player import Player
from store import Store
from items import Item, Weapon, Food
import random
import math
import bcrypt
import pandas as pd


levels = pd.read_csv('room-info.csv')

item_list = [Item('Pile of Gold', 'Contains several coins', 20),
            Item('Ring', 'Size 8', 15), Item('Gem', 'Beautifully polished', 50),
            Item('Crown', 'Used to adorn royalty', 150), Item('Scroll', 'Just says kek', 1),
            Item('Potion', 'Used to increase health', 25), Item('Dice', 'YAHTZEE!', 2),
            Weapon('Silver Sword', "A Witcher's favorite", 20, 'sword', 100),
            Weapon('Wooden Spear', 'Longer than a sword', 25, 'spear', 15),
            Weapon('Wooden Shield', 'Good against arrows', 13, 'shield', 3),
            Weapon('Heavy Book', 'Use the power of knowledge!', 5, 'Book', 1),
            Weapon('Thick rope', 'Very short range weapon', 2, 'rope', 60),
            Weapon('Battle Axe', 'Small stick, big blade', 20, 'axe', 25),
            Food('Apple', 'Red fruit', 2, 'small', 5), Food('Mushroom', 'Probably not poisoned', 1, 'small', 1),
            Food('Root', 'Yum...fiber', 1, 'healthy', 15), Food('Green Leaf', 'You need the nutrients', 1, 'healthy', 15),
            Food('Berries', 'Berries on a stick', 5, 'healthy', 10)]

class World:
    def __init__(self):
        self.grid = None
        self.height = 0
        self.length = 0
        self.starting_room = None
        self.rooms = {}
        self.players = {}
        self.create_world()
        self.password_salt = bcrypt.gensalt()

    def add_player(self, username, password1, password2):
        if password1 != password2:
            return {'error': "Passwords do not match"}
        elif len(username) <= 2:
            return {'error': "Username must be longer than 2 characters"}
        elif len(password1) <= 5:
            return {'error': "Password must be longer than 5 characters"}
        elif self.get_player_by_username(username) is not None:
            return {'error': "Username already exists"}
        password_hash = bcrypt.hashpw(password1.encode(), self.password_salt)
        player = Player(username, self.starting_room, password_hash)
        self.players[player.auth_key] = player
        return {'key': player.auth_key}

    def get_player_by_auth(self, auth_key):
        if auth_key in self.players:
            return self.players[auth_key]
        else:
            return None

    def get_player_by_username(self, username):
        for auth_key in self.players:
            if self.players[auth_key].username == username:
                return self.players[auth_key]
        return None

    def authenticate_user(self, username, password):
        user = self.get_player_by_username(username)
        print('user: ', user)
        if user is None:
            return None
        password_hash = bcrypt.hashpw(password.encode() ,self.password_salt)
        if user.password_hash == password_hash:
            return user
        return None

    def create_world2(self):
        self.grid = [None] * 10
        self.width = 10
        self.height = 10
        for i in range(len(self.grid)):
            self.grid[i] = [None] * self.width

        x = -1 # (this will become 0 on the first step)
        y = 0
        room_count = 0

        exits = random.randint(0,14)  
        direction = 1

        previous_room = None

        while (room_count < 100):
            if (exits < 4):
                # one exit rooms
                if (exits == 0):
                    pass
                elif (exits == 1):
                    pass
                elif (exits == 2):
                    pass
                else:
                    pass
            elif (exits >= 4 and exits < 10):
                # two exit rooms
                if (exits == 4):
                    pass
                elif (exits == 5):
                    pass
                elif (exits == 6):
                    pass
                elif (exits == 7):
                    pass
                elif (exits == 8):
                    pass
                else:
                    pass
            elif (exits >= 10 and exits < 14):
                # three exit rooms
                if (exits == 10):
                    pass
                elif (exits == 11):
                    pass
                elif (exits == 12):
                    pass
                else:
                    pass
            else:
                # four exit room
                pass 


    def create_world(self):
        # Code from Brett that has been partially modified
        # Initializing the grid
        self.grid = [None] * 10
        self.width = 10
        self.height = 10
        for i in range(len(self.grid)):
            self.grid[i] = [None] * self.width

        # Start from lower-left corner (0,0)
        x = -1 # (this will become 0 on the first step)
        y = 0
        room_count = 0
        # Start generating rooms to the east
        direction = 1  # 1: east, -1: west
        # While there are rooms to be created...
        previous_room = None
        while room_count < 100:
            # Calculate the direction of the room to be created
            if direction > 0 and x < 9:
                room_direction = "e"
                x += 1
            elif direction < 0 and x > 0:
                room_direction = "w"
                x -= 1
            else:
                # If we hit a wall, turn north and reverse direction
                room_direction = "n"
                y += 1
                direction *= -1
            # Create a room in the given direction
            # Need to figure out how to do store and Treasure room
            rand_num = random.randint(0, 14)
            room = Room(levels['name'][rand_num], levels['description'][rand_num], room_count, x, y, items=[random.choice(item_list), random.choice(item_list)])
            self.grid[y][x] = room
            # room.save()
            # Connect the new room to the previous room
            if previous_room is not None:
                previous_room.connect_rooms(room_direction, room)
                
            # Update iteration variables
            previous_room = room
            room_count += 1
            print(f'room: {room}')
            self.starting_room = self.grid[0][0]


    def print_rooms(self):
        '''
        Print the rooms in room_grid in ascii characters.
        '''
        # Add top border
        str = "# " * ((3 + self.width * 5) // 2) + "\n"
        # The console prints top to bottom but our array is arranged
        # bottom to top.
        #
        # We reverse it so it draws in the right direction.
        reverse_grid = list(self.grid) # make a copy of the list
        reverse_grid.reverse()
        for row in reverse_grid:
            # PRINT NORTH CONNECTION ROW
            str += "#"
            for room in row:
                if room is not None and room.n_to != 0:
                    str += "  |  "
                else:
                    str += "     "
            str += "#\n"
            # PRINT ROOM ROW
            str += "#"
            for room in row:
                if room is not None and room.w_to != 0:
                    str += "-"
                else:
                    str += " "
                if room is not None:
                    str += f"{room.id}".zfill(3)
                else:
                    str += "   "
                if room is not None and room.e_to != 0:
                    str += "-"
                else:
                    str += " "
            str += "#\n"
            # PRINT SOUTH CONNECTION ROW
            str += "#"
            for room in row:
                if room is not None and room.s_to != 0:
                    str += "  |  "
                else:
                    str += "     "
            str += "#\n"
        # Add bottom border
        str += "# " * ((3 + self.width * 5) // 2) + "\n"
        # Print string
        print(str)

world = World()
world.print_rooms()
