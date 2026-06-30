"""
This file contains a BFS solver for the plane spanning path reconfiguration problem.
"""
from Core.polyline import forget_orientation
from Core.flip import get_all_valid_flips, flip

def bfs_solver_info(points, start, target):
    """ 
    Performs a BFS on the flip graph to find a flip sequence from
    ``start`` path to ``target`` path.

    Both these paths must be plane and over the same set of points.
    """
    start = forget_orientation(start)
    target = forget_orientation(target)
    if start == target: return []

    paths = [start]
    visited = [start]
    flips = [None]
    pred = [0]
    idx = 0
    found = False
    while not found and paths:
        current = paths.pop(0)
        for i, ft in get_all_valid_flips(points, current):
            new_path = flip(current, i, ft)
            if new_path in visited:
                continue

            paths.append(new_path)
            visited.append(new_path)
            pred.append(idx)
            flips.append((i, ft))

            if new_path == target:
                found = True 
                break
        idx+=1

    if found:
        #print(f"A solution has been found by visiting {len(pred)} paths in the flip graph.")
        i = len(pred)-1
        sequence = []
        while i > 0:
            sequence.append(flips[i])
            i = pred[i]

        sequence.reverse()
        #print(f"The flip sequence contains {len(sequence)} flips")
        return sequence, len(pred)
    
    else:
        raise ValueError("No path flip sequence found.")
    
def bfs_solver(points, start, target):
    return bfs_solver_info(points, start, target)[0]