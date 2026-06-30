"""
Given a list of points ``[(x1, y1), (x2, y2), ..., (xn, yn)]``, 
a polyline is an oriented plane path represented by a list of distinct indices over these points.
"""

import random as rd

def generate_random_points(n, w=50, h=30):
    """ Returns a list of ``n`` random points in a ``w*h`` rectangle. """
    return [(w*rd.random(),h*rd.random()) for _ in range(n)]

def ccw(a, b, c):
    """ Checks whether ``a, b, c`` are listed in counter clockwise order. """
    return (c[1]-a[1]) * (b[0]-a[0]) > (b[1]-a[1]) * (c[0]-a[0])

def segments_intersect(p1, p2, q1, q2):
    """ Checks whether the segment ``[p1, p2]`` intersects the segment ``[q1, q2]``. """
    return ccw(p1, q1, q2) != ccw(p2, q1, q2) and (ccw(p1, p2, q1) != ccw(p1, p2, q2))

def line_intersection(p1, p2, q1, q2):
    """ Returns the intsersection point between lines ``(p1, p2)`` and ``(q1, q2)``. """
    p1x, p1y = p1
    p2x, p2y = p2
    q1x, q1y = q1
    q2x, q2y = q2

    pdx, pdy = p2x - p1x, p2y - p1y
    qdx, qdy = q2x - q1x, q2y - q1y

    det = pdx * qdy - pdy * qdx
    if det == 0:
        return None  # parallel or collinear (not handled here)

    t = ((q1x - p1x) * qdy - (q1y - p1y) * qdx) / det
    ix = p1x + t * pdx
    iy = p1y + t * pdy
    return (ix, iy)


def is_plane(points, path):
    """ Checks whether a polyline is plane (no crossing). """
    n = len(path)
    for i in range(n-3):
        p1, p2 = points[path[i]], points[path[i+1]]
        for j in range(i+2, n-1):
            q1, q2 = points[path[j]], points[path[j+1]]
            if segments_intersect(p1, p2, q1, q2):
                return False
    return True

def generate_random_polyline(points, shuffle_points=False, oriented=False):
    """ Returns a random plane spanning path over the ``points``.
        
    If ``shuffle_points`` is set to ``True``, the path returned will be 
    ``[0, 1, ..., n-1]`` but the list of points will be shuffled. 
    """
    path = list(range(len(points)))
    if shuffle_points:
        while not is_plane(points, path):
            rd.shuffle(points)
    else:
        rd.shuffle(path)
        while not is_plane(points, path):
            rd.shuffle(path)
        
    if not oriented:
        return forget_orientation(path)
    else:
        return path

def forget_orientation(path):
    """ Return the ``path`` where the orientation has been forgotten. """
    # Here we just ensure that the index of the last vertex of the path
    # is greater than the first one.
    if path[0] > path[-1]:
        return list(reversed(path))
    return path


import math

def generate_random_path(
        n, w=50, h=30,
        min_len=1.0, max_len=50.0, backtrack=5):

    pts = [(w*rd.random(),h*rd.random())]

    tries_per_step = 50+n//2
    while len(pts) < n:
        base = pts[-1]
        new_pt = None

        for _ in range(tries_per_step):
            angle = rd.uniform(0, 2*math.pi)
            length = rd.uniform(min_len, max_len)

            dx = length * math.cos(angle)
            dy = length * math.sin(angle)
            candidate = (base[0] + dx, base[1] + dy)

            if not(0 <= candidate[0] <= w and 0 <=candidate[1] <= h) :
                continue

            ok = True
            for i in range(len(pts)-2):
                if segments_intersect(pts[i], pts[i+1], base, candidate):
                    ok = False
                    break

            if ok:
                new_pt = candidate
                break  # take the first valid one

        if new_pt is None:
            # backtrack if stuck
            if len(pts) > backtrack:
                pts = pts[:-backtrack]
                continue
            else:
                pts = [pts[0]]

        pts.append(new_pt)

    return pts
