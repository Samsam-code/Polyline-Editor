"""
This file will contain any function helpful for paths with a center

(Notably turning vertices and ray-edge crossings).
"""

import math
from Core.polyline import ccw

def barycenter(points):
    """ Return the barycenter of the ``points``. """
    x,y = 0,0
    for px, py in points:
        x += px
        y += py
    n = len(points)
    return (x / n, y / n)

def sort_ccw(points, center):
    """ 
    Return the list ``points`` sorted by the angle between 
    the horizontal axis and the vector from the ``center``. 
    """
    cx, cy = center
    return sorted(points, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))

def is_turning_vertex(points, center, path, k):
    i = path[k]
    iprev = path[k - 1]
    isucc = path[k + 1]
    return ccw(center, points[i], points[iprev]) == ccw(center, points[i], points[isucc])

def turning_vertices(points, center, path):
    """ Return the list of turning vertices of ``path`` relatively to ``center`` """
    return [k for k in range(1, len(path)-1) if is_turning_vertex(points, center, path, k)]


def single_ray_edge_crossings(points, center, path, k):
    """ Return the number of rays the edge ``k`` crosses.

    /!\ Supposes that the points are already sorted in CCW order.
    """
    i, j = path[k], path[k+1]
    if j < i:
        i, j = j, i
    
    if ccw(center, points[i], points[j]):
        return j-i-1
    else:
        return len(path)-j+i-1
    
def ray_edge_crossings(points, center, path):
    """ Return the number of ray-edge crossings in the path.

    /!\ Supposes that the points are already sorted in CCW order.
    """
    return sum(single_ray_edge_crossings(points, center, path, k) for k in range(len(path)-1))