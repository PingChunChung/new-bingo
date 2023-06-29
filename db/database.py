from pymongo import MongoClient
import hashlib

class UserSystem:
    def __init__(self):
        client = MongoClient('localhost', 27017)  # Assume the mongodb server is running locally
        self.db = client['game_db']
        self.collection = self.db['users']

    def register(self, username, password):
        if self.collection.find_one({"username": username}):
            return False  # User exists
        hashed_password = self.hash_password(password)
        user = {"username": username, "password": hashed_password}
        self.collection.insert_one(user)
        return True

    def login(self, username, password):
        hashed_password = self.hash_password(password)
        account = self.collection.find_one({"username": username, "password": hashed_password})
        return bool(account)

    def save_game_state(self, username, game_state):
        def convert_keys(obj):
            if isinstance(obj, dict):
                return {str(k): convert_keys(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_keys(elem) for elem in obj]
            else:
                return obj
        converted_state = convert_keys(game_state)
        self.collection.update_one({'username': username}, {'$set': {'game_state': converted_state}})

    def load_game_state(self, username):    
        account = self.collection.find_one({'username': username})
        game_state = account.get('game_state') if account else None

        if game_state and 'player_inputs' in game_state:
            player_inputs = game_state['player_inputs']
            game_state['player_inputs'] = {eval(k): v for k, v in player_inputs.items()}

        return game_state
    
    def hash_password(self, password):
        hash_object = hashlib.sha256(password.encode())
        hashed_password = hash_object.hexdigest()
        return hashed_password
    
    def update_leaderboard(self, username, wins, losses):
        self.collection.update_one(
            {"username": username},
            {"$set": {"wins": wins, "losses": losses}},
            upsert=True
        )

    def get_leaderboard(self, limit=10):
        leaderboard = self.collection.find().sort(
            [("wins", -1), ("losses", 1)]).limit(limit)
        return leaderboard
