import pygame
from utils.settings import FONT

class Toolbar:
    def __init__(self, modes):
        self.modes = modes
        self.current_mode = modes[0]
        self.buttons = self._create_buttons()

    def _create_buttons(self):
        buttons = []
        x = 10
        for mode in self.modes:
            rect = pygame.Rect(x, 10, 120, 30)
            buttons.append((mode, rect))
            x += 130
        return buttons

    def draw(self, surface):
        for mode, rect in self.buttons:
            color = (200, 200, 200) if mode != self.current_mode else (150, 150, 255)
            pygame.draw.rect(surface, color, rect)
            text = FONT.render(mode, True, (0, 0, 0))
            surface.blit(text, (rect.x + 10, rect.y + 5))

    def handle_click(self, pos):
        for mode, rect in self.buttons:
            if rect.collidepoint(pos):
                self.current_mode = mode
                return True
        return False
