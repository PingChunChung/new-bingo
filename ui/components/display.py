import pygame
from game.logic import GameLogic
from pygame.surface import Surface
from pygame.font import Font
from typing import Tuple

WHITE: Tuple[int, int, int] = (255, 255, 255)
BLUE: Tuple[int, int, int] = (0, 0, 255)


class Grid:
    def __init__(self, game: GameLogic, screen: Surface, grid_size: Tuple[int, int], font: Font):
        self.game: GameLogic = game
        self.screen: Surface = screen
        self.grid_size: Tuple[int, int] = grid_size
        self.font: Font = font
        
    def draw(self) -> None:
        rect_size = (self.grid_size[0], self.grid_size[1])
        for i in range(self.game.grid_num):
            for j in range(self.game.grid_num):
                color = BLUE if self.game.selected[j][i] else WHITE
                width = 0 if self.game.selected[j][i] else 1

                rect = pygame.Rect(i * rect_size[0], j * rect_size[1], rect_size[0], rect_size[1])
                
                pygame.draw.rect(self.screen, color, rect, width)

                if (i, j) in self.game.player_inputs:
                    rect = pygame.Rect(
                        i * rect_size[0], j * rect_size[1], rect_size[0], rect_size[1])
                    pygame.draw.rect(self.screen, WHITE, rect, 1)
                    text = self.font.render(
                        self.game.player_inputs[(i, j)], True, WHITE)
                else:
                    text = self.font.render("", True, WHITE)

                self.screen.blit(text, rect.move(
                    rect_size[0] // 2, rect_size[1] // 2))


# online mode


class PlayerCountDisplay:
    def __init__(self, screen: Surface, font: Font, player_count_queue, ended_round_players):
        self.screen: Surface = screen
        self.font: Font = font
        self.player_count_queue = player_count_queue
        self.ended_round_players = ended_round_players
        self.player_count: int = 0  # 初始化玩家數量為0
        self.ended_round_players_num: int = 0

    def draw(self, position: Tuple[int, int]) -> None:
        count_text = self.font.render(f"{self.ended_round_players_num}/{self.player_count}", True, WHITE)
        self.screen.blit(count_text, position)

    def set_player_count(self, count: int) -> None:
        self.player_count = count

    def get_player_count(self) -> int:
        return self.player_count

    def set_ended_round_players_num(self, num: int) -> None:
        self.ended_round_players_num = num

    def get_ended_round_players_num(self) -> int:
        return self.ended_round_players_num


# online mode


class RoundsDisplay:
    def __init__(self, game: GameLogic, screen: Surface, font: Font):
        self.screen: Surface = screen
        self.font: Font = font
        self.game: GameLogic = game

    def draw(self, position: Tuple[int, int]) -> None:
        rounds_text = self.font.render(
            f"Round: {self.game.rounds} / 8", True, WHITE)
        self.screen.blit(rounds_text, position)
