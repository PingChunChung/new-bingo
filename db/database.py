from pymongo import MongoClient

class UserSystem:
    def __init__(self):
        client = MongoClient('localhost', 27017)  # Assume the mongodb server is running locally
        self.db = client['game_db']
        self.collection = self.db['users']

    def register(self, username, password):
        if self.collection.find_one({"username": username}):
            return False  # User exists
        user = {"username": username, "password": password}
        self.collection.insert_one(user)
        return True  # Registration successful

    def login(self, username, password):
        account = self.collection.find_one({"username": username, "password": password})
        return bool(account)  # Returns True if login successful

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