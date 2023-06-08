"""Several utility functions for vectors."""

from math import sqrt

def sub(v1,v2): 
    """Difference of two vectors.
    @param v1: first vector
    @param v2: second vector
    @return: v1 - v2
    """
    return [a-b for a,b in zip(v1,v2)]

def add(v1,v2): 
    """Sum of two vectors.
    @param v1: first vector
    @param v2: second vector
    @return: v1 - v2
    """
    return [a+b for a,b in zip(v1,v2)]
    
def dot(v1,v2):
    """Dot product between two vectors.
    @param v1: first vector
    @param v2: second vector
    @return: v1 . v2
    """    
    return sum([a*b for a,b in zip(v1,v2)])
    
def cross(v1,v2):
    """Cross product between two vectors (must be 3D)
    @param v1: first vector
    @param v2: second vector
    @return: v1 * v2
    """
    return [v1[1] * v2[2] - v2[1] * v1[2],
            v1[2] * v2[0] - v2[2] * v1[0],
            v1[0] * v2[1] - v2[0] * v1[1]]
            
def scale(v,s):
    """Scales a vector by a constant.
    @param v: vector to be scaled
    @param s: scale factor
    @return: s v
    """
    return [s*x for x in v]
    
def squarelength(v):
    """Square of the length of a vector.
    @param v: input vector
    @return: |v|**2
    """
    return sum([x*x for x in v])
    
def combine(p0,p1,ratio):
    """Performs a linear combination between points.
    @param p0: first point.
    @param p1: second point.
    @return: p0 * ratio + p1 * (1-ratio)
    """
    return add(scale(p0,ratio),scale(p1,1.0-ratio))

def length(v):
    """Length of a vector.
    @param v: input vector.
    @return: |v|.
    """
    return sqrt(squarelength(v))

def normalize(v):
    """Vector of size 1.
    @param v: input vector.
    @return: v/|v|.
    """
    return scale(v,1.0/length(v))

def squaredistance(a,b):
    """Squared Euclidean distance between two points.
    @param a: input point
    @param b: input point
    @return: | a - b |^2
    """
    return squarelength(sub(a,b))
    
def distance(a,b):
    """Euclidean distance between two points.
    @param a: input point
    @param b: input point
    @return: | a - b |
    """
    return sqrt(squaredistance(a,b))
    
