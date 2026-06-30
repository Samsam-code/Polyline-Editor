"""
A flip on a non-oriented polyline is a removal of an edge followed by 
an insertion of a new one such that the new configuration is still a 
non-oriented polyline.

Once we have removed an edge, there are at most 3 ways we add another one
in the configuration. These types of flip are encoded by the following constants: 
- ``FT_BEG_END``: The new edge connects the two previous extremities of the path;
- ``FT_BEG_REM``: The new edge connects the start of the previous path to one of 
the extremities of the removed edge;
- ``FT_REM_END``: The new edge connects the end of the previous path to one of
the extremities of the removed edge.
"""
from Core import polyline as pl

FT_BEG_END = 2
FT_BEG_REM = 1
FT_REM_END = 3
FLIP_TYPES = (FT_BEG_END, FT_BEG_REM, FT_REM_END)

def flip(path, idx_removed_edge, flip_type, forget_orientation=True):
    """ Performs the indicated flip on the path and returns the result. """
    if flip_type == FT_BEG_END:
        #[1, ..., i, i+1, ..., n] -> [i+1, ..., n, 1, ..., i]
        new_path = path[idx_removed_edge+1:] + path[:idx_removed_edge+1]
    elif flip_type == FT_BEG_REM:
        #[1, ..., i, i+1, ..., n] -> [i, ..., 1, i+1, ..., n]
        new_path = path[:idx_removed_edge+1][::-1] + path[idx_removed_edge+1:]
    elif flip_type == FT_REM_END:
        #[1, ..., i, i+1, ..., n] -> [1, ..., i, n, ..., i+1]
        new_path = path[:idx_removed_edge+1] + path[idx_removed_edge+1:][::-1]
    else : 
        raise ValueError(f"Unknown flip type : {flip_type}")
    
    if forget_orientation:
        return pl.forget_orientation(new_path)
    return new_path

# ===== Conversion: flip type <=> added edge =====

def encode_flip_type(path, idx_removed_edge, added_edge):
    """ Encodes the added edge of the flip in O(1) """
    rem1, rem2 = path[idx_removed_edge], path[idx_removed_edge+1]
    beg, end = path[0], path[-1]
    edge = set(added_edge)
    if edge == {beg, end}: return FT_BEG_END
    elif edge == {beg, rem2} and beg != rem1: return FT_BEG_REM
    elif edge == {rem1, end} and end != rem2: return FT_REM_END
    raise ValueError(f"Replacing {(rem1,rem2)} by {added_edge} is not a flip")

def decode_flip_type(path, idx_removed, flip_type):
    """ Decodes the added edge of the flip in O(1) """
    if flip_type == FT_BEG_END:
        return (path[0], path[-1])
    elif flip_type == FT_BEG_REM:
        return (path[0], path[idx_removed+1])
    elif flip_type == FT_REM_END:
        return (path[idx_removed], path[-1])
    raise ValueError(f"Unknown flip type : {flip_type}")

# ===== Check validity of a flip =====

def flip_produces_new_path(path, idx_removed_edge, added_edge):
    """ Checks whether the path obtained after performing the flip is still a path.
    
    The new path must be different from the previous one.
    """
    rem1, rem2 = path[idx_removed_edge], path[idx_removed_edge+1]
    beg, end = path[0], path[-1]
    edge = set(added_edge)
    return edge in ({beg, end}, {beg, rem2}, {rem1, end})

def flip_creates_intersection(points, path, idx_removed_edge, added_edge):
    """ Checks whether the flip creates an intersection in the path. """
    for i in range(len(path)-1):
        if i == idx_removed_edge: # Do not check with the removed edge
            continue
        if {path[i], path[i+1]}.intersection(added_edge): #skip adjacent edges
            continue
        if pl.segments_intersect(points[path[i]], points[path[i+1]], points[added_edge[0]], points[added_edge[1]]):
            return True
    return False

def is_flip_valid(points, path, idx_removed_edge, added_edge):
    """ Checks whether we can perform the flip. """
    return (
        flip_produces_new_path(path, idx_removed_edge, added_edge)
        and not flip_creates_intersection(points, path, idx_removed_edge, added_edge)
    )

def is_flip_type_valid(points, path, idx_removed_edge, flip_type, remove_redondancy=False):
    """ Checks whether we can perform the flip. """
    rem1, rem2 = path[idx_removed_edge], path[idx_removed_edge+1]
    add1, add2 = decode_flip_type(path, idx_removed_edge, flip_type)

    # No identity
    if (rem1,rem2)==(add1, add2) : return False

    if remove_redondancy:
        # Theses are doubling of flips FT_BEG_END already encodes. 
        # We consider them invalid to avoid redundant work.
        if rem1 == path[0] and flip_type == FT_REM_END: return False
        if rem2 == path[-1] and flip_type == FT_BEG_REM: return False

    return not flip_creates_intersection(points, path, idx_removed_edge, (add1, add2))

def get_all_valid_flips(points, path):
    """ Returns the list of all valid flips. Format: ``[..., (idx_rem, flip_type),...]`` """
    return [(i, ft) for i in range(len(path)-1) for ft in FLIP_TYPES 
            if is_flip_type_valid(points, path, i, ft, remove_redondancy=True)]

def get_all_valid_PR(points, path):
    """ Returns the list of all indices where the prefix rotation flip is available. """
    return [i for i in range(len(path)-1) if is_flip_type_valid(points, path, i, FT_BEG_REM)]

def get_all_valid_SR(points, path):
    """ Returns the list of all indices where the suffix rotation flip is available. """
    return [i for i in range(len(path)-1) if is_flip_type_valid(points, path, i, FT_REM_END)]

def flips_to_paths(start, flips):
    path = start
    sequence = [path]
    for f in flips:
        path = flip.flip(path, *f)
        sequence.append(path)
    return sequence