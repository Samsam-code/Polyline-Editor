import math
from .angle_helper import *

def monotone_path(points, direction):
    """ Return the monotone path induced by ``points`` along ``direction``. """
    dx, dy = direction
    proj = [(x*dx + y*dy, i) for i, (x,y) in enumerate(points)]

    return [i for _, i in sorted(proj)]

def elementary_rotation(points, path, u, ccw=False):
    sign = 1 if ccw else -1
    theta0 = angle_of_vector(u)
    n = len(path)

    best_dtheta = None
    best_k = None

    for k in range(n - 1):
        i = path[k]
        j = path[k+1]

        theta_ab = critical_angle(points[i], points[j])

        dtheta = (sign*(theta_ab - theta0)) % (2*math.pi)
        if dtheta == 0:
            continue

        if best_dtheta is None or dtheta < best_dtheta:
            best_dtheta = dtheta
            best_k = k

    new_theta = (theta0 + sign*best_dtheta) % (2*math.pi)
    new_u = vector_of_angle(new_theta)

    new_path = path.copy()
    new_path[best_k], new_path[best_k+1] = new_path[best_k+1], new_path[best_k]

    return new_u, new_path

def get_all_monotone_paths(points):
    u = (0, 1)
    path0 = monotone_path(points, (0, 1))
    paths = [path0]
    u, path = elementary_rotation(points, path0, u)
    while path != path0:
        paths.append(path)
        u, path = elementary_rotation(points, path, u)

    return paths

if __name__ == "__main__":
    pass