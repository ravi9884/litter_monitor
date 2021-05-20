import numpy as np
from typing import Tuple, List
import datetime
import shutil
import matplotlib.pyplot as plt
from litter_monitor.util import image as i


def mdisp(image, title):
    if i.is_interactive():
        plt.imshow(image, cmap="gray")
        plt.suptitle(title)
        plt.show()

def almost_same(x: Tuple[int, int, int, int],existing_objects: List[Tuple[int, int, int, int]]) -> bool:
    """given a tuple and a list of tuple 

    Args:
        x (Tuple[int, int, int, int]): [description]
        existing_objects (List[Tuple[int, int, int, int]]): [description]

    Returns:
        bool: [description]
    """    
    for ls in existing_objects:
        if len([ a for a,b in zip(list(x),list(ls)) if np.abs(a-b) < 10]) == 4:
            return True
    return False

def same(x,y):
    if len([ a for a,b in zip(list(x),list(y)) if np.abs(a-b) < 10]) == 4:
        return True
    else:
        return False

def key_diff(x,y):
    return np.sum([np.abs(a-b) for a,b in zip(list(x),list(y))])

def closest_key(x, dct):
    lowest = (-1, None)
    s = sorted([ (y,key_diff(x,y)) for y in list(dct)], key=lambda x: x[1])
    return s[0][0]

def is_interactive():
    import __main__ as main
    return not hasattr(main, '__file__')