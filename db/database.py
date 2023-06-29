from pymongo import MongoClient
import hashlib
from typing import Optional, Dict, Any, List

class UserSystem:
    def __init__(self):
        client: MongoClient = MongoClient('localhost', 27017)
        self.db = client['game_db']
        self.collection = self.db['users']

    def register(self, username: str, password: str) -> bool:
        if self.collection.find_one({"username": username}):
            return False
        hashed_password: str = self.hash_password(password)
        user: Dict[str, Any] = {"username": username, "password": hashed_password}
        self.collection.insert_one(user)
        return True

    def login(self, username: str, password: str) -> bool:
        hashed_password: str = self.hash_password(password)
        account: Optional[Dict[str, Any]] = self.collection.find_one({"username": username, "password": hashed_password})
        return bool(account)

    def save_game_state(self, username: str, game_state: Dict[str, Any]) -> None:
        def convert_keys(obj: Dict[str, Any]) -> Dict[str, Any]:
            if isinstance(obj, dict):
                return {str(k): convert_keys(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_keys(elem) for elem in obj]
            else:
                return obj
        converted_state: Dict[str, Any] = convert_keys(game_state)
        self.collection.update_one({'username': username}, {'$set': {'game_state': converted_state}})

    def load_game_state(self, username: str) -> Optional[Dict[str, Any]]:
        account: Optional[Dict[str, Any]] = self.collection.find_one({'username': username})
        game_state: Optional[Dict[str, Any]] = account.get('game_state') if account else None

        if game_state and 'player_inputs' in game_state:
            player_inputs: Dict[str, Any] = game_state['player_inputs']
            game_state['player_inputs'] = {eval(k): v for k, v in player_inputs.items()}

        return game_state

    def hash_password(self, password: str) -> str:
        hash_object: hashlib._Hash = hashlib.sha256(password.encode())
        hashed_password: str = hash_object.hexdigest()
        return hashed_password
    
    def update_leaderboard(self, username: str, wins: int, losses: int) -> None:
        self.collection.update_one(
            {"username": username},
            {"$set": {"wins": wins, "losses": losses}},
            upsert=True
        )

    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        leaderboard: List[Dict[str, Any]] = self.collection.find().sort(
            [("wins", -1), ("losses", 1)]).limit(limit)
        return leaderboard
