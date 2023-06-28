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

    def start(self):
        self.server.listen()
        print(f'Server started, listening on {self.host}:{self.port}')
        while True:
            client, addr = self.server.accept()
            print(f'Accepted connection from {addr}')
            self.clients.append(client)
            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.start()

    def broadcast(self, message, sender):
        for client in self.clients:
            if client != sender:
                client.send(message)

    def handle_client(self, client):
        while True:
            try:
                message = client.recv(1024)
                if not message:
                    print(f'Client {client.getsockname()} has closed the connection')
                    break
                print(f'Received message: {message.decode()} from {client.getsockname()}')
                self.broadcast(message, client)
                if message == b"win" or message == b"lose":
                    self.broadcast(message, client)  # 广播消息给所有客户端
                elif message.startswith(b"login"):
                    self.broadcast(f"player_count {len(self.clients)}".encode(), client)  # 广播玩家数量给所有客户端
                    
                self.broadcast(message, client)
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
