import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request, render_template, make_response
from flask_cors import CORS, cross_origin
# from pusher import Pusher
from decouple import config

from room import Room
from player import Player
from world import World
from items import Item, Food, Weapon
from store import Store

# Look up decouple for config variables
# pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))

world = World()

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


def get_player_by_header(world, auth_header):
    if auth_header is None:
        return None

    auth_key = auth_header.split(" ")
    if auth_key[0] != "Token" or len(auth_key) != 2:
        return None

    player = world.get_player_by_auth(auth_key[1])
    return player


@app.route('/api/registration/', methods=['POST'])
def register():
    # if request.method == 'OPTIONS':
    #     response = make_response()
    #     response.headers['Access-Control-Allow-Origin'] = '*'
    #     response.headers['Access-Control-Allow-Headers'] = '*'
    #     response.headers['Access-Control-Allow-Methods'] = '*'
    #     return response, 200

    values = request.get_json()
    required = ['username', 'password1', 'password2']

    if not all(k in values for k in required):
        response = {'message': "Missing Values"}
        return jsonify(response), 400

    username = values.get('username')
    password1 = values.get('password1')
    password2 = values.get('password2')

    # response = make_response(world.add_player(username, password1, password2))
    # response.headers['Access-Control-Allow-Origin'] = '*'

    response = world.add_player(username, password1, password2)

    if 'error' in response:
        return jsonify("Registration error", response), 500
    else:
        return jsonify(response), 200

# test endpoint
@app.route('/', methods=['GET'])
def test_method():
    return 'Welcome Adventurer'

@app.route('/api/login/', methods=['POST'])
def login():
    # IMPLEMENT THIS
    values = request.get_json()
    required = ['username', 'password']

    if not all(k in values for k in required):
        response = {'message': "Missing Values"}
        return jsonify(response), 400

    username = values.get('username')
    password = values.get('password')

    response = world.authenticate_user(username, password)
    if response is None:
        return jsonify(response), 500
    else:
        return jsonify(response), 200


@app.route('/api/adv/init/', methods=['GET'])
def init():
    player = get_player_by_header(world, request.headers.get("Authorization"))
    if player is None:
        response = {'error': "Malformed auth header"}
        return response, 500

    response = {
        'id': player.current_room.id,
        'title': player.current_room.name,
        'description': player.current_room.description,
        'exits': player.current_room.get_exits()
    }
    # print('THIS IS THE ROOM: ', player.current_room)
    return jsonify(response), 200


@app.route('/api/adv/move/', methods=['POST'])
def move():
    player = get_player_by_header(world, request.headers.get("Authorization"))
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

    player = get_player_by_header(world, request.headers.get("Authorization"))
    if player is None:
        response = {'error': "Malformed auth header"}
        return response, 500

    values = request.get_json()
    items = player.current_room.items

    for item in items:
        if item.name.lower() == values['item_name'].lower():
            player.inventory.append(item)
            print('THIS IS THE ITEM: ', item.name)
            return jsonify(f"You have picked up {item.name}"), 200


@app.route('/api/adv/drop/', methods=['POST'])
def drop_item():
    # IMPLEMENT THIS
    # {
    #   "item":"{name: "Short sword", price: 5, description: "It's sharp."}"
    # }
    player = get_player_by_header(world, request.headers.get("Authorization"))
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
        else:
            return jsonify('Item not found'), 500


@app.route('/api/adv/inventory/', methods=['GET'])
def inventory():
    # IMPLEMENT THIS
    player = get_player_by_header(world, request.headers.get("Authorization"))
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
        else:
            response.append({'name': player.inventory[i].name, 'description': player.inventory[i].description, 'price': player.inventory[i].price})
    
    return jsonify({'Inventory': response}), 200


@app.route('/api/adv/buy/', methods=['POST'])
def buy_item():
    # IMPLEMENT THIS
    player = get_player_by_header(world, request.headers.get("Authorization"))
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
                player.inventory.append(item)
                player.coin_purse -= item.price
                player.current_room.store.vault += item.price
                player.current_room.store.stock.remove(item)
                return jsonify(f"You have bought up {item.name}. You have {player.coin_purse} gold coins left."), 200
            else:
                return jsonify('You do not have enough gold coins to buy that item.'), 500
                

@app.route('/api/adv/sell/', methods=['POST'])
def sell_item():
    # IMPLEMENT THIS
    player = get_player_by_header(world, request.headers.get("Authorization"))
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
                return jsonify(f"You have sold up {item.name}. You have {player.coin_purse} gold coins left."), 200
            else:
                return jsonify('Store does not have enough gold coins to buy that item from you.'), 500


@app.route('/api/adv/store', methods=['GET'])
def check_store():
    player = get_player_by_header(world, request.headers.get("Authorization"))
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


@app.route('/api/adv/rooms/', methods=['GET'])
def rooms():
    # IMPLEMENT THIS
    response = {'error': "Not implemented"}
    return jsonify(response), 400


# Run the program on port 5000
if __name__ == '__main__':
    app.run(debug=False, port=5000)
