import pygame
import sys

from core.geometry_manager import GeometryManager, is_near_edge
from ui.ui_manager import (
    UIManager,
    ADD_POINT,
    MOVE_SPLIT,
    DELETE_POINT,
    FLIP,
    CLEAR,
    EXPORT_TIKZ,
)
from rendering.renderer import Renderer
from utils.settings import WIDTH, HEIGHT
from core.flip_types import (
    FLIP_SAME,
    FLIP_PREFIX_REVERSE,
    FLIP_ROTATE,
    FLIP_SUFFIX_REVERSE,
)

def main():
    # Init pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Polyline Editor")
    clock = pygame.time.Clock()

    # Define manager classes
    gm = GeometryManager()
    ui = UIManager()
    renderer = Renderer(gm, ui)
    
    dragging_point = None
    while True:
        renderer.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # --- mouse down ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                # is it on toolbar?
                if ui.handle_click(pos):
                    if ui.current_mode == CLEAR:
                        gm.points = []
                        ui.set_mode(ADD_POINT)

                    elif ui.current_mode == EXPORT_TIKZ:
                        latex = gm.export_to_tikz()
                        with open("polyline.tex", "w") as f:
                            f.write(latex)
                        print("Exported to polyline.tex")
                        ui.set_mode(MOVE_SPLIT)

                    ui.selection.clear()
                    ui.selection.clear_hover()
                    ui.selection.clear_flip()
                    continue

                mode = ui.current_mode

                if mode == MOVE_SPLIT:
                    p = gm.get_point_at(pos)
                    if p:
                        ui.selection.select_point(p)
                        dragging_point = p
                    else:
                        edge_index = gm.get_edge_at(pos)
                        if edge_index is not None:
                            p = gm.insert_point_on_edge(edge_index, *pos)
                            ui.selection.select_point(p)
                            dragging_point = p
                        else:
                            ui.selection.clear()

                elif mode == ADD_POINT:
                    p = gm.append_point(*pos)
                    ui.selection.select_point(p)
                    continue

                elif mode == DELETE_POINT:
                    p = gm.get_point_at(pos)
                    if p:
                        gm.delete_point(p)
                        ui.selection.clear()
                        continue


                elif mode == FLIP:
                    # Step 1: if no base edge selected yet
                    if ui.selection.flip_base_index is None:
                        edge_index = gm.get_edge_at(pos)
                        if edge_index is not None:
                            ui.selection.flip_base_index = edge_index

                            # Build candidates
                            i = edge_index
                            pts = gm.points
                            n = len(pts) - 1

                            ui.selection.flip_candidates = [
                                (FLIP_SAME, (pts[i], pts[i+1])),
                                (FLIP_PREFIX_REVERSE, (pts[0], pts[i+1])),
                                (FLIP_ROTATE, (pts[0], pts[n])),
                                (FLIP_SUFFIX_REVERSE, (pts[i], pts[n])),
                            ]
                        continue

                    # Step 2: base edge already selected -> choose candidate
                    for flip_type, (p1, p2) in ui.selection.flip_candidates:
                        if is_near_edge(pos, p1, p2):
                            gm.flip(ui.selection.flip_base_index, flip_type)
                            ui.selection.clear_flip()
                            break

            # --- mouse up ---
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_point = None

            # --- mouse move ---
            elif event.type == pygame.MOUSEMOTION:
                pos = pygame.mouse.get_pos()
                mode = ui.current_mode

                if dragging_point:
                    dragging_point.x, dragging_point.y = pos
                else:
                    ui.selection.clear_hover()

                    if mode in {MOVE_SPLIT, DELETE_POINT}:
                        # hover points
                        p = gm.get_point_at(pos)
                        if p:
                            ui.selection.hover_point = p
                        else:
                            ui.selection.hover_point = None

                    if mode in {MOVE_SPLIT, FLIP}:
                        # hover edges
                        edge_index = gm.get_edge_at(pos)
                        if edge_index is not None:
                            ui.selection.hover_edge_index = edge_index
                        else:
                            ui.selection.hover_edge_index = None

            # --- keyboard ---
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if ui.selection.selected_point:
                        gm.delete_point(ui.selection.selected_point)
                        ui.selection.clear()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
