from ConvexHull.convex_hull import convex_hull, walk_cycle, cross, convex_layers
from Core import flip

PREFIX_REVERSAL = flip.FT_BEG_REM
ROTATION = flip.FT_BEG_END
SUFFIX_REVERSAL = flip.FT_REM_END

def fixed_start_switch(points, path, index):
    """ Return a flip sequence corresponding to switching the edge at position ``index`` using 
    only suffix reversal flips assuming that ``(point, path)`` represents a monotone path.
    """
    # Precompute lookup tables
    point_to_index = {points[p]:p for p in path}
    path_to_index = {p: i for i, p in enumerate(path)}

    # Extract suffix
    suffix_i = [points[i] for i in path[index:]]
    suffix_i1= suffix_i[1:]

    # Compute hull arcs for index and index+1
    hull_i = [point_to_index[p] for p in convex_hull(suffix_i)]
    hull_i1 = [point_to_index[p] for p in convex_hull(suffix_i1)]

    # Determine orientation
    ccw = cross(points[path[-1]], points[path[index]], points[path[index+1]])>=0
    arc_i = walk_cycle(hull_i, hull_i.index(path[-1]), hull_i.index(path[index]), ccw)
    arc_i1 = walk_cycle(hull_i1, hull_i1.index(path[-1]), hull_i1.index(path[index+1]), not ccw)
   
    # Choose the shorter arc
    hull_arc = min(arc_i, arc_i1, key=len)

    flip_sequence = []
    
    # Move endpoint along hull
    for hull_vertex in hull_arc[1:-1]:
        j = path_to_index[hull_vertex]
        flip_sequence.append((j, SUFFIX_REVERSAL))
        flip_sequence.append((j-1, SUFFIX_REVERSAL))

    # Perform the switch
    if hull_arc[-1] == path[index]:
        switch = [(i, SUFFIX_REVERSAL) for i in (index, index-1, index, index+1)]
    else:
        switch = [(i, SUFFIX_REVERSAL) for i in (index+1, index, index-1, index)]

    # Add the reverse at the end
    return flip_sequence + switch + list(reversed(flip_sequence))

def monotone_to_onion(points, path):
    """ Return a flip sequence transforming the monotone path 
    ``(point, path)`` to an onion configuration.
    """
    # AHHHHHHHHHH I forgot a case when building bridges. I need to modify that function. 
    # Refer to the LaTeX for the correct algorithm
    # Precompute lookup tables
    point_to_index = {points[p]:p for p in path}
    path_to_index = {p: i for i, p in enumerate(path)}

    flip_sequence = []

    def perform_flip(i, flip_type):
        nonlocal path, flip_sequence
        flip_sequence.append((i, flip_type))
        return flip.flip(path, i, flip_type, forget_orientation=False)
    
    def reverse_path():
        return perform_flip(len(path), PREFIX_REVERSAL)

    # Compute convex layer decomposition
    convex_layer_list = [[point_to_index[p] for p in layer] for layer in convex_layers(points)]
    
    # Outer hull
    hull = convex_layer_list[0]
    print("hull", hull)

    # Identify the endpoints
    print("path", path)
    
    # Form the arc end -> start and move the end along it
    start, end = path[0], path[-1]
    print(start, end)
    start_hull, end_hull = hull.index(start), hull.index(end)
    upper_hull = walk_cycle(hull, end_hull, start_hull)
    for hull_vertex in upper_hull[1:-1]:
        j = path_to_index[hull_vertex]
        path = perform_flip(j, SUFFIX_REVERSAL)
        path = perform_flip(j-1, SUFFIX_REVERSAL)
    
    path = perform_flip(0, SUFFIX_REVERSAL)

    # Construct now the lower hull
    lower_hull = walk_cycle(hull, start_hull, end_hull)
    need_reconstruct = False
    for hv_i, hull_vertex in enumerate(lower_hull[1:-1]):
        if not need_reconstruct:
            # Particular steps where the first points of the lower hull
            # correspond exactly to the beginning of the path
            # so only one rotation flip is needed at the beginning
            if path[-hv_i-1] == hull_vertex:
                continue
            elif hv_i != 0:
                path = perform_flip(len(path)-hv_i-1, ROTATION)
            need_reconstruct = True

        hv_path_index = path.index(hull_vertex)
        path = perform_flip(hv_path_index-1, PREFIX_REVERSAL)
        path = perform_flip(hv_path_index, PREFIX_REVERSAL)

    if not need_reconstruct:
        # If the lower layer was already constructed, 
        # make sure you still flip the last edge to the correct location
        path = perform_flip(len(path)-hv_i, ROTATION)

    # The outer layer is now complete.
    # Let's build the next one similarly
    for hull in convex_layer_list[1:]:
        print("hull", hull)

        # Identify the endpoints
        print("path", path)
        i_start = path.index(end)+1
        start, end = path[i_start], path[-1]
        print(start, end)

        start_hull, end_hull = hull.index(start), hull.index(end)
        upper_hull = walk_cycle(hull, end_hull, start_hull)
        path_to_index = {p: i for i, p in enumerate(path)}
        for hull_vertex in upper_hull[1:-1]:
            j = path_to_index[hull_vertex]
            path = perform_flip(j, SUFFIX_REVERSAL)
            path = perform_flip(j-1, SUFFIX_REVERSAL)
        
        # Make the other hull extremity an end point and construct the bridge between the outer layer and this layer
        path = perform_flip(i_start, ROTATION)

        # Construct now the lower hull
        lower_hull = walk_cycle(hull, start_hull, end_hull)
        need_reconstruct = False
        for hv_i, hull_vertex in enumerate(lower_hull[1:-1]):
            if not need_reconstruct:
                # Particular steps where the first points of the lower hull
                # correspond exactly to the beginning of the path
                # so only one rotation flip is needed at the beginning
                if path[hv_i] == hull_vertex:
                    continue
                elif hv_i != 0:
                    path = perform_flip(hv_i-1, ROTATION)
                need_reconstruct = True

            hv_path_index = path.index(hull_vertex)
            path = perform_flip(hv_path_index, SUFFIX_REVERSAL)
            path = perform_flip(hv_path_index-1, SUFFIX_REVERSAL)

        if not need_reconstruct:
            # If the lower layer was already constructed, 
            # make sure you still flip the last edge to the correct location
            path = perform_flip(hv_i, ROTATION)

        # To simplify the implementation, reverse the path
        path = reverse_path()


    return flip_sequence
    

    



