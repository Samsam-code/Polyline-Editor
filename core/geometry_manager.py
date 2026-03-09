from .point import Point
from .flip_types import (
    FLIP_SAME,
    FLIP_PREFIX_REVERSE,
    FLIP_ROTATE,
    FLIP_SUFFIX_REVERSE,
)

def dist2_to_edge(pos, p1, p2):
    """ Return the distance squared from `pos`to the edge `[p1, p2]`. """
    x, y = pos
    x1, y1 = p1.x, p1.y
    x2, y2 = p2.x, p2.y

    ex, ey = x2 - x1, y2 - y1
    if ex == 0 and ey == 0:
        t = 0
    else:
        t = ((x - x1) * ex + (y - y1) * ey) / (ex * ex + ey * ey)
        t = max(0, min(1, t))

    proj_x = x1 + t * ex
    proj_y = y1 + t * ey
    return (proj_x - x) ** 2 + (proj_y - y) ** 2

def is_near_edge(pos, p1, p2, threshold=7):
    return dist2_to_edge(pos, p1, p2) <= threshold ** 2

class GeometryManager:
    """
    Manages a single polyline as an ordered list of Point objects.
    Edges are implicit between consecutive points.
    """
    def __init__(self):
        self.points = []

    @property
    def edges(self):
        return [
            (self.points[i], self.points[i + 1])
            for i in range(len(self.points) - 1)
        ]

    # --- core operations ---

    def append_point(self, x, y):
        p = Point(x, y)
        self.points.append(p)
        return p

    def insert_point_on_edge(self, edge_index, x, y):
        p = Point(x, y)
        self.points.insert(edge_index + 1, p)
        return p

    def delete_point(self, point):
        if point in self.points:
            self.points.remove(point)

    def move_point(self, point, x, y):
        point.x = x
        point.y = y

    # --- picking helpers ---

    def get_point_at(self, pos, radius=8):
        x, y = pos
        for p in self.points:
            if (p.x - x) ** 2 + (p.y - y) ** 2 <= radius ** 2:
                return p
        return None

    def get_edge_at(self, pos, threshold=7):
        best_i = None
        best_dist2 = float("inf")

        for i in range(len(self.points) - 1):
            p1 = self.points[i]
            p2 = self.points[i + 1]
            dist2 = dist2_to_edge(pos, p1, p2)

            if dist2 < best_dist2:
                best_i, best_dist2 = i, dist2

        if best_i is not None and best_dist2 <= threshold ** 2:
            return best_i
        return None
    
    def flip(self, i, flip_type):
        pts = self.points

        if flip_type == FLIP_SAME:
            return

        elif flip_type == FLIP_PREFIX_REVERSE:
            # [0..i] reversed + [i+1..end]
            self.points = pts[i::-1] + pts[i+1:]

        elif flip_type == FLIP_ROTATE:
            # [i+1..end] + [0..i]
            self.points = pts[i+1:] + pts[:i+1]

        elif flip_type == FLIP_SUFFIX_REVERSE:
            # [0..i] + reversed [i+1..end]
            self.points = pts[:i+1] + pts[:i:-1]
    
    def export_to_tikz(self, scale=100):
        lines = []

        # Begin TikZ
        lines.append("\\begin{tikzpicture}")

        # Define the points
        lines.append("\n% Define points")
        for i, p in enumerate(self.points):
            lines.append(f"\\coordinate (p{i+1}) at ({p.x/scale:.2f},{p.y/scale:.2f});")

        # Draw polyline
        lines.append("\n% Path edges")

        lines.append("\\draw[thick, blue] "+
                     " -- ".join([f"(p{i+1})" for i in range(len(self.points))])+
                     ";")

        # Draw points with labels
        lines.append("\n% Draw points")
        lines.append("\\foreach \\p/\\name in {"+
                     ", ".join([f"p{i+1}/$p_{{{i+1}}}$" for i in range(len(self.points))])+
                     "}")
        lines.append("    \\filldraw[black] \\p circle (2pt); %node[above] {\\name};\n")

        # End TikZ
        lines.append("\\end{tikzpicture}\n")

        return "\n".join(lines)



