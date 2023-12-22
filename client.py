import asyncio
import websockets
import json
import requests
import time
import uuid

service_discovery_url = "http://localhost:6969/"

async def find_server():
    response = requests.request("GET", service_discovery_url + "find_server", headers = {}, data = {})
    if response.status_code == 503:
        return None
    return response.json().get("server_ip")

async def find_server_for_game(game_id):
    response = requests.request("GET", service_discovery_url + "find_server_for_game", headers = {'Content-Type': 'application/json'}, data = json.dumps({"game_id": game_id}))
    if response.status_code == 404:
        return None
    return response.json().get("server_ip")

def notify_game_creation(server_ip, game_id):
    response = requests.request(
        "POST",
        service_discovery_url + "create_game",
        headers={'Content-Type': 'application/json'},
        data=json.dumps({"server_ip": server_ip, "game_id": game_id})
    )
    return response.json()

def notify_game_termination(game_id):
    response = requests.request(
        "DELETE",
        service_discovery_url + "end_game",
        headers={'Content-Type': 'application/json'},
        data=json.dumps({"game_id": game_id})
    )
    return response.json()

def print_menu():
    print("\nWelcome to Terminal Tic-Tac-Toe! \n")
    print("Please choose an option:")
    print("1. Create a Game")
    print("2. Join a Game")
    print("3. Exit \n")

def clear_screen():
    print("\033[H\033[J", end="")

def print_board(state):
    print('-' * (len(state[0]) * 4 + 1))
    for row in state:
        row_display = []
        for cell in row:
            if cell == 1:
                row_display.append('1')
            elif cell == 2:
                row_display.append('2')
            else:
                row_display.append(' ')
        print('| ' + ' | '.join(row_display) + ' |')
        print('-' * (len(row) * 4 + 1))
    print()

async def handle_game(initial_action, server_ip, client_id, game_id):
    async with websockets.connect(f'ws://{server_ip}') as websocket:
        # initial_action will be either "create" or "join"
        # Notify server about creating or joining a game
        await websocket.send(json.dumps({'action': initial_action, 'client_id': client_id, 'game_id': game_id}))

        while True:
            try:
                response = await websocket.recv()
            except:
                print("Game Abandoned.")
                break

            data = json.loads(response)
            action = data['action']

            if "state" in data:
                print_board(data["state"])

            if action == 'play' or action == 'invalid_move':
                if action == 'invalid_move':
                    print("Invalid move. Try again.")

                row, col = map(int, input("Your turn. Enter your move (row col): ").split())
                while row < 0 or row >= 3 or col < 0 or col >= 3:\
                    row, col = map(int, input("Invalid. Enter your move (row col): ").split())

                request_data = {
                    'action': 'move',
                    'client_id': client_id,
                    'game_id': game_id,
                    'row': row,
                    'col': col,
                }
                await websocket.send(json.dumps(request_data))
            elif action == 'wait_for_join':
                print("Waiting for another player to join... \n")
            elif action == 'wait_for_play':
                print("Waiting for the other player... \n")
            elif action == 'win':
                print("Congratulations! You won. \n\n")
                break
            elif action == 'lose':
                print("Game over. You lost. \n\n")
                break
            elif action == 'draw':
                print("It's a draw. \n\n")
                break


async def main():
    # client_id = input("Enter your client ID: ")
    client_id = str(uuid.uuid4())

    print(f"Your Client ID is - {client_id}")

    while True:
        # clear_screen()
        print_menu()
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            print("Finding a server for your game...")
            server_ip = await find_server()
            if not server_ip:
                print("No available servers found. Try again later.")
                continue

            # print(f"Creating a new game on server {server_ip}...")
            print(f"Creating a new game...")
            game_id = str(int(time.time()))
            notify_game_creation(server_ip, game_id)
            print(f"Created game - {game_id}")
            
            await handle_game('create', server_ip, client_id, game_id)
            notify_game_termination(game_id)

        elif choice == '2':
            game_id = input("Enter the game ID you wish to join: ")
            server_ip = await find_server_for_game(game_id)
            if not server_ip:
                print("Invalid game_id. Try again.")
                continue

            print(f"Joining game {game_id}...")
            
            await handle_game('join', server_ip, client_id, game_id)
            notify_game_termination(game_id)

        elif choice == '3':
            print("Exiting the game. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")

# Start the client
if __name__ == "__main__":
    asyncio.run(main())
