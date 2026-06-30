from Core import polyline as pl
from Core import flip
from ConvexHull import convex_hull as ch
import random

PREFIX_REVERSAL = flip.FT_BEG_REM
ROTATION = flip.FT_BEG_END
SUFFIX_REVERSAL = flip.FT_REM_END

#convex2 = convex in convex
def decompose_convex2(points):
    """ Return both the outer layer and the inner layer in CCW order. """
    outer_hull = ch.convex_hull(points)
    set_outer_hull = set(outer_hull)
    inner_hull = ch.convex_hull([i for i in points if not i in set_outer_hull])
    return outer_hull, inner_hull

def generate_random_convex2_points(max_n, w=50, h=30):
    points = pl.generate_random_points(max_n, w, h)
    outer, inner = decompose_convex2(points)
    points = outer + inner
    random.shuffle(points)
    return points

def convex2_to_canonical(points, path):
    flip_sequence = []

    def perform_flip(i, flip_type):
        print((i, flip_type))
        flip_sequence.append((i, flip_type))
        return flip.flip(path, i, flip_type, forget_orientation=False)
    
    def reverse_path():
        return perform_flip(len(path), PREFIX_REVERSAL)
    
    point_to_index = {p: i for i, p in enumerate(points)}
    outer_hull, inner_hull = decompose_convex2(points)
    outer_hull = [point_to_index[i] for i in outer_hull]
    inner_hull = [point_to_index[i] for i in inner_hull]
    outer_index = {v:i for i,v in enumerate(outer_hull)} 
    inner_index = {v:i for i,v in enumerate(inner_hull)}

    def get_neighbors(v, layer, layer_index):
        """ Returns ``(u_ccw, u_cw)`` the neighbors of ``v`` in ``layer``"""
        iv = layer_index[v]
        u_ccw = layer[0] if iv == len(layer)-1 else layer[iv+1]
        u_cw = layer[iv-1]
        return (u_ccw, u_cw)

    def get_closest_intersection_index(i1, i2, path):
        """ Return the index of the segment the closest to ``i1`` in ``path`` that intersects 
        the segment between points whose indices are ``i1`` and ``i2`` in ``points``. """

        #print(path, i1, i2)
        p1, p2 = points[i1], points[i2]
        p1x, p2x = p1

        segments = [(points[path[i]], points[path[i+1]]) for i in range(len(path)-1)]

        best_i = None
        best_dist = float("inf")

        for index, (a, b) in enumerate(segments):
            if not pl.segments_intersect(p1, p2, a, b):
                continue
            if p1 in (a, b) or p2 in (a, b):
                continue
            ix, iy = pl.line_intersection(p1, p2, a, b)
            dist_to_p1 = abs(ix+iy-p1x-p2x) #Manhattan suffices here
            if dist_to_p1 < best_dist:
                best_dist = dist_to_p1
                best_i = index
                print(index)

        #input(best_i)
        return best_i

    def handle_start_intersection(i_inter_edge, path):
        """
        Handle cases where there is an edge preventing the start to connect to its neighbor.
        """
        nonlocal points, outer_hull, outer_index, inner_hull, inner_index
        print("i_inter_edge", i_inter_edge)
        e1, e2 = path[i_inter_edge], path[i_inter_edge+1]
        if e2 in inner_index:
            # Easy case where we can just flip the blocking edge to become a diagonal
            return perform_flip(i_inter_edge, PREFIX_REVERSAL)

        #Otherwise, e2 is in outer layer and there could be some other edge blocking the flip.
        if get_closest_intersection_index(e2, path[0], path) is None:
            # Easy case: nothing blocks the improving flip
            return perform_flip(i_inter_edge, PREFIX_REVERSAL)
        else:
            # Harder case: there is at least a point on the inner layer in the triangle (start, e1, e2)
            # Here, what happens is that the path must first follow some verticies in the inner layer in order
            # until it reaches the other point closest to (e1, e2) in the inner layer.
            # Then, visit all the other verticies remaining in this side of (e1, e2)
            
            # In this case, we want first to identify p the other point on the inner layer on the same side as the start 
            # that is the closest to (e1, e2).
            
            p = path[0]
            ccw_nbor, cw_nbor= get_neighbors(p, inner_hull, inner_index)

            pe1, pe2 = points[e1], points[e2]
            inter_is_ccw = pl.segments_intersect(points[p], points[ccw_nbor], pe1, pe2)

            if inter_is_ccw:
                while not pl.segments_intersect(points[p], points[cw_nbor], pe1, pe2):
                    p = cw_nbor
                    ccw_nbor, cw_nbor = get_neighbors(p, inner_hull, inner_index)
                p_nbor = ccw_nbor

            else:
                while not pl.segments_intersect(points[p], points[ccw_nbor], pe1, pe2):
                    p = ccw_nbor
                    ccw_nbor, cw_nbor = get_neighbors(p, inner_hull, inner_index)
                p_nbor = cw_nbor

            # Now that p is identified, there are 2 cases:
            # Either p_nbor is its predecessor and we can get rid (e1, e2) in 3 flips
            # Or its not and we can get rid of that big diagonal (e1, e2) in 4 flips.
            ip = path.index(p)
            if path[ip-1] == p_nbor:
                path = perform_flip(ip-1, PREFIX_REVERSAL)
                path = perform_flip(ip, PREFIX_REVERSAL) # Always legal since p is in the triangle (start, e1, e2)
                path = perform_flip(i_inter_edge, PREFIX_REVERSAL)
            else:
                path = perform_flip(ip-1, PREFIX_REVERSAL)
                path = perform_flip(path.index(p_nbor), PREFIX_REVERSAL) 
                path = perform_flip(path.index(p), PREFIX_REVERSAL) 
                path = perform_flip(i_inter_edge, PREFIX_REVERSAL)
            
            return path
        
        
    # --- main loop ---
    while True:
        start_outer_layer = False
        if path[0] in outer_index:
            print("START")
            start_outer_layer = True
            # Start is in outer layer
            ccw_nbor, cw_nbor = get_neighbors(path[0], outer_hull, outer_index)
            if cw_nbor == path[1]:
                # The edge to CW neighbor is well placed
                # Let's try to place the CCW edge
                ccw_nbor_path_index = path.index(ccw_nbor)
                ccw_nbor2, _ = get_neighbors(ccw_nbor, outer_hull, outer_index)

                if path[ccw_nbor_path_index-1] == ccw_nbor2:
                    # the edge we would have to flip is already well placed
                    # So we don't flip it.
                    if path[-1] in outer_index:
                        # If the end is on the outerlayer as well, that means that
                        # the extremities are neighbor to one another.
                        # so we find an edge that is miss placed and we rotate it.
                        for i in range(len(path)):
                            if path[i+1] not in outer_hull:
                                path = perform_flip(i, ROTATION)
                                break
                        continue
                    else:
                        # Otherwise, we work on the inner layer.
                        #print("aaaaaaaaaa222")
                        pass
                        
                else:
                    # Otherwise, the edge we want to flip is in a bad position.
                    # So we can flip it and go the the next iteration 
                    path = perform_flip(ccw_nbor_path_index-1, PREFIX_REVERSAL)
                    #print("bbbbbbbbbbbbbb")
                    continue
            
            elif ccw_nbor == path[1]:
                # The edge to CCW neighbor is well placed
                # Let's try to place the CW edge by doing the symmetric of the previous case
                cw_nbor_path_index = path.index(cw_nbor)
                _, cw_nbor2 = get_neighbors(cw_nbor, outer_hull, outer_index)

                if path[cw_nbor_path_index-1] == cw_nbor2:
                    if path[-1] in outer_index:
                        # If the end is on the outerlayer as well, that means that
                        # the extremities are neighbor to one another.
                        # so we find an edge that is miss placed and we rotate it.
                        #print("ccccccccccccc11111111")
                        for i in range(len(path)):
                            if path[i+1] not in outer_hull:
                                path = perform_flip(i, ROTATION)
                                break
                        continue
                    else:
                        # Otherwise, we work on the inner layer.
                        #print("ccccccccccccc2222222")
                        pass
                else:
                    path = perform_flip(cw_nbor_path_index-1, PREFIX_REVERSAL)
                    #print("dddddddddddddd")
                    continue

            else:
                # The first edge is badly placed. So no matter what, we can either 
                # place correctly the CCW one or the CW one

                # Try the CCW one
                ccw_nbor_path_index = path.index(ccw_nbor)
                ccw_nbor2, _ = get_neighbors(ccw_nbor, outer_hull, outer_index)

                if path[ccw_nbor_path_index-1] == ccw_nbor2:
                    # the edge we would like to flip is already well placed
                    # So go with the other one instead (as it is garanteed to be badly placed).
                    cw_nbor_path_index = path.index(cw_nbor)
                    path = perform_flip(cw_nbor_path_index-1, PREFIX_REVERSAL)
                    #print("eeeeeeeee111111111")
                else:
                    path = perform_flip(ccw_nbor_path_index-1, PREFIX_REVERSAL)
                    #print("eeeeeeeeeeee2222222222")
                continue

        elif path[-1] in outer_index:
            # If the end is in the outer layer but not the start
            # Just reverse the path for simplicity of implementation
            path = reverse_path()
            print("reverse")
            continue
        
        # At this point, 
        # Either both endpoints are in the inner layer
        # Or the start is in the outer layer and the end is in the inner layer with some constraints
        # on how the path visit the outer layers.

        if start_outer_layer:
            print("OTHER PART")
            # Start by improving the situation in the inner layer (similarly to the outer layer but for endpoint)
            ccw_nbor, cw_nbor = get_neighbors(path[-1], inner_hull, inner_index)
            if ccw_nbor == path[-1]:
                # There is only one point on the inner layer
                # So we have already finished
                break

            if cw_nbor == path[-2]:
                # The edge to CW neighbor is well placed
                # Let's try to place the CCW edge

                # But first, check for intersections:
                i_inter_edge = get_closest_intersection_index(path[-1], ccw_nbor, path)
                if i_inter_edge is not None:
                    # The edge intersecting the segment we want to place can be flipped
                    path = perform_flip(i_inter_edge, SUFFIX_REVERSAL)
                    continue

                ccw_nbor_path_index = path.index(ccw_nbor)
                ccw_nbor2, _ = get_neighbors(ccw_nbor, inner_hull, inner_index)

                if path[ccw_nbor_path_index+1] == ccw_nbor2:
                    # the edge we would have to flip is already well placed
                    # at this point, either it's over or there are some irregularities on the outer path.
                    if ccw_nbor_path_index == len(outer_hull):
                        # in this case, the outer path follows exactly the outer hull
                        # and the inner hull is correctly done so we can end
                        break
                    # Otherwise, there are irregularities on the outer path (it visits some verticies of the inner hull)
                    # First, we check out whether the inner path is "looping" (the endpoint is the neighbor of the entry of the inner path)
                    if not all([p in inner_index for p in path[ccw_nbor_path_index:]]):
                        # The inner path is not looping so the endpoint is already next to an irregularity
                        # In this case, we just flip the good edge of CCW neighbor
                        path = perform_flip(ccw_nbor_path_index, SUFFIX_REVERSAL)
                    else:
                        # The inner path is indeed looping
                        # So we search for diagonals in the inner path so that we can move the end extremity next to the irregularities 
                        diag_i = len(path)-2
                        cw_nbor_i = cw_nbor
                        while path[diag_i] == cw_nbor_i:
                            diag_i-=1
                            _, cw_nbor_i = get_neighbors(cw_nbor_i, inner_hull, inner_index)

                        # diag_i is now a vertex such that the edge path[diag_i-1] --- path[diag_i] is a diagonal
                        # and cw_nbor_i is an irregular vertex on the outer path.

                        # Now that an irregularity is located, we can perform a first flip to move the end to that place.
                        path = perform_flip(diag_i, SUFFIX_REVERSAL)

                        # Next we can flip the edge going out of the CW neighbor of the end point
                        path = perform_flip(path.index(cw_nbor_i), SUFFIX_REVERSAL)

                    # Finally, now that the irragularity has been split, 
                    # it reversed the situation next to the start of the path
                    # so we can perform a flip that improves the outer layer again
                    continue # Improving flip be done during the next loop
                else:
                    path = perform_flip(ccw_nbor_path_index, SUFFIX_REVERSAL)
                    #print("bbbbbbbbbbbbbb")
                    continue
            
            elif ccw_nbor == path[-2]:
                # The edge to CCW neighbor is well placed
                # Let's try to place the CW edge by doing the symmetric of the previous case

                # But first, check for intersections:
                i_inter_edge = get_closest_intersection_index(path[-1], cw_nbor, path)
                if i_inter_edge is not None:
                    # The edge intersecting the segment we want to place can be flipped
                    path = perform_flip(i_inter_edge, SUFFIX_REVERSAL)
                    continue

                cw_nbor_path_index = path.index(cw_nbor)
                _, cw_nbor2 = get_neighbors(cw_nbor, inner_hull, inner_index)

                if path[cw_nbor_path_index+1] == cw_nbor2:
                    if cw_nbor_path_index == len(outer_hull):
                        break
                    if not all([p in inner_index for p in path[cw_nbor_path_index:]]):
                        # The inner path is not looping so the endpoint is already next to an irregularity
                        # In this case, we just flip the good edge of CCW neighbor
                        path = perform_flip(cw_nbor_path_index, SUFFIX_REVERSAL)
                    else:
                        diag_i = len(path)-2
                        ccw_nbor_i = ccw_nbor
                        while path[diag_i] == ccw_nbor_i:
                            diag_i-=1
                            ccw_nbor_i, _ = get_neighbors(ccw_nbor_i, inner_hull, inner_index)

                        # diag_i is now a vertex such that the edge path[diag_i-1] --- path[diag_i] is a diagonal
                        # and ccw_nbor_i is an irregular vertex on the outer path.

                        path = perform_flip(diag_i, SUFFIX_REVERSAL)
                        path = perform_flip(path.index(ccw_nbor_i), SUFFIX_REVERSAL)

                    continue # Improving flip will be done during the next loop
                else:
                    path = perform_flip(cw_nbor_path_index, SUFFIX_REVERSAL)
                    #print("dddddddddddddd")
                    continue

            else:
                # The last edge is badly placed, so the endpath is surrounded by irregularities.
                # So we can for instance split the CCW irregularity
                # But first, check for intersections:
                i_inter_edge = get_closest_intersection_index(path[-1], ccw_nbor, path)
                if i_inter_edge is not None:
                    # The edge intersecting the segment we want to place can be flipped
                    path = perform_flip(i_inter_edge, SUFFIX_REVERSAL)
                    continue

                path = perform_flip(path.index(ccw_nbor), SUFFIX_REVERSAL)
                continue # Improving flip will be done during the next loop
            
        print("LAST PART")
        # If we get to that point, that means both endpoints are in the inner layer
        # The idea now is to improve the inner layer from the start point until 
        # either an endpoint ends up being in the outer layer
        # or the two end points end up being neighbor, in which case we will rotate a missplaced edge
        
        # At this point, there are no constraint in the path so we have to be very careful about potential intersections
        print(path, inner_hull, inner_index)
        ccw_nbor, cw_nbor = get_neighbors(path[0], inner_hull, inner_index)
        if cw_nbor == path[1]:
            # The edge to CW neighbor is well placed
            # Let's try to place the CCW edge

            # Check for intersections first:
            i_inter_edge = get_closest_intersection_index(path[0], ccw_nbor, path)
            if i_inter_edge is not None:
                path = handle_start_intersection(i_inter_edge, path)
                continue

            
            #Otherwise, we try to improve the inner layer "normally" 
            ccw_nbor_path_index = path.index(ccw_nbor)
            ccw_nbor2, _ = get_neighbors(ccw_nbor, inner_hull, inner_index)

            if path[ccw_nbor_path_index-1] == ccw_nbor2:
                # the edge we would have to flip is already well placed
                # So we don't flip it.

                if path[-1] == ccw_nbor:
                    # If the end is on the outerlayer as well, that means that
                    # the extremities are neighbor to one another.
                    # so we find an edge that is miss placed and we rotate it.
                    #print("ccccccccccccc11111111")
                    for i in range(len(path)):
                        if path[i+1] not in inner_index:
                            path = perform_flip(i, ROTATION)
                            break
                    continue
                else:
                    # Otherwise, we will act differently depending on which type of edge is connected to the CCW neighbor
                    ccw_nbor_succ = path[ccw_nbor_path_index+1]
                    if ccw_nbor_succ in inner_index:
                        # if the bad edge is an inner diagonal,
                        # we will "rotate" the diagonal until we flip an interlayer edge to an inner edge
                        # this part takes O(n) flips before getting any improvement in the configuration
                        while path[0] not in outer_index:
                            path = perform_flip(ccw_nbor_path_index, PREFIX_REVERSAL)
                            path = perform_flip(ccw_nbor_path_index-1, PREFIX_REVERSAL)

                        continue
                    
                    elif get_closest_intersection_index(ccw_nbor, ccw_nbor_succ, inner_hull+[inner_hull[0]]) is not None:
                        # if the bad edge crosses the inner hull, that means it's an edge we really want to flip
                        # even if that displaces some well positionned edges (a bit like when we handle intersections).

                        # This case ressembles a lot the case where we have a big diagonal intersecting the edge we want to place
                        # But there are just some subtleties that add some cases compared to the other one.

                        p = path[0]
                        cw_nbor_p = cw_nbor
                        pe1, pe2 = points[ccw_nbor], points[ccw_nbor_succ]
                        i_inter_edge = ccw_nbor_path_index
                        
                        while not pl.segments_intersect(points[p], points[cw_nbor_p], pe1, pe2):
                            p = cw_nbor_p
                            ccw_nbor_p, cw_nbor_p = get_neighbors(p, inner_hull, inner_index)

                        # Now that p is identified, there are 2 cases:
                        # Either p_nbor is its predecessor and we can get rid (e1, e2) in 3 flips
                        # Or its not and we can get rid of that big diagonal (e1, e2) in 4 flips.
                        ip = path.index(p)
                        if path[ip-1] == ccw_nbor_p:
                            # Here is the subtlety: now p is not always in the triangle (start, e1, e2).
                            # So path[ip+1] is not forced to see path[ip-1] and thus we have to introduce another case.
                            if pl.ccw(points[ccw_nbor_p], points[p], points[path[ip+1]]):
                                # If those points are in CCW order, then we can do the usual case
                                path = perform_flip(ip-1, PREFIX_REVERSAL)
                                path = perform_flip(ip, PREFIX_REVERSAL)
                                path = perform_flip(i_inter_edge, PREFIX_REVERSAL)
                            else:
                                # We just have to find a point in the outer layer that can see both p and its CCW neighbor
                                i_out = ip+2
                                while not pl.ccw(points[ccw_nbor_p], points[p], points[path[i_out]]):
                                    i_out+=1
                                
                                # Now that we have found it, we can perform the following sequence of flips:
                                path = perform_flip(ip-1, PREFIX_REVERSAL)
                                path = perform_flip(i_out-1, PREFIX_REVERSAL)
                                path = perform_flip(i_out-2, PREFIX_REVERSAL)
                                path = perform_flip(i_inter_edge, PREFIX_REVERSAL)

                        else:
                            path = perform_flip(ip-1, PREFIX_REVERSAL)
                            path = perform_flip(path.index(ccw_nbor_p), PREFIX_REVERSAL) 
                            path = perform_flip(path.index(p), PREFIX_REVERSAL) 
                            path = perform_flip(i_inter_edge, PREFIX_REVERSAL)

                        continue
                    else:
                        # The bad edge is a an edge connecting the inner part to the outer part without crossing the inner hull
                        # First, let's check whether the path to the CCW neighbor stays in the inner hull. 
                        
                        if all([p in inner_index for p in path[:ccw_nbor_path_index]]):
                            # If thats the case, the start path is "looping"
                            # So we search for diagonals in the inner path so that we can move the end extremity next to the irregularities
                            diag_i = 0
                            cw_nbor_i = cw_nbor
                            while path[diag_i+1] == cw_nbor_i:
                                diag_i+=1
                                _, cw_nbor_i = get_neighbors(cw_nbor_i, inner_hull, inner_index)

                            path = perform_flip(diag_i, PREFIX_REVERSAL)
                            # This does not change the potential function but it will next iteration of the loop
                            continue

                        if pl.ccw(points[ccw_nbor], points[ccw_nbor_succ], points[path[ccw_nbor_path_index+2]]):
                            # The case where these points go CW is easier to handle 
                            # so we flip the inner neighbor edge to go to the CW case
                            path = perform_flip(ccw_nbor_path_index-1, PREFIX_REVERSAL)
                            continue

                        # In this case, the CCW neighbor of the start is connected the the vertex ccw_nbor_succ in the outer hull
                        # and ccw_nbor_succ's CCW neighbor must be connected to at least one vertex in the inner hull.
                        # That inner vertex it's connected to must belong to the same inner path as ccw_nbor 
                        # (otherwise, some parts of the outer hull would be innaccessible to the start).
                        
                        # We check whether the inner path to which the CCW belongs contains a diagonal or not
                        # Even stronger property: that path either goes only CCW via adjacent neighbors
                        # Or it can go CCW, then take a diagonal and then go CW via adjacent neighbors.

                        ip = ccw_nbor_path_index
                        ccw_nbor_p, _ = get_neighbors(ccw_nbor, inner_hull, inner_index)
                        while path[ip-1] == ccw_nbor_p:
                            ip-=1
                            ccw_nbor_p, _ = get_neighbors(path[ip], inner_hull, inner_index)

                        if path[ip-1] in outer_index:
                            # We are in the easy case where there is no diagonal
                            # In this case, we can transform both inter-layer edges into 
                            # an inner diagonal and a good outer edge
                            path = perform_flip(ip-1, PREFIX_REVERSAL)
                            path = perform_flip(ccw_nbor_path_index, PREFIX_REVERSAL)
                            continue

                        # Otherwise p=path[ip] is the first vertex where there is a diagonal.
                        outer_ccw_nbor, _ = get_neighbors(ccw_nbor_succ, outer_hull, outer_index)

                        if get_closest_intersection_index(outer_ccw_nbor, path[ip], inner_hull+[inner_hull[0]]) is not None:
                            # The CCW neighbor of ccw_nbor_succ cannot see p
                            # That means that ccw_nbor_succ can see it, so we perform this sequence of flip 
                            # getting rid of 1 diagonal
                            p = path[ip]
                            path = perform_flip(ccw_nbor_path_index-1, PREFIX_REVERSAL)
                            while path[0]!= p:
                                path = perform_flip(ccw_nbor_path_index, PREFIX_REVERSAL)
                                path = perform_flip(ccw_nbor_path_index-1, PREFIX_REVERSAL)
                            path = perform_flip(ccw_nbor_path_index, PREFIX_REVERSAL)
                            path = perform_flip(ccw_nbor_path_index-1, PREFIX_REVERSAL)

                            continue
                        else:
                            # Otherwise, we want to perform the same sequence until outer_ccw_nbor can see the starting point
                            path = perform_flip(ccw_nbor_path_index-1, PREFIX_REVERSAL)
                            while get_closest_intersection_index(outer_ccw_nbor, path[0], inner_hull+[inner_hull[0]]) is not None:
                                path = perform_flip(ccw_nbor_path_index, PREFIX_REVERSAL)
                                path = perform_flip(ccw_nbor_path_index-1, PREFIX_REVERSAL)

                            path = perform_flip(path.index(outer_ccw_nbor)-1, PREFIX_REVERSAL)
                            
                            continue # The improving flip will be done next loop (by flipping the diagonal adjacent to the new start)

            else:
                # Otherwise, the edge we want to flip is in a bad position.
                # So we can flip it and go the the next iteration 
                path = perform_flip(ccw_nbor_path_index-1, PREFIX_REVERSAL)
                #print("bbbbbbbbbbbbbb")
                continue
        
        elif ccw_nbor == path[1]:
            # The edge to CCW neighbor is well placed
            # Let's try to place the CW edge by doing the symmetric of the previous case

            # Check for intersections first:
            i_inter_edge = get_closest_intersection_index(path[0], cw_nbor, path)
            if i_inter_edge is not None:
                path = handle_start_intersection(i_inter_edge, path)
                continue

            cw_nbor_path_index = path.index(cw_nbor)
            _, cw_nbor2 = get_neighbors(cw_nbor, inner_hull, inner_index)

            if path[cw_nbor_path_index-1] == cw_nbor2:
                if path[-1] == cw_nbor:
                    # If the end is on the outerlayer as well, that means that
                    # the extremities are neighbor to one another.
                    # so we find an edge that is miss placed and we rotate it.
                    #print("ccccccccccccc11111111")
                    for i in range(len(path)):
                        if path[i+1] not in inner_hull:
                            path = perform_flip(i, ROTATION)
                            break
                    continue
                else:
                    # Otherwise, we will act differently depending on which type of edge is connected to the CW neighbor
                    print("THIS ONE")
                    cw_nbor_succ = path[cw_nbor_path_index+1]
                    if cw_nbor_succ in inner_index:
                        # if the bad edge is an inner diagonal,
                        # we will "rotate" the diagonal until we flip an interlayer edge to an inner edge
                        # this part takes O(n) flips before getting any improvement in the configuration
                        while path[0] not in outer_index:
                            path = perform_flip(cw_nbor_path_index, PREFIX_REVERSAL)
                            path = perform_flip(cw_nbor_path_index-1, PREFIX_REVERSAL)

                        continue
                    #######
                    elif get_closest_intersection_index(cw_nbor, cw_nbor_succ, inner_hull+[inner_hull[0]]) is not None:
                        p = path[0]
                        ccw_nbor_p = ccw_nbor
                        pe1, pe2 = points[cw_nbor], points[cw_nbor_succ]
                        i_inter_edge = ccw_nbor_path_index
                        
                        while not pl.segments_intersect(points[p], points[ccw_nbor_p], pe1, pe2):
                            p = ccw_nbor_p
                            ccw_nbor_p, cw_nbor_p = get_neighbors(p, inner_hull, inner_index)

                        # Now that p is identified, there are 2 cases:
                        # Either p_nbor is its predecessor and we can get rid (e1, e2) in 3 flips
                        # Or its not and we can get rid of that big diagonal (e1, e2) in 4 flips.
                        ip = path.index(p)
                        if path[ip-1] == cw_nbor_p:
                            # Here is the subtlety: now p is not always in the triangle (start, e1, e2).
                            # So path[ip+1] is not forced to see path[ip-1] and thus we have to introduce another case.
                            if not pl.ccw(points[cw_nbor_p], points[p], points[path[ip+1]]):
                                # If those points are in CW order, then we can do the usual case
                                path = perform_flip(ip-1, PREFIX_REVERSAL)
                                path = perform_flip(ip, PREFIX_REVERSAL)
                                path = perform_flip(i_inter_edge, PREFIX_REVERSAL)
                            else:
                                # We just have to find a point in the outer layer that can see both p and its CW neighbor
                                i_out = ip+2
                                while pl.ccw(points[cw_nbor_p], points[p], points[path[i_out]]):
                                    i_out+=1
                                
                                # Now that we have found it, we can perform the following sequence of flips:
                                path = perform_flip(ip-1, PREFIX_REVERSAL)
                                path = perform_flip(i_out-1, PREFIX_REVERSAL)
                                path = perform_flip(i_out-2, PREFIX_REVERSAL)
                                path = perform_flip(i_inter_edge, PREFIX_REVERSAL)

                        else:
                            path = perform_flip(ip-1, PREFIX_REVERSAL)
                            path = perform_flip(path.index(cw_nbor_p), PREFIX_REVERSAL) 
                            path = perform_flip(path.index(p), PREFIX_REVERSAL) 
                            path = perform_flip(i_inter_edge, PREFIX_REVERSAL)

                        continue
                    else:
                        # The bad edge is a an edge connecting the inner part to the outer part without crossing the inner hull
                        # First, let's check whether the path to the CW neighbor stays in the inner hull. 
                        print("THISSSSSSS ONE")
                        if all([p in inner_index for p in path[:cw_nbor_path_index]]):
                            # If thats the case, the start path is "looping"
                            # So we search for diagonals in the inner path so that we can move the end extremity next to the irregularities
                            diag_i = 0
                            ccw_nbor_i = ccw_nbor
                            while path[diag_i+1] == cw_nbor_i:
                                diag_i+=1
                                ccw_nbor_i, _ = get_neighbors(ccw_nbor_i, inner_hull, inner_index)

                            path = perform_flip(diag_i, PREFIX_REVERSAL)
                            # This does not change the potential function but it will next iteration of the loop
                            continue

                        if not pl.ccw(points[cw_nbor], points[cw_nbor_succ], points[path[cw_nbor_path_index+2]]):
                            # The case where these points go CW is easier to handle 
                            # so we flip the inner neighbor edge to go to the CW case
                            path = perform_flip(cw_nbor_path_index-1, PREFIX_REVERSAL)
                            continue

                        # In this case, the CCW neighbor of the start is connected the the vertex ccw_nbor_succ in the outer hull
                        # and ccw_nbor_succ's CCW neighbor must be connected to at least one vertex in the inner hull.
                        # That inner vertex it's connected to must belong to the same inner path as ccw_nbor 
                        # (otherwise, some parts of the outer hull would be innaccessible to the start).
                        
                        # We check whether the inner path to which the CCW belongs contains a diagonal or not
                        # Even stronger property: that path either goes only CCW via adjacent neighbors
                        # Or it can go CCW, then take a diagonal and then go CW via adjacent neighbors.

                        ip = cw_nbor_path_index
                        _, cw_nbor_p = get_neighbors(cw_nbor, inner_hull, inner_index)
                        while path[ip-1] == cw_nbor_p:
                            ip-=1
                            _, cw_nbor_p = get_neighbors(path[ip], inner_hull, inner_index)

                        if path[ip-1] in outer_index:
                            # We are in the easy case where there is no diagonal
                            # In this case, we can transform both inter-layer edges into 
                            # an inner diagonal and a good outer edge
                            path = perform_flip(ip-1, PREFIX_REVERSAL)
                            path = perform_flip(cw_nbor_path_index, PREFIX_REVERSAL)
                            continue

                        # Otherwise p=path[ip] is the first vertex where there is a diagonal.
                        _, outer_cw_nbor, = get_neighbors(cw_nbor_succ, outer_hull, outer_index)

                        if get_closest_intersection_index(outer_cw_nbor, path[ip], inner_hull+[inner_hull[0]]) is not None:
                            # The CCW neighbor of ccw_nbor_succ cannot see p
                            # That means that ccw_nbor_succ can see it, so we perform this sequence of flip 
                            # getting rid of 1 diagonal
                            print("BBBBBBB one")
                            p = path[ip]
                            print(path)
                            print("P is", p)
                            path = perform_flip(cw_nbor_path_index-1, PREFIX_REVERSAL)
                            while path[0]!= p:
                                print(path)
                                path = perform_flip(cw_nbor_path_index, PREFIX_REVERSAL)
                                path = perform_flip(cw_nbor_path_index-1, PREFIX_REVERSAL)
                            print(path)
                            path = perform_flip(cw_nbor_path_index, PREFIX_REVERSAL)
                            path = perform_flip(cw_nbor_path_index-1, PREFIX_REVERSAL)

                            continue
                        else:
                            print("AAAAAAAAAAA ONE")
                            # Otherwise, we want to perform the same sequence until outer_ccw_nbor can see the starting point
                            path = perform_flip(cw_nbor_path_index-1, PREFIX_REVERSAL)
                            while get_closest_intersection_index(outer_cw_nbor, path[0], inner_hull+[inner_hull[0]]) is not None:
                                path = perform_flip(cw_nbor_path_index, PREFIX_REVERSAL)
                                path = perform_flip(cw_nbor_path_index-1, PREFIX_REVERSAL)

                            path = perform_flip(path.index(outer_cw_nbor)-1, PREFIX_REVERSAL)
                            
                            continue # The improving flip will be done next loop (by flipping the diagonal adjacent to the new start)

            else:
                path = perform_flip(cw_nbor_path_index-1, PREFIX_REVERSAL)
                #print("dddddddddddddd")
                continue

        else:
            # The first edge is badly placed. 
            # Try to see if it's possible to place an edge to its neighbor

            # Try the CCW one
            # Check for intersections first:
            i_inter_edge = get_closest_intersection_index(path[0], ccw_nbor, path)
            if i_inter_edge is not None:
                path = handle_start_intersection(i_inter_edge, path)
                continue

            ccw_nbor_path_index = path.index(ccw_nbor)
            ccw_nbor2, _ = get_neighbors(ccw_nbor, inner_hull, inner_index)

            if path[ccw_nbor_path_index-1] != ccw_nbor2:
                path = perform_flip(ccw_nbor_path_index-1, PREFIX_REVERSAL)
                continue

            # the edge we would like to flip is already well placed
            # So try to go with the other one instead.

            # Check for intersections first:
            i_inter_edge = get_closest_intersection_index(path[0], cw_nbor, path)
            if i_inter_edge is not None:
                path = handle_start_intersection(i_inter_edge, path)
                continue

            cw_nbor_path_index = path.index(cw_nbor)
            _, cw_nbor2 = get_neighbors(cw_nbor, inner_hull, inner_index)
            if path[cw_nbor_path_index-1] != cw_nbor2:
                path = perform_flip(cw_nbor_path_index-1, PREFIX_REVERSAL)
                continue
                #print("eeeeeeeee111111111")
            
            # At this point, both edges are well placed.

            # We just check if one of those is an extremity:
            if path[-1] in (ccw_nbor, cw_nbor):
                # It is the case so we do a rotation flip
                for i in range(len(path)):
                    if path[i+1] not in inner_index:
                        path = perform_flip(i, ROTATION)
                        break
                continue

            # Otherwise, we could do something similar to the other cases
            # but more lazyly, we can just say to connect the start to the CCW neighbor 
            path = perform_flip(ccw_nbor_path_index-1, PREFIX_REVERSAL)
            # The idea is that either you will go to another case which will improve the potential
            # Or you will come back to this case and the CCW distance to the endpoint will be reducing

            continue
    
    return flip_sequence #Overall complexity of O(n_0 + n_1^2) (where n_0 = |outer_layer| and n_1 = |inner_layer|)

            
                

            

        


