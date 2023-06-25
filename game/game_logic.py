import random
from collections import Counter

class GameLogic():
    def __init__(self):
        self.grid_num = 4
        self.grid = [["" for _ in range(self.grid_num)] for _ in range(self.grid_num)]
        self.selected = [[False]*self.grid_num for _ in range(self.grid_num)]
        self.used_nums = []


        self.player_name = ""
        self.player_inputs = {}

        self.rounds = 0

        self.min_number = 1
        self.max_number = 99
    
    def select(self, x, y):
        if self.selected[x][y] == False and (x,y) in self.player_inputs:  
            self.selected[x][y] = True
        print(f'(x, y) : {self.selected[x][y]}')
        print(f'used nums: {self.used_nums}')
        return self.check_game_over()
    
    def check_game_finish(self):
        if self.check_game_win():
            return "win"
        if self.check_game_lose():
            return "lose"

    def check_game_win(self):
        for i in range(self.grid_num):
            if all(self.selected[i][j] for j in range(self.grid_num)):
                return True
            if all(self.selected[j][i] for j in range(self.grid_num)):
                return True
        if all(self.selected[i][i] for i in range(self.grid_num)):
            return True
        if all(self.selected[i][self.grid_num-1-i] for i in range(self.grid_num)):
            return True
        return False
    
    def check_game_lose(self):
        if self.rounds >= 8:
            return True
        return False
    
    def update_player_input(self, x, y, value):
        self.grid[x][y] = value
        self.player_inputs[(x, y)] = value
        print(f'player_inputs[(x,y)]: {self.player_inputs[(x,y)]}')


    
    def is_all_filled(self):
        return len(self.player_inputs) == self.grid_num**2
    
    def get_random_num_in_used_nums(self):
        output = random.choice(self.used_nums)
        self.used_nums.remove(output)
        return output

    def is_invalid_input(self, x: int, y: int, value: str) -> bool:
        if not value.isdigit():
            return True
        count = Counter(self.used_nums)
        if count[value] > 1:
            return True
        value = int(value)
        if self.is_invalid_num_range(value):
            return True
        if (x == y or x == self.grid_num - 1 - y) and not self.is_prime(value):
            return True
        return False

    def is_prime(self, num: int) -> bool:
        if num < 2:
            return False
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                return False
        return True
    

    def is_invalid_num_range(self, value: int) -> bool:
        if not self.min_number <= int(value) <= self.max_number:
            return True
        return False
