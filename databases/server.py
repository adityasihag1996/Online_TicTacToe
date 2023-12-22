from flask import Flask, request, jsonify

from datastore import DataStore
from config import REDIS_HOST, REDIS_PORT, GAME_SERVER_IP_LIST

# Initialise the Datastore
redis_datastore = DataStore(redis_host = REDIS_HOST, redis_port = REDIS_PORT, game_server_list = GAME_SERVER_IP_LIST)

# Initialise the flask app for APIs
app = Flask(__name__)


@app.route('/find_server', methods=['GET'])
def find_server():
    """
    Find an available server, with capacity to host the game.
    """
    server_ip = redis_datastore.find_server()

    if server_ip:
        return jsonify({'server_ip': server_ip}), 200
        
    return jsonify({'message': 'No servers available'}), 503


@app.route('/create_game', methods=['POST'])
def create_game():
    """
    Using a IP, GAME_ID, we host the game on the server, so necessary metadata storage
    """
    server_ip, game_id = request.json.get('server_ip'), request.json.get('game_id')

    redis_datastore.create_game(server_ip, game_id)

    return jsonify({'message': 'Game created', 'game_id': game_id, 'server_ip': server_ip}), 200


@app.route('/find_server_for_game', methods = ['GET'])
def find_server_for_game():
    """
    Given a GAME_ID, find the IP which is hosting the game
    """
    game_id = request.json.get('game_id')

    server_ip = redis_datastore.find_server_for_game(game_id)

    if server_ip:
        return jsonify({'game_id': game_id, 'server_ip': server_ip}), 200
    else:
        return jsonify({'message': 'Game not found'}), 404

@app.route('/end_game', methods = ['DELETE'])
def end_game():
    """
    Game has ended, clean the metadata
    """
    game_id = request.json.get('game_id')

    end_status = redis_datastore.remove_game(game_id)
    
    if end_status:
        return jsonify({'message': 'Game ended', 'game_id': game_id}), 200
    else:
        return jsonify({'message': 'Game not found'}), 404


if __name__ == '__main__':
    app.run(debug = True, host = "localhost", port = 6969)
