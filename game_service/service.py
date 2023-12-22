import asyncio
import websockets
import json
import random
from TicTacToe import TicTacToe


games = {}  # This dict will store game_id to game object mapping
client_to_game = {}  # This dict will store client WebSocket to game_id mapping
game_to_clients = {}  # This dict will store game_id to a list of client WebSockets (players)
client_id_to_clients = {}  # This dict will store client_id to client WebSocket
clients_to_client_id = {}  # This dict will store client WebSocket to client_id


def cleanup(client_id, game_id, websocket):
    """
    Data cleanup
    """
    del games[game_id]
    del game_to_clients[game_id]
    del client_id_to_clients[client_id]
    del client_to_game[websocket]
    del clients_to_client_id[websocket]


async def game_server(websocket, path):
    # The client sends a message with the action 'create', 'join', 'move' and their client_id
    async for message in websocket:
        data = json.loads(message)
        action = data['action']
        client_id = data['client_id']
        
        if action == 'create':
            game_id = data['game_id']

            game = TicTacToe()

            games[game_id] = game
            game_to_clients[game_id] = [websocket]
            client_id_to_clients[client_id] = websocket
            clients_to_client_id[websocket] = client_id
            client_to_game[websocket] = game_id
            game.player1 = client_id
            
            await websocket.send(json.dumps({'action': 'wait_for_join'}))
            
        elif action == 'join':
            game_id = data['game_id']
            if game_id in games:
                game_to_clients[game_id].append(websocket)
                games[game_id].player2 = client_id
                client_id_to_clients[client_id] = websocket
                clients_to_client_id[websocket] = client_id
                client_to_game[websocket] = game_id

                game_state = games[game_id].get_state()

                if random.uniform(0, 1) < 0.5:
                    # player1 starts
                    games[game_id].current_player = games[game_id].player1
                    await asyncio.gather(*[
                        client_id_to_clients[games[game_id].player2].send(json.dumps({'action': 'wait_for_play', 'state': game_state})),
                        client_id_to_clients[games[game_id].player1].send(json.dumps({'action': 'play', 'state': game_state}))
                    ])
                else:
                    games[game_id].current_player = games[game_id].player2
                    await asyncio.gather(*[
                        client_id_to_clients[games[game_id].player1].send(json.dumps({'action': 'wait_for_play', 'state': game_state})),
                        client_id_to_clients[games[game_id].player2].send(json.dumps({'action': 'play', 'state': game_state}))
                    ])
            else:
                await websocket.send(json.dumps({'error': 'Game not found'}))
        
        elif action == 'move':
            game_id = client_to_game[websocket]
            game = games[game_id]
            row = data['row']
            col = data['col']

            move_state = game.move(row, col, client_id)
            if move_state is None:
                # Invalid move
                await websocket.send(json.dumps({'action': 'invalid_move'}))
            else:
                # Valid move, update game state
                game_state = game.get_state()

                if move_state == 0:
                    await websocket.send(json.dumps({'action': 'wait_for_play', 'state': game_state}))
                    for client in game_to_clients[game_id]:
                        if client != websocket:
                            await client.send(json.dumps({'action': 'play', 'state': game_state}))

                if move_state == 1 or move_state == 2:
                    # Player 1 or 2 wins
                    try:
                        await websocket.send(json.dumps({'action': 'win', 'state': game_state}))
                        for client in game_to_clients[game_id]:
                            if client != websocket:
                                await client.send(json.dumps({'action': 'lose', 'state': game_state}))
                    finally:
                        cleanup(client_id, game_id, websocket)

                if move_state == -1:
                    # Game draw
                    draw_message = json.dumps({'action': 'draw', 'state': move_state})
                    try:
                        await asyncio.gather(*[
                            client.send(draw_message)
                            for client in game_to_clients[game_id]
                        ])
                    finally:
                        cleanup(client_id, game_id, websocket)
    
    if websocket.closed:
        client_id = clients_to_client_id[websocket]
        game_id = client_to_game[websocket]

        print(f"Connection Lost to Client - {client_id} ...")
        print(f"Terminating game - {game_id} ...")

        for client in game_to_clients[game_id]:
            if client.closed == False:
                await client.close()
                # await client.send(json.dumps({'action': 'conn_lost'}))

        cleanup(client_id, game_id, websocket)


# Start the server
asyncio.get_event_loop().run_until_complete(
    websockets.serve(game_server, 'localhost', 7001))
asyncio.get_event_loop().run_forever()
