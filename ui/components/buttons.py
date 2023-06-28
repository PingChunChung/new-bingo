import pygame

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Button:
    def __init__(self, rect, color=WHITE, text="", font=None, callback=None):
        self.rect = rect
        self.color = color
        self.text = text
        self.font = font
        self.callback = callback
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, 2)
        text = self.font.render(self.text, True, WHITE)
        surface.blit(text, self.rect.move(10, 10))
    
    def set_color(self, color):
        self.color = color

    def handle_click(self, event):
        x, y = event.pos
        if self.rect.collidepoint(x, y):
            if self.callback is not None:
                self.callback()