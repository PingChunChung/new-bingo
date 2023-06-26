import pygame
from game.game_logic import GameLogic
import utility.message_box

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class GameUI:
    def __init__(self, game: GameLogic):
        right_padding = 500
        self.game = game
        pygame.init()

        self.total_grid_size = (600, 600)  # size of the grid
        self.grid_size = (self.total_grid_size[0] // self.game.grid_num, self.total_grid_size[1] // self.game.grid_num)
        self.colored = [[False]*self.game.grid_num for _ in range(self.game.grid_num)]
        self.window_size = (self.total_grid_size[0] + right_padding, self.total_grid_size[1])
        self.screen = pygame.display.set_mode(self.window_size)
        self.font = pygame.font.Font(None, 36)

        self.current_cell = None

        # mode
        self.is_typing_mode = True

        # confirm button
        self.confirm_button_rect = pygame.Rect((self.total_grid_size[0] + right_padding // 4, self.total_grid_size[1] - 50,110,50))
        self.confirm_button_pressed = False
        self.confirm_button_color = WHITE

        # getRandomNum button
        self.getRandomNum_button_rect = pygame.Rect((self.total_grid_size[0] + right_padding // 4, self.total_grid_size[1] - 110,110,50))
        self.getRandomNum_button_color = WHITE

        # record button
        self.record_button_rect = pygame.Rect((self.total_grid_size[0] + right_padding*2 // 4, self.total_grid_size[1] - 50,110,50))
        self.record_button_color = WHITE


        self.record = {"win": 0, "lose": 0}
    
    def start(self):
        pygame.display.set_caption('Bingo Game')
        clock = pygame.time.Clock()
    

        running = True
        while running:
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_button(self.screen, self.getRandomNum_button_color, self.getRandomNum_button_rect,"Get")
            self.draw_button(self.screen, self.confirm_button_color, self.confirm_button_rect,"Confirm")
            self.draw_button(self.screen, self.record_button_color, self.record_button_rect,"Record")
            
            pygame.display.flip()
            for event in pygame.event.get():
                # 關閉遊戲
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event)
                    break
                if self.is_typing_mode and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        input_value = self.game.player_inputs[self.current_cell][:-1]
                        self.game.update_player_input(*self.current_cell, input_value)
                    if len(self.game.player_inputs.get(self.current_cell, '')) < 2:
                        input_value = self.game.player_inputs.get(self.current_cell,'') + event.unicode
                        self.game.update_player_input(*self.current_cell, input_value)

            clock.tick(30)
        pygame.quit()

    def draw_grid(self):
        rect_size = (self.grid_size[0], self.grid_size[1])
        for i in range(self.game.grid_num):
            for j in range(self.game.grid_num):
                color = BLUE if self.game.selected[i][j] else WHITE
                rect = pygame.Rect(i * rect_size[0], j * rect_size[1], rect_size[0], rect_size[1])
                
                pygame.draw.rect(self.screen, color, rect, 1)

                if (i, j) in self.game.player_inputs:
                    rect = pygame.Rect(i * rect_size[0], j * rect_size[1], rect_size[0], rect_size[1])
                    pygame.draw.rect(self.screen, color, rect, 1)
                    text = self.font.render(self.game.player_inputs[(i,j)], True, WHITE)
                else:
                    text = self.font.render("", True, WHITE)

                
                self.screen.blit(text, rect.move(rect_size[0] // 2, rect_size[1] // 2))

    def handle_click(self, event):
        x, y = event.pos

        # 按下confirm
        if self.confirm_button_rect.collidepoint(x, y) and not self.confirm_button_pressed:
            # 檢查有沒有全填滿

            self.game.used_nums = [j for i in self.game.grid for j in i]
            if not self.game.is_all_filled():
                utility.message_box.show_message("Hints", "Please fill in all numbers!")
                return
            
            for (i, j) in self.game.player_inputs:
                if self.game.is_invalid_input(i, j, self.game.grid[i][j]):
                    utility.message_box.show_message("Error", "Invalid input at position " + str((i + 1, j + 1)) + "! Please enter again.")
                    return
                
            self.is_typing_mode = False
            self.confirm_button_color = BLUE
            return

        # 點擊格子
        if x < self.total_grid_size[0]:
            i = x // self.grid_size[0]
            j = y // self.grid_size[1]

            if self.is_typing_mode:
                self.current_cell = (i, j)
                self.game.update_player_input(i, j, "")

        # 按下getRandomNum
        if self.getRandomNum_button_rect.collidepoint(x, y):
            num = self.game.get_random_num_in_used_nums()
            # 這邊之後可以優化，不要用迴圈
            for i in range(self.game.grid_num):
                for j in range(self.game.grid_num):
                    if self.game.grid[i][j] == num:
                        self.game.selected[i][j] = True
                        break
            self.game.rounds += 1
            if self.game.check_game_finish() == "win":
                self.record["win"] += 1
                utility.message_box.show_message("Win!", f"You win!\nWin: {self.record['win']} - Lose: {self.record['lose']}")
                self.restart_game()
            elif self.game.check_game_finish() == "lose":
                self.record["lose"] += 1
                utility.message_box.show_message("Lose!", f"You lose!\nWin: {self.record['win']} - Lose: {self.record['lose']}")
                self.restart_game()
            print(f"Get: {num}")
            print(f"rounds: {self.game.rounds}")
            return

        if self.record_button_rect.collidepoint(x, y):
                utility.message_box.show_message("Record", f"Win: {self.record['win']} - Lose: {self.record['lose']}")
            
    def draw_button(self, surface, color, rect, string):
        pygame.draw.rect(surface, color, rect, 2)
        text = self.font.render(string, True, WHITE)
        surface.blit(text, rect.move(10, 10))

    def restart_game(self):
        # self.game.reset()
        self.game.__init__()
        self.is_typing_mode = True
        self.confirm_button_color = WHITE