from Core.polyline import forget_orientation
from Core.flip import get_all_valid_flips, get_all_valid_SR, flip, FT_REM_END
from GeneralCase.center_core import turning_vertices, ray_edge_crossings

import heapq

SUFFIX_ROTATION = FT_REM_END

def invariant(points, center, path):
    nb_turns = len(turning_vertices(points, center, path))
    nb_crossings = ray_edge_crossings(points, center, path)
    return nb_turns, nb_crossings

def diminish_turning_crossing_once(points, center, start):
    """ /!\ Supposes that points have been sorted by angle to the center """
    start_invariant = invariant(points, center, start)

    paths = [start]
    visited = [start]
    flips = [None]
    pred = [0]
    idx = 0
    found = False
    while not found and paths:
        current = paths.pop(0)
        for i, ft in get_all_valid_flips(points, current):
            new_path = flip(current, i, ft, forget_orientation=False)
            if new_path in visited:
                continue

            paths.append(new_path)
            visited.append(new_path)
            pred.append(idx)
            flips.append((i, ft))

            new_invariant = invariant(points, center, new_path)

            if new_invariant < start_invariant:
                found = True 
                break
        idx+=1

    if found:
        print(f"A solution has been found by visiting {len(pred)} paths in the flip graph.")
        i = len(pred)-1
        sequence = []
        while i > 0:
            sequence.append(flips[i])
            i = pred[i]

        sequence.reverse()
        print(f"The flip sequence contains {len(sequence)} flips")
        return sequence
    
    else:
        raise ValueError("No path flip sequence found.")
    
def diminish_turning_crossing_once_fixed_start_point(points, center, start):
    """ /!\ Supposes that points have been sorted by angle to the center """
    start_invariant = invariant(points, center, start)

    #print("All valid suffix rotation", get_all_valid_SR(points, start))

    paths = [(start_invariant, start, 0)] #heapq
    visited = [start]
    flips = [None]
    pred = [0]
    found = False
    while not found and paths:
        _, current, idx = heapq.heappop(paths)
        for i in get_all_valid_SR(points, current):
            new_path = flip(current, i, SUFFIX_ROTATION, forget_orientation=False)
            if new_path in visited:
                continue
            
            new_invariant = invariant(points, center, new_path)
            heapq.heappush(paths,(new_invariant,new_path, len(visited)))
            visited.append(new_path)
            pred.append(idx)
            flips.append(i)

            if new_invariant < start_invariant:
                #print("SOLUTION", new_path)
                found = True 
                break

    if found:
        print(f"A solution has been found by visiting {len(pred)} paths in the flip graph.")
        i = len(pred)-1
        sequence = []
        while i > 0:
            sequence.append((flips[i], SUFFIX_ROTATION))
            i = pred[i]

        sequence.reverse()
        print(f"The flip sequence contains {len(sequence)} flips")
        return sequence
    
    else:
        raise ValueError("No path flip sequence found.")
    
def diminish_turning_crossing_to_star(points, center, start, heuristic=invariant, end_condition=(0, 0)):
    """ /!\ Supposes that points have been sorted by angle to the center """
    start_invariant = heuristic(points, center, start)

    paths = [(start_invariant, start, 0)] #heapq
    visited = [start]
    flips = [None]
    pred = [0]
    found = False
    while not found and paths:
        _, current, idx = heapq.heappop(paths)
        for i, ft in get_all_valid_flips(points, current):
            new_path = flip(current, i, ft, forget_orientation=False)
            if new_path in visited:
                continue
            
            new_invariant = heuristic(points, center, new_path)
            heapq.heappush(paths,(new_invariant,new_path, len(visited)))
            visited.append(new_path)
            pred.append(idx)
            flips.append((i, ft))

            if new_invariant == end_condition:
                #print("SOLUTION", new_path)
                found = True 
                break

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



def diminish_turning_crossing_to_star_fixed_start_point(points, center, start, heuristic=invariant, end_condition=(0, 0)):
    """ /!\ Supposes that points have been sorted by angle to the center """
    start_invariant = heuristic(points, center, start)

    #print("All valid suffix rotation", get_all_valid_SR(points, start))

    paths = [(start_invariant, start, 0)] #heapq
    visited = [start]
    flips = [None]
    pred = [0]
    found = False
    while not found and paths:
        _, current, idx = heapq.heappop(paths)
        for i in get_all_valid_SR(points, current):
            new_path = flip(current, i, SUFFIX_ROTATION, forget_orientation=False)
            if new_path in visited:
                continue
            
            new_invariant = heuristic(points, center, new_path)
            heapq.heappush(paths,(new_invariant,new_path, len(visited)))
            visited.append(new_path)
            pred.append(idx)
            flips.append(i)

            if new_invariant == end_condition:
                #print("SOLUTION", new_path)
                found = True 
                break

    if found:
        #print(f"A solution has been found by visiting {len(pred)} paths in the flip graph.")
        i = len(pred)-1
        sequence = []
        while i > 0:
            sequence.append((flips[i], SUFFIX_ROTATION))
            i = pred[i]

        sequence.reverse()
        #print(f"The flip sequence contains {len(sequence)} flips")
        return sequence, len(pred)
    
    else:
        raise ValueError("No path flip sequence found.")