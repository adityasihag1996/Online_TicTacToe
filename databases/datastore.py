import redis

from config import MAX_GAMES_PER_SERVER

class DataStore:
    def __init__(self, redis_host = 'localhost', redis_port = 6379, game_server_list = []):
        self.redis_client = redis.Redis(host = redis_host, port = redis_port, db = 0)

        # Initialise the "ServerLoadCountTable" table with zero counts for all IPs of game servers
        for server_ip in game_server_list:
            self.redis_client.hset("ServerLoadCountTable", server_ip, 0)

    def find_server(self):
        # Find server with games hosted count < MAX_GAMES_PER_SERVER
        for key in self.redis_client.hkeys("ServerLoadCountTable"):
            server_ip = key.decode("utf-8")
            current_count = int(self.redis_client.hget("ServerLoadCountTable", server_ip))
            if current_count < MAX_GAMES_PER_SERVER:
                return server_ip
            
        return None
    
    def create_game(self, server_ip, game_id):
        # Add <game_id: server_ip> mapping in "GameRoutingTable"
        self.redis_client.hset("GameRoutingTable", game_id, server_ip)

        # INCR count in <server_ip: count> mapping in "ServerLoadCountTable"
        self.redis_client.hincrby("ServerLoadCountTable", server_ip, 1)

    def find_server_for_game(self, game_id):
        # Find IP for server hosting GAME_ID
        server_ip = self.redis_client.hget("GameRoutingTable", game_id).decode("utf-8") if self.redis_client.hexists("GameRoutingTable", game_id) else None
        return server_ip
    
    def remove_game(self, game_id):
        # Remove <game_id: server_ip> from "GameRoutingTable"
        # DECR count in <server_ip: count> mapping in "ServerLoadCountTable"
        server_ip = self.redis_client.hget("GameRoutingTable", game_id)
        if server_ip:
            server_ip = server_ip.decode("utf-8")
            self.redis_client.hdel("GameRoutingTable", game_id)
            self.redis_client.hincrby("ServerLoadCountTable", server_ip, -1)
            return True
        else:
            return False
