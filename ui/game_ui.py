import pygame
from game.logic import GameLogic
import utility.message_box
from db.database import UserSystem
import socket
import threading
from ui.components.buttons import Button

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class GameUI:
    def __init__(self, user_system: UserSystem, game: GameLogic, player_name = "",  game_state = None, online_mode=False):
        right_padding = 500

        self.user_system = user_system
        self.game = game
        self.player_name = player_name
        self.running = True
        self.online_mode = online_mode

        pygame.init()

        self.server_thread = None
        # 線上模式
        if self.online_mode:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect(("localhost", 12345))
            self.server_thread = threading.Thread(target=self.receive_messages)
            self.server_thread.start()
            self.send_message(f"{self.player_name} login")
        
        if game_state:
            self.game.grid = game_state["grid"]
            self.game.selected = game_state["selected"]
            self.game.used_nums = game_state["used_nums"]
            self.game.player_inputs = game_state["player_inputs"]
            self.game.rounds = game_state["rounds"]

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

        #TODO: 線上模式的code，之後移動位置記得測試
        self.player_count = 0  # 玩家数量
        self.round_players = set()  # 当前回合已完成的玩家
        self.waiting_for_round = False  # 是否等待回合结束

        self.buttons = {
            "confirm": Button(pygame.Rect((self.total_grid_size[0] + right_padding // 4, self.total_grid_size[1] - 50, 110, 50)),
                                        text="Confirm", font=self.font, callback=self.handle_confirm),
            "getRandomNum": Button(pygame.Rect((self.total_grid_size[0] + right_padding // 4, self.total_grid_size[1] - 110, 110, 50)),
                                            text="Get", font=self.font, callback=self.handle_get_random_num),
            "record": Button(pygame.Rect((self.total_grid_size[0] + right_padding * 2 // 4, self.total_grid_size[1] - 50, 110, 50)),
                                        text="Record", font=self.font, callback=self.handle_record)
        }


    def start(self):
        pygame.display.set_caption('Bingo Game')
        clock = pygame.time.Clock()
    
        # running = True
        while self.running:
            self.screen.fill(BLACK)
            self.draw_grid()
            for button in self.buttons.values():
                button.draw(self.screen)
            if self.online_mode:
                self.draw_player_count()  # 顯示玩家數量
            pygame.display.flip()
            for event in pygame.event.get():
                # 關閉遊戲
                if event.type == pygame.QUIT:
                    if self.player_name:
                       self.user_system.save_game_state(self.player_name, self.game.__dict__)
                    self.running = False
                    break
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
        # pygame.quit()
        self.quit_game()
        pygame.quit()
    
    def receive_messages(self):
        while self.running:
            try:
                message = self.server_socket.recv(1024).decode()
                if message == "win":
                    self.record["win"] += 1
                    if len(self.round_players) == self.player_count:  # 所有玩家都完成回合
                        utility.message_box.show_message("Lose!", f"You lose!\nWin: {self.record['win']} - Lose: {self.record['lose']}")
                        self.restart_game()
                elif message == "lose":
                    self.waiting_for_round = True  # 等待回合结束
                    # self.record["lose"] += 1
                    # utility.message_box.show_message("Lose!", f"You lose!\nWin: {self.record['win']} - Lose: {self.record['lose']}")
                    # self.restart_game()
                elif message.startswith("player_count"):
                    _, count = message.split()
                    self.player_count = int(count)
                else:
                    print("Received message:", message)  # 在命令行中显示接收到的消息
            except Exception as e:
                print(f'Error occurred: {e}')
                break

    def send_message(self, message):
        if not self.running:
            return
        try:
            self.server_socket.send(message.encode())
        except Exception as e:
            print(f'Error occurred: {e}')

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

        if self.confirm_button_rect.collidepoint(x, y) and not self.confirm_button_pressed:
            self.confirm_button.handle_click(event)
        if self.getRandomNum_button_rect.collidepoint(x, y):
            self.getRandomNum_button.handle_click(event)
        if self.record_button_rect.collidepoint(x, y):
            self.record_button.handle_click(event)

        # 點擊格子
        if x < self.total_grid_size[0]:
            i = x // self.grid_size[0]
            j = y // self.grid_size[1]

            if self.is_typing_mode:
                self.current_cell = (i, j)
                self.game.update_player_input(i, j, "")

    def draw_player_count(self):
        count_text = self.font.render(f"{len(self.round_players)}/{self.player_count}", True, WHITE)
        self.screen.blit(count_text, (self.total_grid_size[0] + 10, 10))

    def quit_game(self):
        self.running = False

        if self.online_mode:
            if self.server_socket:
                try:
                    # Add a condition to ensure the socket is valid
                    if self.server_socket.fileno() != -1:
                        self.server_socket.shutdown(socket.SHUT_RDWR)
                        self.server_socket.close()
                except socket.error as e:
                    print(f'Error occurred: {e}')
            
        # Join the server thread
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join()
            
        import sys
        sys.exit()

    def restart_game(self):
        self.game.__init__()
        self.is_typing_mode = True
        self.confirm_button_pressed = False
        self.confirm_button.set_color(WHITE)

    def handle_confirm(self):
        # 檢查有沒有全填滿
        self.game.used_nums = [j for i in self.game.grid for j in i]
        print(f"self.grid: {self.game.grid}")
        print(f"self.game.used_nums: {self.game.used_nums}")
        if not self.game.is_all_filled():
            utility.message_box.show_message("Hints", "Please fill in all numbers!")
            return
        
        for (i, j) in self.game.player_inputs:
            if self.game.is_invalid_input(i, j, self.game.grid[i][j]):
                utility.message_box.show_message("Error", "Invalid input at position " + str((i + 1, j + 1)) + "! Please enter again.")
                return
        else:   
            self.is_typing_mode = False
            self.confirm_button.set_color(BLUE)
            self.confirm_button_pressed = True

        return
    def handle_get_random_num(self):
        if not self.confirm_button_pressed:
            utility.message_box.show_message("Hints", "Please confirm your input.")
            return
        if self.waiting_for_round:  # 等待回合结束，不能继续获取数字
            utility.message_box.show_message("Wait", "Please wait for other players to finish the round.")
            return
        num = self.game.get_random_num_in_used_nums()
        # 這邊之後可以優化，不要用迴圈
        for i in range(self.game.grid_num):
            for j in range(self.game.grid_num):
                if self.game.grid[i][j] == num:
                    self.game.selected[i][j] = True
                    break
        self.game.rounds += 1
        if self.online_mode:
            self.send_message("win" if self.game.check_game_finish() == "win" else "lose")
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

    def handle_record(self):
        utility.message_box.show_message("Record", f"Win: {self.record['win']} - Lose: {self.record['lose']}")