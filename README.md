# Online Tic Tac toe
This repository contains a toy TicTacToe game, which can be played online.

The system was developed by keeping scale and independent maintainability in mind.
Highlight of the toy project is, clients connect to game servers using WebSockets.

For simplicity, all modules are present in the same git, ideally, they will on different gits.

## Table of Contents

- [Installation](#Installation)
- [System Architecture](#SystemArchitecture)
- [Usage](#Usage)
- [To-Do](#to-do)
- [Contributing](#contributing)

## Installation
To use this implementation, you will need to have Python >= 3.9 installed on your system, as well as the following Python libraries:

```
git clone https://github.com/adityasihag1996/Online_TicTacToe.git
cd Online_TicTacToe
pip install -r requirements.txt
```

## System Architecture
Each module of the architecture is independently scalable.\
_**First Module**_ is the `Service Discovery`, which helps in finding an available server to host the game instance on.\
Each game server can host a specific amount of games only, so we need to find a server which has capacity to host a gmae when we create a new game.\
When a client tries to create a game, SD looks up in the DB (Redis) to find a server which has space available.

![Sample Image](/sysdes1.jpg "Sample Image Title")

_**Second Module**_ is the `find and play`, which simply establishes a WebSocket connection to a game server, and keeps it until the game is over, or any one of the user abruptly disconnects.

![Sample Image](/sysdes2.jpg "Sample Image Title")

## Usage
You will need to spin up 4 major components:-
- Database
- Service Discovery
- Game Server
- Client

Here's how you can do that.\

```
## Redis database
cd databases
python logic.py

cd ../

## Service Discovery
python service.py

## Game Server
cd game_service
python server.py

cd ../

## Client
python client.py
```

You can modify params of the project in `config.py`.

## To-Do

- [ ] Create a version which used TCP, easier to implement and manage than WebSockets.

## Contributing
Contributions to improve the project are welcome. Please follow these steps to contribute:

- Fork the repository.
- Create a new branch for each feature or improvement.
- Submit a pull request with a comprehensive description of changes.
