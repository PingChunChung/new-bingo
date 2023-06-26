from pymongo import MongoClient

class UserSystem:
    def __init__(self):
        client = MongoClient('localhost', 27017)  # Assume the mongodb server is running locally
        self.db = client['game_db']
        self.users = self.db['users']

    def register(self, username, password):
        if self.users.find_one({"username": username}):
            return False  # User exists
        user = {"username": username, "password": password}
        self.users.insert_one(user)
        return True  # Registration successful

    def login(self, username, password):
        account = self.users.find_one({"username": username, "password": password})
        return bool(account)  # Returns True if login successful

    def save_game_state(self, username, game_state):
        self.collection.update_one({'username': username}, {'$set': {'game_state': game_state}})

    def load_game_state(self, username):
        account = self.collection.find_one({'username': username})
        return account.get('game_state') if account else None