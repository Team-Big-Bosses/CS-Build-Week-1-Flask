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
            Item('Ring', 'Size 8', 15), 
            Item('Gem', 'Beautifully polished', 50),
            Item('Crown', 'Used to adorn royalty', 150), 
            Item('Scroll', 'Just says kek', 1),
            Item('Potion', 'Used to increase health', 25), 
            Item('Dice', 'YAHTZEE!', 2),
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
        self.starting_room = None
        self.rooms = [None] * 20
        self.players = {}
        self.init_grid()
        self.create_world(100)
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
            return {'key': user.auth_key}
        return None

    def init_grid(self):
        self.height = 20
        self.grid = [None] * self.height
        self.width = 20
        self.previous_room = None
        
        for i in range(len(self.grid)):
            self.grid[i] = [None] * self.width

    def create_world(self, num_rooms):
        first_x = (self.width // 2) - 1 
        first_y = (self.height // 2) - 1
        x = (self.width // 2) - 1
        y = (self.height // 2) - 1
        room_count = 1
        total_rooms = num_rooms
        past_rooms_list = []
        rooms_list = []
        # Start generating rooms to the east
        # While there are rooms to be created...
        direction_list = [1, 2, 3, 4]
        rand_num = random.randint(0, 12)
        self.starting_room = Room(levels['name'][rand_num], levels['description'][rand_num], room_count, first_x, first_y, items=[random.choice(item_list), random.choice(item_list)])
        self.grid[first_y][first_x] = self.starting_room
        rooms_list.append(self.starting_room)
        previous_room = self.starting_room

        while room_count < total_rooms:
            if len(direction_list) > 0:
                direction = random.choice(direction_list) # 1: North, 2: South, 3: East, 4: West

            if len(direction_list) == 0:
                while len(direction_list) == 0:
                    random_past_coord = random.choice(past_rooms_list)
                    # print(random_past_coord)
                    x = random_past_coord[0]
                    y = random_past_coord[1]
                    # print(x, y)
                    direction_list = [1, 2, 3, 4]
                    direction = random.choice(direction_list) # 1: North, 2: South, 3: East, 4: West
                    
                        
            # Calculate the direction of the room to be created
            if (direction == 1):
                # North
                if ((y+1) < self.height and (y+1) > -1):
                    if self.grid[y+1][x] is None:
                        room_direction = 'n'
                        room_count += 1
                        y += 1
                        direction_list = [1, 2, 3, 4]
                        rand_num = random.randint(0, 12)
                        room = Room(levels['name'][rand_num], levels['description'][rand_num], room_count, x, y, items=[random.choice(item_list), random.choice(item_list)])
                        rooms_list.append(room)
                        past_rooms_list.append([x,y])
                        self.grid[y][x] = room
                        if previous_room is not None:
                            previous_room.connect_rooms(room_direction, room)
                        previous_room = room
                    else:
                        direction_list.remove(1)
                else:
                    direction_list.remove(1)

            elif (direction == 2):
                # South
                if (self.height > (y-1) and (y-1) > -1):
                    if self.grid[y-1][x] is None:
                        room_direction = 's'
                        room_count += 1
                        y -= 1
                        direction_list = [1, 2, 3, 4]
                        rand_num = random.randint(0, 12)
                        room = Room(levels['name'][rand_num], levels['description'][rand_num], room_count, x, y, items=[random.choice(item_list), random.choice(item_list)])
                        rooms_list.append(room)
                        past_rooms_list.append([x,y])
                        self.grid[y][x] = room
                        if previous_room is not None:
                            previous_room.connect_rooms(room_direction, room)
                        previous_room = room
                        
                    else:
                        direction_list.remove(2)
                else:
                    direction_list.remove(2)

            elif (direction == 3):
                # East
                if (x+1) < self.width and (x+1) > -1:
                    if self.grid[y][x+1] is None:
                        room_direction = 'e'
                        room_count += 1
                        x += 1
                        direction_list = [1, 2, 3, 4]
                        rand_num = random.randint(0, 12)
                        room = Room(levels['name'][rand_num], levels['description'][rand_num], room_count, x, y, items=[random.choice(item_list), random.choice(item_list)])
                        rooms_list.append(room)
                        past_rooms_list.append([x,y])
                        self.grid[y][x] = room
                        if previous_room is not None:
                            previous_room.connect_rooms(room_direction, room)
                        previous_room = room
 
                    else:
                        direction_list.remove(3)
                else:
                    direction_list.remove(3)

            else:
                # West
                if (self.width > (x-1) and (x-1) > -1):
                    if self.grid[y][x-1] is None:
                        room_direction = 'w'
                        room_count += 1
                        x -= 1
                        direction_list = [1, 2, 3, 4]
                        rand_num = random.randint(0, 12)
                        room = Room(levels['name'][rand_num], levels['description'][rand_num], room_count, x, y, items=[random.choice(item_list), random.choice(item_list)])
                        rooms_list.append(room)
                        past_rooms_list.append([x,y])
                        self.grid[y][x] = room
                        if previous_room is not None:
                            previous_room.connect_rooms(room_direction, room)
                        previous_room = room
                      
                    else:
                        direction_list.remove(4)
                else:
                    direction_list.remove(4)   

        for y in range(self.height):
            for x in range(self.width):
                if(self.grid[y][x] is not None):
                    # print(self.width, '+', self.height)
                    if ((y+1) < self.height and (y-1) >= 0 and (x+1) < self.width and (x-1) >= 0):
                        if (self.grid[y+1][x] is not None):
                            room = self.grid[y][x]
                            north = self.grid[y+1][x]
                            room.connect_rooms('n', north)
                        if (self.grid[y-1][x] is not None):
                            room = self.grid[y][x]
                            south = self.grid[y-1][x]
                            room.connect_rooms('s', south)
                        if (self.grid[y][x+1] is not None):
                            room = self.grid[y][x]
                            east = self.grid[y][x+1]
                            room.connect_rooms('e', east)
                        if (self.grid[y][x-1] is not None):
                            room = self.grid[y][x]
                            west = self.grid[y][x-1]
                            room.connect_rooms('w', west)
                        
        for room in rooms_list:
            # print(room.id)
            exits = sorted(room.get_exits())
            # print(exits)
            # print()
            # # store rooms - Stores should be in NESW, ES, NE, WS, NW
            if (exits == ['e', 'n', 's', 'w'] or exits == ['e', 's'] or exits == ['e', 'n'] or exits == ['s', 'w'] or exits == ['n', 'w']):
                room.store = Store(stock = [random.choice(item_list), random.choice(item_list)], vault = random.randint(50, 100)) 
                if exits == ['e', 'n', 's', 'w']:
                    room.name = levels['name'][8]
                    room.description = levels['description'][8]
                elif exits == ['e', 's']:
                    room.name = levels['name'][2]
                    room.description = levels['description'][2]
                elif exits == ['e', 'n']:
                    room.name = levels['name'][6]
                    room.description = levels['description'][6]
                elif exits == ['s', 'w']:
                    room.name = levels['name'][1]
                    room.description = levels['description'][1]
                else:
                    room.name = levels['name'][5]
                    room.description = levels['description'][5]

            # tree rooms - Tree room should be in WE, NW
            if (exits == ['e', 'w'] or exits == ['n', 'w']):
                if exits == ['e', 'w']:
                    room.name = levels['name'][4]
                    room.description = levels['description'][4]
                if exits == ['n', 'w']:
                    room.name = levels['name'][11]
                    room.description = levels['description'][11]

            # treasure rooms - Treasure room in N and S(silver) and E and W (Bronze)
            if (exits == ['n'] or exits == ['s'] or exits == ['s'] or exits == ['w']):
                if exits == ['n'] or exits == ['s']:
                    room.name = levels['name'][0]
                    room.description = levels['name'][0]
                    room.items = [item_list[0], item_list[2]]
                if exits == ['e'] or exits == ['w']:
                    room.name = levels['name'][10]
                    room.description = levels['name'][10]
                    room.items = [item_list[0], item_list[1]]

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

        return str

    def init_rooms(self):
        for i in range(len(self.rooms)):
            self.rooms[i] = [None] * 20

    def get_matrix(self):
        self.init_rooms()
        grid = self.grid
        for lists in grid:
            for room in lists:
                if room:
                    # Get room info
                    r_id = room.id
                    n_to = room.n_to
                    s_to = room.s_to
                    e_to = room.e_to
                    w_to = room.w_to
                    directions = {'n': n_to, 's': s_to, 'e': e_to, 'w': w_to}
                    exits = {}
                    for exit in directions:
                        if directions[exit]:
                            exits[exit] = True
                        else:
                            exits[exit] = False
                    x = room.x
                    y = room.y
                    
                    self.rooms[y][x] = {'id': r_id, 'exits': exits, 'coordinates': (x, y)}

        return self.rooms
                    
# world = World()
# world.get_matrix()