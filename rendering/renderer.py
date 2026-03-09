import pygame
from utils.settings import*

class Renderer:
    def __init__(self, gm, ui, grid_size=25):
        self.gm = gm
        self.ui = ui
        self.grid_size = grid_size

    def draw_grid(self, surface):
        w, h = surface.get_size()
        for x in range(0, w, self.grid_size):
            pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, h), 1)
        for y in range(0, h, self.grid_size):
            pygame.draw.line(surface, GRID_COLOR, (0, y), (w, y), 1)

    def draw(self, surface):
        surface.fill(BG_COLOR)
        self.draw_grid(surface)
        self.ui.draw(surface)

        # Draw flip candidates
        for _, (p1, p2) in self.ui.selection.flip_candidates:
            pygame.draw.line(surface, FLIP_EDGE_COLOR, (p1.x, p1.y), (p2.x, p2.y), FLIP_EDGE_THICKNESS)

        # Draw edges
        for i, (p1, p2) in enumerate(self.gm.edges):
            color = EDGE_COLOR
            if self.ui.selection.hover_edge_index == i:
                color = HOVER_EDGE_COLOR
            pygame.draw.line(surface, color, (p1.x, p1.y), (p2.x, p2.y), EDGE_THICKNESS)

        # Draw points
        for p in self.gm.points:
            color = POINT_COLOR
            if p is self.ui.selection.hover_point:
                color = HOVER_POINT_COLOR
            elif p is self.ui.selection.selected_point:
                color = SELECTED_POINT_COLOR

            pygame.draw.circle(surface, color, (p.x, p.y), POINT_SIZE)

