import socket
import threading
from db.database import UserSystem

class GameServer:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.clients = []
        self.user_system = UserSystem()

        self.ended_round_players = set()
        self.ended_round_players_num = 0

    def start(self):
        self.server.listen()
        print(f'Server started, listening on {self.host}:{self.port}')
        while True:
            client, addr = self.server.accept()
            print(f'Accepted connection from {addr}')
            self.clients.append(client)
            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.start()

    def broadcast(self, message, sender, toSender: bool = False):
        for client in self.clients:
            if client != sender:
                client.send(message)
            if toSender:
                sender.send(message)


    def handle_client(self, client):
        while True:
            try:
                message = client.recv(1024)
                if not message:
                    print(f'Client {client.getsockname()} has closed the connection')
                    self.broadcast(f"player_count {len(self.clients) - 1} ".encode(), None)
                    break
                print(f'Received message: {message.decode()} from {client.getsockname()}')
                # 玩家加入
                if message.endswith(b"login"):
                    self.broadcast(message, client)
                    self.broadcast(f"player_count {len(self.clients)}".encode(), client, toSender=True)
                if message == b"win" or message == b"lose":
                    print("game over")
                    self.broadcast(message, client)
                elif message == b"round_end":
                    self.ended_round_players.add(client)
                    self.broadcast(f"round_end {len(self.ended_round_players)} \n".encode(), client, toSender=True)
                    if len(self.ended_round_players) == len(self.clients):
                        self.broadcast(b"All complete, start next round \n", None)
                        self.ended_round_players.clear()
            except Exception as e:
                print(f'Error occurred: {e}')
                break
        self.clients.remove(client)
        client.close()
    def close(self):
        self.server.close()

if __name__ == "__main__":
    server = GameServer()
    server.start()
