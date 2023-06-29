import pygame
from pygame.surface import Surface
from pygame.font import Font
from typing import Optional, Callable, Tuple

BLACK: Tuple[int, int, int] = (0, 0, 0)
WHITE: Tuple[int, int, int] = (255, 255, 255)
RED: Tuple[int, int, int] = (255, 0, 0)
GREEN: Tuple[int, int, int] = (0, 255, 0)
BLUE: Tuple[int, int, int] = (0, 0, 255)

class Button:
    def __init__(self, rect: pygame.Rect, color: Tuple[int, int, int] = WHITE, text: str = "",
                 font: Optional[Font] = None, callback: Optional[Callable[[], None]] = None):
        self.rect: pygame.Rect = rect
        self.color: Tuple[int, int, int] = color
        self.text: str = text
        self.font: Optional[Font] = font
        self.callback: Optional[Callable[[], None]] = callback
    
    def draw(self, surface: Surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect, 2)
        text = self.font.render(self.text, True, WHITE)
        surface.blit(text, self.rect.move(10, 10))
    
    def set_color(self, color: Tuple[int, int, int]) -> None:
        self.color = color

    def handle_click(self, event: pygame.event.EventType) -> None:
        x, y = event.pos
        if self.rect.collidepoint(x, y):
            if self.callback is not None:
                self.callback()
