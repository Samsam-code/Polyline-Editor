def cross(o, a, b):
    """2D cross product of OA and OB vectors.
    Returns positive if OAB makes a counter-clockwise turn,
    negative for clockwise, and zero if collinear.
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def convex_hull(points):
    """ Returns the points forming the convex hull in CCW order. """
    points = sorted(points)  # sort lexicographically
    if len(points) <= 1:
        return points

    # Build lower hull
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    # Build upper hull
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    # Concatenate lower and upper hulls (excluding last point of each because it repeats)
    return lower[:-1] + upper[:-1]

def convex_layers(points):
    """ Returns a list of convex hull layers (outermost first). """
    pts = points.copy()  # copy
    layers = []

    while len(pts) > 1:
        hull = convex_hull(pts)
        layers.append(hull)

        # Remove hull points from the set
        hull_set = set(hull)
        pts = [p for p in pts if p not in hull_set]

    # If one point remains, it forms the last layer
    if pts:
        layers.append(pts)

    return layers


def walk_cycle(hull, start, end, ccw=True):
    step = 1 if ccw else -1
    m = len(hull)
    i = start
    out = []
    while True:
        out.append(hull[i])
        if i == end:
            break
        i = (i + step) % m
    return out

def hull_arcs(hull, a, b):
    ia = hull.index(a)
    ib = hull.index(b)
    ccw = walk_cycle(hull, ia, ib, True)
    cw  = walk_cycle(hull, ia, ib, False)
    return ccw, cw

