import random

class GameLogic():
    def __init__(self):
        self.grid_num = 4
        self.grid = [["" for _ in range(self.grid_num)] for _ in range(self.grid_num)]
        self.selected = [[False]*self.grid_num for _ in range(self.grid_num)]
        self.used_nums = []


        self.player_name = ""
        self.player_inputs = {}

        self.rounds = 0
    
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
        # if not self.is_valid_input(x, y, value):
        #     print("Invalid input, please enter a valid number.")
        #     return False
        print(f'(x, y) : {self.selected[x][y]}')
        self.grid[x][y] = value
        self.player_inputs[(x, y)] = value
        return True
    
    def is_all_filled(self):
        return len(self.player_inputs) == self.grid_num**2
    
    def get_random_num_in_used_nums(self):
        output = random.choice(self.used_nums)
        self.used_nums.remove(output)
        return output

    # def reset(self):
        # self.grid = [["" for _ in range(self.grid_num)] for _ in range(self.grid_num)]
        # self.selected = [[False]*self.grid_num for _ in range(self.grid_num)]
        # self.rounds = 0
        # self.used_nums = []
        # self.player_name = ""
        # self.player_inputs = {}