import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request, render_template, make_response
# from pusher import Pusher
# from decouple import config

from room import Room
from player import Player
from world import World
from items import Item, Food, Weapon
from store import Store

# Look up decouple for config variables
# pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))

world = World()
# world.print_rooms()

app = Flask(__name__)

# CORS(app, supports_credentials = True)
# app.config['CORS_ALLOW_HEADERS'] = "Content-Type"
# app.config['CORS_RESOURCES'] = {r"/": {"origins": "https://client-lilac.now.sh/"}}

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


def get_player_by_ip(world, user):
    player = world.get_player_by_username(user)
    return player


# test endpoint
@app.route('/', methods=['GET'])
def test_method():
    return request.headers.get('X-Forwarded-For', request.remote_addr)


@app.route('/api/instantiate/', methods=['POST'])
def instantiate():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        user = request.environ['REMOTE_ADDR']
    else:
        user = request.environ['HTTP_X_FORWARDED_FOR']

    response = world.add_player(user)

    if 'error' in response:
        return jsonify("Registration error", response), 500
    else:
        return jsonify(response), 200

@app.route('/api/adv/init/', methods=['GET'])
def init():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        user = request.environ['REMOTE_ADDR']
    else:
        user = request.environ['HTTP_X_FORWARDED_FOR']

    player = get_player_by_ip(world, user)
    if player is None:
        response = {'error': "Malformed auth header"}
        return response, 500

    response = {
        'IP': player.username,
        'id': player.current_room.id,
        'title': player.current_room.name,
        'description': player.current_room.description,
        'exits': player.current_room.get_exits(),
        'items': player.current_room.get_items()
    }
    # print('THIS IS THE ROOM: ', player.current_room)
    return jsonify(response), 200


@app.route('/api/adv/move/', methods=['POST'])
def move():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        user = request.environ['REMOTE_ADDR']
    else:
        user = request.environ['HTTP_X_FORWARDED_FOR']

    player = get_player_by_ip(world, user)

    if player is None:
        response = {'error': "Malformed auth header"}
        return jsonify(response), 500

    values = request.get_json()
    required = ['direction']

    if not all(k in values for k in required):
        response = {'message': "Missing Values"}
        return jsonify(response), 400

    direction = values.get('direction')
    if player.travel(direction):
        response = {
            'title': player.current_room.name,
            'description': player.current_room.description,
        }
        return jsonify(response), 200
    else:
        response = {
            'error': "You cannot move in that direction.",
        }
        return jsonify(response), 500


@app.route('/api/adv/take/', methods=['POST'])
def take_item():
    # IMPLEMENT THIS
    # {
    #   "item_name":"Torch"
    # }

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        user = request.environ['REMOTE_ADDR']
    else:
        user = request.environ['HTTP_X_FORWARDED_FOR']

    player = get_player_by_ip(world, user)

    if player is None:
        response = {'error': "Malformed auth header"}
        return response, 500

    values = request.get_json()
    items = player.current_room.items

    for item in items:
        if item.name.lower() == values['item_name'].lower():
            player.add_to_inventory(item)
            # print('THIS IS THE ITEM: ', item.name)
            player.current_room.items.remove(item)
            return jsonify(f"You have picked up {item.name}"), 200
    return jsonify(f"{values['item_name']} not found"), 500


@app.route('/api/adv/drop/', methods=['POST'])
def drop_item():
    # IMPLEMENT THIS
    # {
    #   "item":"{name: "Short sword", price: 5, description: "It's sharp."}"
    # }
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        user = request.environ['REMOTE_ADDR']
    else:
        user = request.environ['HTTP_X_FORWARDED_FOR']

    player = get_player_by_ip(world, user)

    if player is None:
        response = {'error': "Malformed auth header"}
        return response, 500

    values = request.get_json()
    inventory = player.inventory

    for item in inventory:
        if item.name.lower() == values['item_name'].lower():
            player.inventory.remove(item)
            player.current_room.items.append(item)
            return jsonify(f"You have dropped {item.name}"), 200
    return jsonify(f"{values['item_name']} not found"), 500


@app.route('/api/adv/inventory/', methods=['GET'])
def inventory():
    # IMPLEMENT THIS
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        user = request.environ['REMOTE_ADDR']
    else:
        user = request.environ['HTTP_X_FORWARDED_FOR']

    player = get_player_by_ip(world, user)

    if player is None:
        response = {'error': "Malformed auth header"}
        return response, 500
    
    # response = {
    #     'name': player.coin_purse,
    #     'description': 
    # }
    response = []
    for i in range(len(player.inventory)):
        if (type(player.inventory[i]) is Weapon):
            response.append({'name': player.inventory[i].name, 'description': player.inventory[i].description, 'price': player.inventory[i].price, 'weapon_type': player.inventory[i].weapon_type, 
                            'damage': player.inventory[i].damage})
        elif (type(player.inventory[i]) is Food):
            response.append({'name': player.inventory[i].name, 'description': player.inventory[i].description, 'price': player.inventory[i].price, 'food_type': player.inventory[i].food_type, 
                            'healing_amount': player.inventory[i].healing_amount})
        elif (type(player.inventory[i]) is Item):
            response.append({'name': player.inventory[i].name, 'description': player.inventory[i].description, 'price': player.inventory[i].price})
    
    return jsonify({'Inventory': response, 'Money': player.coin_purse}), 200


@app.route('/api/adv/buy/', methods=['POST'])
def buy_item():
    # IMPLEMENT THIS
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        user = request.environ['REMOTE_ADDR']
    else:
        user = request.environ['HTTP_X_FORWARDED_FOR']

    player = get_player_by_ip(world, user)

    if player is None:
        response = {'error': "Malformed auth header"}
        return response, 500

    values = request.get_json()
    if (player.current_room.store is not None):
        stock = player.current_room.store.stock
    else:
        return jsonify("There's no store here!"), 500

    for item in stock:
        if item.name.lower() == values['item_name'].lower():
            if (item.price <= player.coin_purse):
                player.add_to_inventory(item)
                player.coin_purse -= item.price
                player.current_room.store.vault += item.price
                player.current_room.store.stock.remove(item)
                return jsonify(f"You have bought up {item.name}. You have {player.coin_purse} gold coins left."), 200
            else:
                return jsonify('You do not have enough gold coins to buy that item.'), 500
    return jsonify(f"{values['item_name']} not found"), 500
        

@app.route('/api/adv/sell/', methods=['POST'])
def sell_item():
    # IMPLEMENT THIS
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        user = request.environ['REMOTE_ADDR']
    else:
        user = request.environ['HTTP_X_FORWARDED_FOR']

    player = get_player_by_ip(world, user)

    if player is None:
        response = {'error': "Malformed auth header"}
        return response, 500

    values = request.get_json()
    if (player.current_room.store is not None):
        inventory = player.inventory
        stock = player.current_room.store.stock
    else:
        return jsonify("There's no store here!"), 500

    for item in inventory:
        if item.name.lower() == values['item_name'].lower():
            if (item.price <= player.current_room.store.vault):
                player.inventory.remove(item)
                stock.append(item)
                player.coin_purse += item.price
                player.current_room.store.vault -= item.price
                return jsonify(f"You have sold your {item.name}. You have {player.coin_purse} gold coins left."), 200
            else:
                return jsonify('Store does not have enough gold coins to buy that item from you.'), 500
    return jsonify(f"{values['item_name']} not found"), 500

@app.route('/api/adv/store', methods=['GET'])
def check_store():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        user = request.environ['REMOTE_ADDR']
    else:
        user = request.environ['HTTP_X_FORWARDED_FOR']

    player = get_player_by_ip(world, user)
    
    if player is None:
        response = {'error': "Malformed auth header"}
        return response, 500

    if not player.current_room.store:
        return jsonify('There is no store in this room!'), 500

    stock = player.current_room.store.stock
    response = []
    for i in range(len(stock)):
        if (type(stock[i]) is Weapon):
            response.append({'name': stock[i].name, 'description': stock[i].description, 'price': stock[i].price, 'weapon_type': stock[i].weapon_type, 
                            'damage': stock[i].damage})
        elif (type(stock[i]) is Food):
            response.append({'name': stock[i].name, 'description': stock[i].description, 'price': stock[i].price, 'food_type': stock[i].food_type, 
                            'healing_amount': stock[i].healing_amount})
        else:
            response.append({'name': stock[i].name, 'description': stock[i].description, 'price': stock[i].price})
    
    return jsonify({'Stock': response}), 200


@app.route('/api/adv/rooms', methods=['GET'])
def rooms():
    # IMPLEMENT THIS
    response = {'rooms': world.print_rooms()}
    return jsonify(response), 200


@app.route('/api/adv/grid', methods=['GET'])
def grid():
    # IMPLEMENT THIS
    response = {'grid': world.get_matrix()}
    return jsonify(response), 200
    
# Run the program on port 5000
if __name__ == '__main__':
    app.run(debug=False, port=5000)
