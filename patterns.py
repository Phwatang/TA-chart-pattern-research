# Collection of pattern sequences to search for
# All sequence values generated focus around the value 1

from array import array
import numpy as np

def triangle(opening: float = 0.04, collapse_grad: float = 0.004, 
    direc_grad: float = 0, bull_var: bool = True) -> np.ndarray:
    """Returns a Numpy array containing triangle wave pattern.
    
    ---
    Parameters:
    opening: The opening \"height\" of the triangle
    collapse_grad: The gradient at which the top and bottom of the 
        collapse inwards
    direc_grad: The gradient at which the overall triangle progresses
    bull_var: if True, the bullish variant will be returned. If False,
        the bearish variant will be returned."""
    
    pattern = []
    # Choose if starting at top/bottom of triangle
    if bull_var:
        do_top = True
    else:
        do_top = False

    for n in range(5):
        if do_top:
            pattern.append(1 + opening + n*(direc_grad-collapse_grad))
        else:
            pattern.append(1 + n*(direc_grad+collapse_grad))
        # Swap to other side of triangle
        do_top = not do_top
    return np.array(pattern)

def rectangle(opening: float = 0.04, bull_var: bool = True) -> np.ndarray:
    """Returns a numpy array containing a rectangle pattern"""

    pattern = []
    # Choose if starting at top/bottom of rectangle
    if bull_var:
        do_top = True
    else:
        do_top = False
    
    for n in range(5):
        if do_top:
            pattern.append(1+opening)
        else:
            pattern.append(1)
        # Swap to other side of rectangle
        do_top = not do_top
    return np.array(pattern)

SYM_TRIANGLE_BULL = triangle(opening=0.04, collapse_grad=0.004, bull_var=True)
SYM_TRIANGLE_BEAR = triangle(opening=0.04, collapse_grad=0.004, bull_var=False)
ASC_TRIANGLE = triangle(opening=0.04, collapse_grad=0.004, direc_grad=0.004, bull_var=True)
DES_TRIANGLE = triangle(opening=0.04, collapse_grad=0.004, direc_grad=-0.004, bull_var=False)
FALL_WEDGE = triangle(opening=0.03, collapse_grad=0.003, direc_grad=-0.008, bull_var=True)
RISE_WEDGE = triangle(opening=0.03, collapse_grad=0.003, direc_grad=0.008, bull_var=False)
RECTANGLE_BULL = rectangle(opening=0.03, bull_var=True)
RECTANGLE_BEAR = rectangle(opening=0.03, bull_var=False)

SHORT_SCALES = [2,4,6,8,10]
LONG_SCALES = [20,30,40,50,60]