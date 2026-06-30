import pygame
import sys

from core.geometry_manager import GeometryManager, dist2_to_edge
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

def main(initial_polyline=[]):
    # Init pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Polyline Editor")
    clock = pygame.time.Clock()

    # Define manager classes
    gm = GeometryManager(initial_polyline)
    ui = UIManager()
    if not initial_polyline:
        ui.set_mode(ADD_POINT)
    else:
        ui.set_mode(FLIP)
        
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
                    best_ft = None
                    best_dist2 = float("inf")

                    for flip_type, (p1, p2) in ui.selection.flip_candidates:
                        dist2 = dist2_to_edge(pos, p1, p2)
                        if dist2 < best_dist2:
                            best_ft, best_dist2 = flip_type, dist2

                    if best_ft is not None and best_dist2 <= 49:
                        gm.flip(ui.selection.flip_base_index, best_ft)
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
    hilbert3 = [(77, 75), (75, 128), (124, 127), (126, 70), (177, 74), (227, 72), (228, 130), (177, 123), (176, 181), (228, 175), (225, 229), (177, 229), (124, 224), (127, 169), (69, 175), (74, 226), (75, 279), (122, 268), (126, 323), (70, 324), (74, 376), (77, 427), (127, 428), (121, 376), (179, 377), (178, 424), (229, 426), (225, 373), (223, 317), (170, 319), (171, 279), (228, 277), (279, 278), (322, 273), (324, 325), (270, 327), (274, 374), (276, 424), (327, 421), (323, 375), (377, 372), (372, 425), (428, 425), (425, 373), (430, 321), (375, 327), (371, 271), (423, 276), (425, 222), (424, 176), (377, 174), (374, 220), (325, 224), (275, 223), (273, 171), (327, 175), (327, 123), (276, 127), (275, 73), (328, 73), (371, 75), (371, 127), (427, 127), (425, 71)]
    original_pb = [(315, 252), (144, 405), (595, 414), (707, 374), (508, 350), (379, 372), (287, 111), (332, -1000000)]
    pb2 =[(310, 327), (144, 405), (595, 414), (707, 374), (508, 350), (446, 404), (430, 331), (384, 388), (380, 298), (350, 363), (280, 109), (241, 136), (280, 175), (295, 188), (234, 177), (250, 191), (264, 206), (182, 141), (221, 163), (245, 99), (307, 70), (308, 61), (306, 52), (332, -1000000)]
    
    no_pinch = [(434, 443), (424, 286), (248, 427), (293, 406), (438, 588), (401, 510), (618, 439), (539, 458), (376, 177), (283, 171), (597, 151), (603, 82), (639, 342), (685, 348), (508, 377), (518, 225)]

    convex_next_to_convex =  [(105, 228), (197, 130), (277, 119), (100, 292), (131, 365), (298, 125), (526, 114), (312, 159), (167, 369), (438, 213), (343, 284), (212, 396), (341, 304), (300, 377), (441, 250), (456, 178), (315, 184), (490, 137), (570, 108), (602, 172), (587, 293), (337, 361), (495, 371)]
    
    star = [(454, 53), (406, 200), (398, 144), (383, 105), (334, 149), (274, 57), (323, 196), (267, 169), (184, 176), (281, 223), (79, 221), (222, 242), (270, 259), (233, 278), (173, 351), (154, 463), (289, 346), (233, 429), (330, 322), (332, 463), (352, 384), (384, 529), (376, 341), (419, 332), (478, 457), (458, 347), (551, 521), (459, 302), (581, 403), (744, 338), (491, 248), (464, 231), (679, 145), (574, 172), (596, 90), (487, 163), (459, 118)]
    monotone = [(42, 327), (71, 482), (109, 312), (142, 430), (149, 181), (173, 310), (188, 279), (207, 191), (213, 534), (227, 374), (236, 474), (240, 272), (278, 373), (302, 224), (344, 391), (350, 260), (359, 124), (387, 426), (409, 241), (421, 390), (423, 504), (438, 155), (463, 284), (502, 357), (517, 265), (537, 395), (569, 126), (586, 483), (635, 186), (638, 337), (672, 529), (708, 383), (730, 248), (747, 181), (779, 436), (802, 346)]
    degen_star = [(454, 53), (596, 90), (679, 145), (459, 118), (574, 172), (487, 163), (744, 338), (383, 105), (491, 248), (581, 403), (464, 231), (398, 144), (551, 521), (459, 312), (458, 347), (478, 457), (406, 200), (419, 332), (376, 341), (384, 529), (352, 384), (332, 463), (330, 322), (289, 346), (233, 429), (323, 196), (154, 463), (270, 259), (334, 149), (281, 223), (233, 278), (173, 351), (222, 242), (267, 169), (184, 176), (79, 221), (274, 57)]
    main(monotone)
