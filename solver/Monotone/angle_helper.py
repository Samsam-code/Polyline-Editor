import math

def vector_of_angle(theta):
    """Return the unit vector associated with ``theta``"""
    return (math.cos(theta), math.sin(theta))

def angle_of_vector(u):
    return math.atan2(u[1], u[0])

def critical_angle(a, b):
    dx = a[0] - b[0]
    dy = a[1] - b[1]
    return math.atan2(-dx, dy)