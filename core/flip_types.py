"""
Define constants for the 4 possible types of flips
"""

#(i, i+1): [0, ..., i, i+1, ..., n] -> [0, ..., i, i+1, ..., n] (no transformation)
FLIP_SAME = 0

#(0, i+1): [0, ..., i, i+1, ..., n] -> [i, ..., 0, i+1, ..., n]
FLIP_PREFIX_REVERSE = 1

#(0, n): [0, ..., i, i+1, ..., n] -> [i+1, ..., n, 0, ..., i]
FLIP_ROTATE = 2

#(i, n): [0, ..., i, i+1, ..., n] -> [0, ..., i, n, ..., i+1]
FLIP_SUFFIX_REVERSE = 3
