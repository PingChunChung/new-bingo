import pygame
from game.logic import GameLogic
import utility.message_box
from db.database import UserSystem
import socket
import threading
from ui.components.buttons import Button
from ui.components.display import *
import queue
from typing import Dict, Tuple, List, Optional

BLACK: Tuple[int, int, int] = (0, 0, 0)
WHITE: Tuple[int, int, int] = (255, 255, 255)
RED: Tuple[int, int, int] = (255, 0, 0)
GREEN: Tuple[int, int, int] = (0, 255, 0)
BLUE: Tuple[int, int, int] = (0, 0, 255)


class GameUI:
    def __init__(self, user_system: UserSystem, game: GameLogic, player_name: str = "", game_state: dict = None, online_mode: bool = False):
        right_padding: int = 500

        self.user_system: UserSystem = user_system
        self.game: GameLogic = game
        self.player_name: str = player_name
        self.running: bool = True
        self.online_mode: bool = online_mode

        pygame.init()

        self.server_thread: threading.Thread = None
        self.player_count_queue: queue.Queue = queue.Queue()

        if game_state:
            self.game.grid = game_state["grid"]
            self.game.selected = game_state["selected"]
            self.game.used_nums = game_state["used_nums"]
            self.game.player_inputs = game_state["player_inputs"]
            self.game.rounds = game_state["rounds"]

        self.player_count: int = 0  # 玩家数量
        self.ended_round_players: set = set()  # 當前回合已完成的玩家
        self.waiting_for_round: bool = False  # 是否等待回合结束

        self.total_grid_size: Tuple[int, int] = (600, 600)  # size of the grid
        self.grid_size: Tuple[int, int] = (self.total_grid_size[0] // self.game.grid_num, self.total_grid_size[1] // self.game.grid_num)
        self.colored: List[List[bool]] = [[False]*self.game.grid_num for _ in range(self.game.grid_num)]
        self.window_size: Tuple[int, int] = (self.total_grid_size[0] + right_padding, self.total_grid_size[1])
        self.screen: pygame.Surface = pygame.display.set_mode(self.window_size)
        self.font: pygame.font.Font = pygame.font.Font(None, 36)

        self.grid: Grid = Grid(self.game, self.screen, self.grid_size, self.font)
        self.player_count_display: PlayerCountDisplay = PlayerCountDisplay(self.screen, self.font, self.player_count_queue, self.ended_round_players)
        self.rounds_display: RoundsDisplay = RoundsDisplay(self.game, self.screen, self.font)
        self.current_cell: Optional[Tuple[int, int]] = None

        # mode
        self.is_typing_mode: bool = True

        self.record: Dict[str, int] = {"win": 0, "lose": 0}

        # button
        self.confirm_button_rect: pygame.Rect = pygame.Rect(
            (self.total_grid_size[0] + right_padding // 4, self.total_grid_size[1] - 50, 110, 50))
        self.confirm_button_pressed: bool = False
        self.getRandomNum_button_rect: pygame.Rect = pygame.Rect(
            (self.total_grid_size[0] + right_padding // 4, self.total_grid_size[1] - 110, 110, 50))
        self.record_button_rect: pygame.Rect = pygame.Rect(
            (self.total_grid_size[0] + right_padding*2 // 4, self.total_grid_size[1] - 50, 110, 50))
        self.buttons: Dict[str, Button] = {
            "confirm": Button(self.confirm_button_rect, text="Confirm", font=self.font, callback=self.handle_confirm),
            "getRandomNum": Button(self.getRandomNum_button_rect, text="Get", font=self.font, callback=self.handle_get_random_num),
            "record": Button(self.record_button_rect, text="Record", font=self.font, callback=self.handle_record)
        }

        # 線上模式
        if self.online_mode:
            self.server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect(("localhost", 12345))
            self.server_thread = threading.Thread(target=self.receive_messages, args=(self.player_count_queue,))
            self.server_thread.start()
            self.send_message(f"{self.player_name} login")

    def start(self) -> None:
        pygame.display.set_caption('Bingo Game')
        clock: pygame.time.Clock = pygame.time.Clock()

        while self.running:
            self.screen.fill(BLACK)
            self.grid.draw()
            self.rounds_display.draw((self.total_grid_size[0] + 10, 50))
            for button in self.buttons.values():
                button.draw(self.screen)
            if self.online_mode:
                self.player_count_display.draw((self.total_grid_size[0] + 10, 10))  # 顯示玩家數量
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
                        input_value = self.game.player_inputs.get(self.current_cell, '') + event.unicode
                        self.game.update_player_input(*self.current_cell, input_value)

            clock.tick(30)

        self.quit_game()
        pygame.quit()

    def receive_messages(self, player_count_queue: queue.Queue) -> None:
        while self.running:
            try:
                message: str = self.server_socket.recv(1024).decode()
                if message.startswith("player_count"):
                    print(f'received message: {message}')
                    _, count = message.split()
                    player_count: int = int(count)
                    player_count_queue.put(player_count)
                    self.player_count_display.set_player_count(player_count)
                elif message.startswith("round_end"):
                    print(f'received message: {message}')
                    fields: List[str] = message.split()
                    ended_round_players_num: int = int(fields[1])
                    self.player_count_display.set_ended_round_players_num(ended_round_players_num)
                    if ended_round_players_num == self.player_count_display.get_player_count():
                        self.waiting_for_round = False
                        self.player_count_display.set_ended_round_players_num(0)
                else:
                    print("Received message:", message)
            except Exception as e:
                print(f'Error occurred: {e}')
                break

    def send_message(self, message: str) -> None:
        if not self.running:
            return
        try:
            self.server_socket.send(message.encode())
        except Exception as e:
            print(f'Error occurred: {e}')

    def quit_game(self) -> None:
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

    def restart_game(self) -> None:
        self.game.__init__()
        self.is_typing_mode = True
        self.confirm_button_pressed = False
        self.buttons["confirm"].set_color(WHITE)

    def handle_click(self, event: pygame.event.Event) -> None:
        x, y = event.pos

        if self.confirm_button_rect.collidepoint(x, y) and not self.confirm_button_pressed:
            self.buttons["confirm"].handle_click(event)
        if self.getRandomNum_button_rect.collidepoint(x, y):
            self.buttons["getRandomNum"].handle_click(event)
        if self.record_button_rect.collidepoint(x, y):
            self.buttons["record"].handle_click(event)

        # 點擊格子
        if x < self.total_grid_size[0]:
            i = x // self.grid_size[0]
            j = y // self.grid_size[1]

            if self.is_typing_mode:
                self.current_cell = (i, j)
                self.game.update_player_input(i, j, "")

    def handle_confirm(self) -> None:
        # 檢查有沒有全填滿
        self.game.used_nums = [j for i in self.game.grid for j in i]
        print(f"self.grid: {self.game.grid}")
        print(f"self.game.used_nums: {self.game.used_nums}")
        if not self.game.is_all_filled():
            utility.message_box.show_message("Hints", "Please fill in all numbers!")
            return

        for (i, j) in self.game.player_inputs:
            if self.game.is_invalid_input(i, j, self.game.grid[i][j]):
                utility.message_box.show_message(
                    "Error", "Invalid input at position " + str((i + 1, j + 1)) + "! Please enter again."
                )
                return
        else:
            self.is_typing_mode = False
            self.buttons["confirm"].set_color(BLUE)
            self.confirm_button_pressed = True

        return

    def handle_get_random_num(self) -> None:
        if not self.confirm_button_pressed:
            utility.message_box.show_message("Hints", "Please confirm your input.")
            return
        if self.online_mode:
            if self.waiting_for_round:  # 等待回合结束，不能繼續get
                utility.message_box.show_message(
                    "Wait", "Please wait for other players to finish the round.")
                return
        num = self.game.get_random_num_in_used_nums()
        for i in range(self.game.grid_num):
            for j in range(self.game.grid_num):
                if self.game.grid[i][j] == num:
                    self.game.selected[i][j] = True
                    break
        self.grid.draw()
        pygame.display.flip()
        self.game.rounds += 1

        if self.game.check_game_finish() == "win":
            self.record["win"] += 1
            if self.player_name != "":
                self.user_system.update_leaderboard(self.player_name, self.record["win"], self.record["lose"])
            utility.message_box.show_message(
                "Win!", f"You win!\nWin: {self.record['win']} - Lose: {self.record['lose']}")
            self.restart_game()
        elif self.game.check_game_finish() == "lose":
            self.record["lose"] += 1
            if self.player_name != "":
                self.user_system.update_leaderboard(self.player_name, self.record["win"], self.record["lose"])
            utility.message_box.show_message(
                "Lose!", f"You lose!\nWin: {self.record['win']} - Lose: {self.record['lose']}")
            self.restart_game()

        if self.online_mode:
            self.waiting_for_round = True
            self.send_message("round_end")
        print(f"Get: {num}")
        print(f"rounds: {self.game.rounds}")
        return

    def handle_record(self) -> None:
        utility.message_box.show_message(
            "Record", f"Win: {self.record['win']} - Lose: {self.record['lose']}")
