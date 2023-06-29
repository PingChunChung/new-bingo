import pygame
from game.logic import GameLogic

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)


class Grid:
    def __init__(self, game: GameLogic, screen, grid_size, font):
        self.game = game
        self.screen = screen
        self.grid_size = grid_size
        self.font = font

    def draw(self):
        rect_size = (self.grid_size[0], self.grid_size[1])
        for i in range(self.game.grid_num):
            for j in range(self.game.grid_num):
                color = BLUE if self.game.selected[i][j] else WHITE
                rect = pygame.Rect(
                    i * rect_size[0], j * rect_size[1], rect_size[0], rect_size[1])

                pygame.draw.rect(self.screen, color, rect, 1)

                if (i, j) in self.game.player_inputs:
                    rect = pygame.Rect(
                        i * rect_size[0], j * rect_size[1], rect_size[0], rect_size[1])
                    pygame.draw.rect(self.screen, color, rect, 1)
                    text = self.font.render(
                        self.game.player_inputs[(i, j)], True, WHITE)
                else:
                    text = self.font.render("", True, WHITE)

                self.screen.blit(text, rect.move(
                    rect_size[0] // 2, rect_size[1] // 2))

# online mode


class PlayerCountDisplay:
    def __init__(self, screen, font, player_count_queue, round_players):
        self.screen = screen
        self.font = font
        self.player_count_queue = player_count_queue
        self.round_players = round_players
        self.player_count = 0  # 初始化玩家數量為0

    def update_player_count(self, count: int):
        self.player_count = count
        
    def draw(self, position):
        # if not self.player_count_queue.empty():  # 檢查佇列是否有新的玩家數量
        #     player_count = self.player_count_queue.get()
        count_text = self.font.render(f"{len(self.round_players)}/{self.player_count}", True, WHITE)
        self.screen.blit(count_text, position)

# online mode


class RoundsDisplay:
    def __init__(self, game: GameLogic, screen, font):
        self.screen = screen
        self.font = font
        self.game = game
    def draw(self, position):
        rounds_text = self.font.render(
            f"Round: {self.game.rounds}", True, WHITE)
        self.screen.blit(rounds_text, position)
